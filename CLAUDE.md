# substrate — working instructions

## Heavy Agda compiles: ALWAYS via `scripts/membudget` (never bare `agda` for hogs)

A heavy `agda` compile can consume many GB; run concurrently with others (or with
the IDE's background typecheck) it can OOM the whole machine — this happened
2026-06-19 (a 5.6 GB monolithic KAT `refl` stacked with other compiles took the box).
To make that impossible by construction:

    scripts/membudget init 8192                                  # once per boot: global RAM budget (MB)
    scripts/membudget run <MB> <label> -- agda --safe -i. <Module>.agda
    scripts/membudget status                                     # TOTAL / leased / free + active leases

`run` does two things:
1. **cgroup cap (per tree):** launches the compile in a `systemd-run --user --scope`
   with `MemoryMax=<MB>` + `MemorySwapMax=0` — the kernel kills only that scope
   (exit 137) if it exceeds; the machine stays up.
2. **budget semaphore (sum of trees):** leases `<MB>` from a shared cotype ledger. If the
   budget can't cover it the call **BLOCKS** (WaitForSingleObject-style: sleeps, wakes on a
   release, re-attempts, proceeds when it fits) rather than failing — so a forgotten second
   concurrent launch waits its turn instead of OOM'ing or erroring. It REFUSES (exit 3) only
   the *impossible* (request > the level's TOTAL budget — would block forever). Escapes:
   `MEMBUDGET_NOBLOCK=1` fails fast; `MEMBUDGET_TIMEOUT=<s>` gives up after s. Leases release
   on exit and auto-GC if an owner dies.

Use it for any module expected to take **> ~1 GB or > ~60 s** (round / encrypt KATs,
256-byte exhaustive reflections, a by-hand full build). Trivial one-off checks may
call `agda` directly. Also: `pkill -f agda` before a heavy launch; never stack work
on a measured multi-GB process.

**Recursion-safe:** a job launched under `membudget` may itself call `membudget`
(e.g. a build script that wraps each module). A nested call SUBALLOCATES from its
parent's reservation (not the global pool the ancestor already holds) and runs
in-scope — so it never deadlocks on the global budget and never double-counts. It is
refused only if the *parent's* reservation can't cover it (size the top-level budget
for the whole subtree).

**Automatic (no explicit prefix):** `source scripts/membudget-shrc` puts a PATH shim ahead
of the real `agda`, so bare `agda` (interactive AND inside `make` recipes) auto-routes through
`membudget run` (lease `AGDA_MB`, default `auto`; `AGDA_MB=384 agda …` to pin the ceiling for a one-off). The ledger is a shared file, so this budgets agda across separate
shells too (concurrent background compiles can't OOM the box — a second is refused).
For a whole contained session, `scripts/membudget shell [MB]` opens a shell inside one
top-level scope (the cgroup auto-contains the entire process hierarchy) with the rc
loaded. To make it permanent for every shell:
`echo 'source ~/github/substrate/scripts/membudget-shrc' >> ~/.bashrc`.

Rationale + history: memory `feedback_budget_concurrent_compiles`. The pre-commit
full build already caps each module at `+RTS -M256m` (⟡cap-384; was 1024m); `membudget`
is the same discipline for the ad-hoc compiles I run by hand.

## Building the tree: `make -j` self-throttles by RAM

The build is recursive make (`agda/Makefile` → per-dir, `AGDA ?= agda`, one process per file).
With the shim active, **`make -j` with NO number is the right invocation** — it spawns the
whole dependency frontier and each `agda` blocks on the budget semaphore, so effective
parallelism self-tunes to memory availability, in dependency order (no `-jN` guess, no OOM):

    cd agda
    make -j                                   # that's it — the generated makefiles self-inject the shim
                                              # onto PATH (+ membudget auto-inits its budget on first use)

The makefiles (`scripts/gen_build_makefiles.py`) now put the agda-shim on `make`'s PATH by construction
(idempotent `export PATH`, exported to recipes + sub-makes), so **`make` IS the controlled+instrumented
build path — no manual `source membudget-shrc`, no `membudget init`** (it auto-inits to 70%-RAM/8GiB). The
shim calls `membudget` by absolute path, so it's self-contained. `make -j` self-throttles by RAM and ALSO
records a proof-cost profile per re-typechecked module (Ⓟ.proof-cost-ledger, always-on opt-out;
`MEMBUDGET_NOPROFILE=1 make` to skip the ~2× profiling cost; `make AGDA=/path/to/agda` to pin a different
agda). Sourcing `membudget-shrc` is still useful for *interactive* bare `agda`; it is no longer needed for
`make`. NOTE: the pre-commit gate (`full_build_check.py`) invokes agda directly (not via make), so it is
NOT shim-routed — to grow the ledger, build via `make`.

`make`'s recipes resolve `agda` via PATH → the shim → `membudget run` → blocks/leases. The
per-file `+RTS -M256m` heap cap keeps each job under the 384MiB lease ceiling. `AGDA_MB=auto`
(the shim default) right-sizes each lease from peak-mem history (192MB cold); pin `AGDA_MB=<N>` only
to override. (Demonstrated: `make -j` over a 2-subdir node under a 1-job budget
serialized cleanly via BLOCKED/lease hand-off; exit 0.)

## Build-time estimation (genlop-style): `scripts/buildtime.py`

Per-module typecheck times are recorded PARALLEL TO THE RECURSIVE-MAKE STRUCTURE: each source dir
gets a `.agda-times.tsv` alongside its `Makefile` (gitignored — timing is hardware/cache-specific).
The **`membudget` wrapper is the universal capture point**: the agda shim routes every compile
through `membudget run`, which times ONLY the post-lease run (not the semaphore wait) and appends
`module<TAB>seconds` to the module's per-dir ledger (best-effort; never alters the compile's exit
code). `full_build_check.py` also records its run and prints a genlop-style up-front estimate + live
ETA. Read it back:

    scripts/buildtime.py --predict          # genlop -p: estimated full build (Σ medians; wall ≈ /J)
    scripts/buildtime.py --top [N]          # the slowest modules (build hot-spots)
    scripts/buildtime.py --module <relpath> # one module's history    --stats / --compact

Estimate = MEDIAN of a module's last K=5 runs (robust to the cold/warm-`.agdai` bimodality); unseen
modules fall back to the global median. Only SUCCESSFUL compiles are recorded (a failed/OOM-killed run
is not representative).

**Autobudget (`AGDA_MB=auto`, the shim default).** `membudget` also captures each compile's peak-mem
(`/usr/bin/time -v` maxRSS → the `peak_mb` 3rd ledger column) and, when the lease is `auto`, SIZES it by
rounding `max(peak)` **UP to the next power of two** (floor 64, cap `AGDA_MB_MAX=384` = 384MiB ceiling),
fallback `AGDA_MB_DEFAULT=192` with no history. The pow2 step IS the safety margin — it sits `2ⁿ ± 2ⁿ⁻¹`
around the need (a `2ⁿ⁻¹` headroom band), so no extra fudge and no over-rounding (peak 900 → 1024, not
512; peak 65 → 128). The **384MiB ceiling** (⟡cap-384) is justified by the full-build invariant: every
module typechecks under `+RTS -M256m` (256 MB heap) and passes, so worst-case maxRSS ≈ 256 MB heap +
~0.1 GB RTS ≈ 356 MB < 384. The strict `-M256m` gate is a FORCING FUNCTION: a module that would exceed it
must SEAL its heavy neutrals `opaque` (a heavy type-level redex like `normalize R.detJac` or `iterate n σ`
becomes a non-reducing handle — the cross-module elaboration memo) or import a CHEAPER proof, not grow the
cap. A peak that would round to 512 is clamped to 384 (still ≥ the real peak). The **192 MB default** covers a typical cold module (measured maxRSS tops ~120 MB) at high
concurrency, and the retry ladder `192→384` lands on the ceiling so a heavy unseen module still self-heals. maxRSS over-counts the OOM-relevant (anonymous) footprint, so this is
conservatively safe; a lease is a hard kill cap, so rounding UP keeps cap ≥ peak. Light modules lease small → far more
`make -j` modules fit the global budget concurrently.

**Retry-on-OOM (self-correcting).** A too-tight first guess is absorbed: a cgroup `MemoryMax` kill exits
137, and because an agda compile is idempotent (the shim sets `MEMBUDGET_RETRY_OOM=1`), membudget
releases the lease and re-enters at the next power-of-2 bucket, doubling until it fits or hits the cap
(then it gives up with 137 — no infinite loop). The successful run records the real peak, so the history
converges. Only TOP leases retry (only they have a hard cgroup cap; a SUB's mb is a budget reservation).
`AGDA_MB=<N>` pins a fixed lease; `scripts/buildtime.py --mem` shows the per-module peaks → bucketed
leases.

## Commit policy

Work and commit directly on `main`; the pre-commit hook (CI gates) is the promotion
gate. After `git commit`, the `post-commit` hook AMENDS the commit (advisory) —
**wait for the marker `post-commit advisory (auto-captured)` in HEAD before pushing**,
then `git fetch` + fast-forward. See memory `feedback_commit_on_main_ci_gated` and
`feedback_wait_for_postcommit_amend_before_push`.

## Reuse-search BEFORE building new machinery (the trigger fires on the PLAN)

When a plan proposes building a NEW def / lemma / module / bridge, that proposal **is the trigger**:
first search for the structure it would reinvent. The substrate is dense — most "build X" is really
"instantiate the X that already exists." Repeatedly (one arc ran 5 near-reinventions, each caught only by
a user pointer or late grounding): hand-built recip-homomorphism lemmas before the Ⓖ★ **cross-mixer**
dual; bespoke factorisation before the div-mod **wedge** (`a = recon q b r`); a Bézout reproof before
`Algebra.Z.Euclid.euclid` (the EEA trace already held Bézout); a Monoid→Category bridge before
`Category.Delooping.deloop`; a round-trip Canonical before `Algebra.Quotient.split-Canonical`.

The search is **structural, not grep** (grep misses inline lambdas / differently-named helpers):

    python jea/metalanguage/jea_pysim.py <files-or-.agdai globs> --clusters --extract --skeleton

over `.py` AND Agda `.agdai` core (point at `agda/_build/.../Substrate/...`). It reads the interned SPPF
(shared canonical nodes = corroborated shape).

**FASTEST first check before a new `data`/`record`: grep `catalog/reuse-index.md`** for the concept name
(`V4`, `Real`, `Wedge`, `Monoid`, `Stream`, `DivStr`, …). It is the mechanically-generated (from the
typechecked `.agdai` cores — `scripts/gen_reuse_index.py`) name→canonical-home index of every structure in
the tree, with a *Multiply-homed* section to pick the right one when a name has several homes. Regenerate it
(~2min) after adding structures. Then, for deeper cases, scan `Substrate.Generators` / the `*.Registry`
bridge-indexes and the apex memories (`project_split_idempotent_apex`, `project_witness_tower_*`) for the
generator the plan should instantiate. Rule of thumb: before writing a `record`/new operator/new bridge,
name the existing generator it specialises — or confirm (briefly) there isn't one. This is the standing
prevention layer (Ε / G9); memory `similarity-not-grep` + the `construct-dont-classify` skill's
"reinvent-vs-reuse" reflex are the recalled forms, this is the always-loaded one.

**The trigger also fires on CONCLUSIONS and STRUCTURAL QUESTIONS, not just build-plans.**
Before writing that something is *gated / deferred / awkward / impossible / new reach*, or
answering *what is this / how does it relate* — run the same structural search FIRST. A
deferral/TODO comment is a **hypothesis to verify** (find the actual provider), not a fact; it
may be stale or point at a different deferral sharing a tag. The substrate almost always already
**names its centers** (`FreeUP`, the Registry monoidal groupoid, the terminal coalgebra, the EEA
fold-table) — reasoning to a correct-but-unnamed answer is the recurring miss. Search the
**witness tower** specifically for any spectral / multiplicity / cycle / conjugacy / combinatorial
claim (the silo most often skipped). Memory `feedback_reuse_search_before_feasibility_conclusions`
is the recalled form; this is the always-loaded one.

**Opacity / OOM at a concrete instance → the FreeUP β-interface is the route-around.** When a concrete
cyclic/linear instantiation OOMs (dense materialization — the Cycle7 pattern) or an `opaque` def won't
reduce, don't grind the dense form or reinvent a seal: prove via the universal-property β-interface —
the exposed basis-action lemma (`extend-on-basis`, e.g. `cyclic-Linear-basis`) + prove-on-generators-
then-lift (`HasOrder-from-perm` / `extend-unique` / `package-comm`). The operator is determined by its
basis-action up to unique iso, so the dense form is never needed; the `opaque` seal exists to *channel*
you into this interface (it is BOTH the obstruction and the enforcement). Applies to any free-extension
(linear maps, permutations, GF(2ⁿ)/bilinear — the AES linear layer included); NOT to point-evaluations
(a concrete KAT) or exhaustive tables (the S-box), where reflection + `membudget` decomposition remain
the tools. Memory `feedback_opacity_blowup_routearound_freeup`.

**The absence-words ARE the trigger.** Before asserting in prose that something is *no / none / can't /
impossible / irreducible / doesn't-need / the-only* — about the substrate or a construction — run the
structural search FIRST. These absence-claims (not just build-plans) are the recurring miss; the word is
the signal to verify, not assert. (Repeatedly caught only by the user: "AES exhaustion is irreducible"
[false — affine is linear], "opacity isn't an obstruction" [it is, and the interface], "permutations have
no CF trace" [gcd IS the Euclidean algorithm], "templatize fuel-bezout" [already generic over deg/modulus].)
