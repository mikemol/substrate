# substrate — working instructions

## THE STANDING RULE: fix the tooling so it answers your question

**If you have a question the tooling doesn't answer directly, fix the tooling so it
answers your question.** No complex command lines, no greps, no seds, no judgements
not in code. You want to know something about something? Use the tool that enables
STRUCTURAL instead of TEXTUAL queries. **Don't have the tool yet? Extending your
tools is fixing your tools; fixing your tools is extending your tools.**

`.claude/skills/struct-tools/SKILL.md` is the entrypoint — it carries the
`artifact → tool` table, and running a tool bare lists its modes.

Two failure shapes this exists to stop, both measured repeatedly:

- **Reasoning not codified.** Needing more than ONE tooling command, or manipulating
  a tool's output (`| tail`, a `python3 -c` wrapper, a shell `case` over an error
  string), means the judgement is happening in the turn instead of in a program. It
  evaporates when the turn ends and the next reader re-derives it — differently.
- **Reading a toolkit gap as a category.** "No tool covers this, so grep is
  legitimate here" is the same error as reading *no consumer found* as *no consumer
  exists*: a fact about the METHOD reported as a fact about the SUBSTRATE. A build
  log is `Checking <mod>`, an error kind, a make target; `pgrep` is pid/command/state.
  Both are structured; neither had a reader yet. **An exception admitted for the
  uncovered case is the loophole that swallows the rule** — so there are no
  exceptions, only tools that do not exist yet.

⚑ **A missing mode is WORK, not a finding.** The honest response to "the tool can't
answer that" is to add the mode, not to route around it.

⚑ **This rule has a hook, and the hook is why it is here twice.** `scripts/
hook_structural_query.py` (PreToolUse/Bash) names the owning tool when a textual
query hits a structured artifact — advisory by default, `STRUCT_HOOK_BLOCK=1` to
refuse. The instruction states the policy; the hook is the layer that can refuse a
violation. **A policy that lives only in a document governs the turns where it is
already being thought about** — this one was violated twice in a single turn after
being acknowledged in that same turn.

## Heavy Agda compiles: ALWAYS via `scripts/membudget` (never bare `agda` for hogs)

A heavy `agda` compile can consume many GB; run concurrently with others (or with
the IDE's background typecheck) it can OOM the whole machine — this happened
2026-06-19 (a 5.6 GB monolithic KAT `refl` stacked with other compiles took the box).
To make that impossible by construction:

    scripts/membudget init 8192                                  # create the ledger if absent (optional: run/status auto-create it)
    scripts/membudget init --reset 8192                          # RESIZE the global budget in place, keeping live leases
    scripts/membudget run <MB> <label> -- agda --safe -i. <Module>.agda
    scripts/membudget status                                     # TOTAL / leased / free + active leases

⚑ **`init` NEVER OVERWRITES** (2026-09-22, agreed with mtools' `fence.admit`). It used to `rm -f` the
ledger and recreate it, which wiped a LIVE lease (the job kept running uncounted, over-subscribing
the pool) and briefly left no total, so a concurrent client refused. Now a plain `init` on an existing
ledger changes nothing and says so; `init --reset N` is the resize. A ledger with two `TOTAL_MB` lines
is REFUSED (exit 4) rather than read by line order.

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
(e.g. a build script that wraps each module). A nested call draws from the GLOBAL pool and
gets its OWN scope: leases are disjoint, and parentage governs cascade-GC only (see the header of
the membudget client and mtools' `admit.py`; measured against this tree 2026-10-10, W327 — this
paragraph used to say the opposite, that a nested call suballocates from its parent's
reservation, and the code wins). So size the global budget for the whole subtree.

**Automatic (no explicit prefix):** `source scripts/membudget-shrc` puts a PATH shim ahead
of the real `agda`, so bare `agda` (interactive AND inside `make` recipes) auto-routes through
`membudget run` (lease `AGDA_MB`, default `auto`; `AGDA_MB=384 agda …` to pin the ceiling for a one-off). The ledger is a shared file, so this budgets agda across separate
shells too (concurrent background compiles can't OOM the box — a second is refused).
For a whole contained session, `scripts/membudget shell [MB]` opens a shell inside one
top-level scope (the cgroup auto-contains the entire process hierarchy) with the rc
loaded. To make it permanent for every shell:
`echo 'source ~/github/substrate/scripts/membudget-shrc' >> ~/.bashrc`.

Rationale + history: memory `feedback_budget_concurrent_compiles`. The pre-commit
full build already caps each module's GHC heap at `+RTS -M$(MEM_CAP)` (the value lives in
`scripts/gen_build_makefiles.py` — do not restate it here); `membudget` is the same discipline
for the ad-hoc compiles I run by hand.

⚑ **THE BASH CLIENT IS BEING RETIRED (operator ruling 2026-10-02, W79) in favour of mtools'
`mikemol-membudget` (fence), which shares the same ledger file and caps memory in a cgroup-v2
sibling (measured on this host, W324 and W326).** So cite the path through its ONE authority,
`substrate/build_settings.py` `MEMBUDGET` (the generated makefiles, the agda shim via the exported
`MEMBUDGET`, `gen_selftest_mk`, `install_freshness` and `gate_status` already read it), never the
literal `scripts/membudget`. The swap is waiting on `build_census` reading the python client's
`describe` rows (W331), which waits on the fleet pin reaching mtools 7ff52eb.

## Building the tree: `make -j` self-throttles by RAM

The build is ONE FLAT IMPORT-DAG makefile (`agda/Flat.mk`, generated) plus a thin root
`agda/Makefile` — **not** recursive per-directory make. Those 280 per-dir makefiles were deleted:
directory order encoded only 0.4% of the real import edges, so a cold `make -j` built imports
in-process and OOM-stormed. Each target is the real `_build/<ver>/agda/<Mod>.agdai`, depending on
its own `.agda` AND every direct import's `.agdai` (source-parsed from `open import`), so make's
mtime model is sound and a warm build is a near-instant mtime check. `make all` also INGESTS each
core into the SPPF store — a module is done when interned, not when its `.agdai` exists.

⚑ **⟡agda-jobs — the `-j` width has ONE authority: `gen_build_makefiles.AGDA_JOBS`** (env
`AGDA_JOBS` overrides; read it with `scripts/gen_build_makefiles.py --jobs`). Never type a
number at a call site — six sites once spelled this by hand, which is how conventions drift.

**It replaced a bare `-j`, and THAT RATIONALE WAS SOUND ABOUT MEMORY, so it is kept:** with the
shim active, an unlimited frontier lets each `agda` block on the budget semaphore, so
parallelism self-tunes to RAM in dependency order — no `-jN` guess, no OOM. **What the
semaphore does not bound is PROCESS COUNT:** unlimited `-j` over a ~3.5k-module DAG forks a
shell per ready target — thousands on a wide frontier — which then sleep in the acquire loop.
Cheap each, not free in PIDs. So the cap bounds the QUEUE, not the throttle: the RAM semaphore
still governs, and at the default 8 GiB budget it admits ~21–42 concurrent compiles depending
on lease size (192/256/384 MB), so the width sits at or below what RAM already permits.

    cd agda
    make -j "$(../scripts/gen_build_makefiles.py --jobs)"   # the generated makefiles self-inject the
                                                           # shim onto PATH (+ membudget auto-inits)
    make -j                                   # still SAFE — the semaphore governs either way;
                                              # you lose only the fork bound

The makefiles (`scripts/gen_build_makefiles.py`) now put the agda-shim on `make`'s PATH by construction
(idempotent `export PATH`, exported to recipes + sub-makes), so **`make` IS the controlled+instrumented
build path — no manual `source membudget-shrc`, no `membudget init`** (it auto-inits to 70%-RAM/8GiB). The
shim calls `membudget` by absolute path, so it's self-contained. `make -j` self-throttles by RAM and ALSO
records a proof-cost profile per re-typechecked module (Ⓟ.proof-cost-ledger, always-on opt-out;
`MEMBUDGET_NOPROFILE=1 make` to skip the ~2× profiling cost; `make AGDA=/path/to/agda` to pin a different
agda). Sourcing `membudget-shrc` is still useful for *interactive* bare `agda`; it is no longer needed for
`make`. NOTE: the pre-commit full-build gate now runs **`make -C agda -j`** (⟡cap-384) — the SINGLE build path,
shim-routed through `membudget` (which owns retry-on-OOM), so building via the gate grows the ledger too.

`make`'s recipes resolve `agda` via PATH → the shim → `membudget run` → blocks/leases. The
per-file `+RTS -M$(MEM_CAP)` heap cap keeps each job under its lease. `AGDA_MB=auto` (the shim
default) right-sizes each lease from peak-mem history; pin `AGDA_MB=<N>` only to override.
(Demonstrated: `make -j` over a 2-subdir node under a 1-job budget serialized cleanly via
BLOCKED/lease hand-off; exit 0.)

⚑ **Do not quote a cap, a lease default, or a build figure from this file — ask the oracle.**
The `build-system` skill routes to the `build-oracle` agent, which re-derives every number from
the file that owns it. This section has been wrong by a factor of two: `MEM_CAP` lives in
`scripts/gen_build_makefiles.py` and was restated as `256m` in three other files while its
authority said `128m`. The generated census in `.claude/skills/build-system/SKILL.md` carries the
live figures (module/edge counts, DAG depth, both caps, the three ledgers, the declared gate
roster by phase), and a pre-commit gate refuses it when it drifts.

## Build-time estimation (genlop-style): `scripts/buildtime.py`

Per-module typecheck times are recorded PER SOURCE DIRECTORY: each source dir
gets a `.agda-times.tsv` alongside its `Makefile` (gitignored — timing is hardware/cache-specific).
The **`membudget` wrapper is the universal capture point**: the agda shim routes every compile
through `membudget run`, which times ONLY the post-lease run (not the semaphore wait) and appends
`module<TAB>seconds` to the module's per-dir ledger (best-effort; never alters the compile's exit
code). The pre-commit `make -C agda -j` full build records every re-typechecked module through that same
capture point; read the accumulated history back with:

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
512; peak 65 → 128). ⚑ **THE TWO CAPS ARE DIFFERENT KINDS, NOT JUST DIFFERENT NUMBERS — and conflating them is how this
paragraph went stale.**

- **`MEM_CAP` is a GATE.** The GHC **heap** cap the build enforces per module
  (`gen_build_makefiles.MEM_CAP` is the authority — read it, never quote a number from here). Exceeding
  it is a FAILURE: the module must seal its heavy neutrals `opaque` or import a cheaper proof. Wrong-LARGE
  is the danger, which is what makes it a forcing function.
- **`AGDA_MB` is a FITTING PARAMETER.** The membudget **lease** — a cgroup `MemoryMax` over the whole
  process (maxRSS: heap + RTS + everything else). It **autosizes**: membudget tries the sized guess and,
  on an OOM kill (exit 137), releases and re-enters at the next power-of-two bucket until it fits.
  `AGDA_MB_MAX` is therefore the top of that SEARCH, not a bound the lease must respect.

⚑ **SO THE ASYMMETRY INVERTS BETWEEN THEM, and reading the lease as a ceiling gets it backwards.** For
the heap gate, a too-large value silently admits debt. For the lease, a too-SMALL guess costs one retry
and self-corrects, while a too-large one wastes pool — so starting low is correct. The whole point is
packing maximum concurrency into the global budget, which is why the default is a starting point rather
than a safe over-estimate.

**Live today: `-M128m` heap; maxRSS valid at 256 MiB.** Earlier text here said `-M256m` and derived a
384 ceiling from it (`256 heap + ~0.1 GB RTS ≈ 356 < 384`) — stranded on a premise the generator no
longer holds, and framed as a bound where the mechanism is a search. **The intended direction is DOWN:
`-M64m` heap and 96 MiB maxRSS.** Not there yet; recorded so a lower number reads as progress rather
than regression.

⚑ **AND THE SAME STALE PREMISE WAS FOUND IN FOUR MORE FILES** (2026-08-20), each restating `256m`
while the generator emitted `128m` — including `check_cap_ratchet.py`, the gate that ENFORCES the
cap, whose docstring said "the 128MiB cap" two lines above `MEM_CAP = "256m"`. All are now paid
down to CITE their authority rather than restate it. ⚑⚑ One of them, `scripts/agda-shim/agda`, was
*already* written as a citation — and cited a **line number** that had since moved, so the comment
written to prevent drift became an instance of it. Cite a SYMBOL, never a line. For any build
figure, **ask the `build-system` skill** (→ the `build-oracle` agent), which re-derives from the
owning file; the gated census in `.claude/skills/build-system/SKILL.md` holds the live values.

The strict heap gate is a FORCING FUNCTION: a module that would exceed it
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

## Observability / OTLP: the store is someone else's, the discipline is ours

Measurements move between runs, so they are only readable as a SERIES, and the series lives
in cassian's VictoriaMetrics (180d retention). Three rules, each a recorded incident.

**The read side is a TOOL, never `curl`.** `scratch/tsdbprobe.py` owns the metrics surface —
`--reachable`, `--series`, `--names`, `--query`, `--labels`, `--verify`, `--producers`. Every
question this repo has asked of the store was once a hand-assembled `curl | grep`, which is
the shape the standing rule forbids; that is how the `vm_rows_inserted_total` mistake was
made (a counter that lives only on the `:8428/metrics` exposition page, so `/api/v1/query`
returns empty — it reported "ingestion failed" on a SUCCESSFUL write, for two projects at once).

**Verification is READ-YOUR-WRITE, never a transport 200.** Emit a heartbeat whose VALUE you
control (`<prefix>_emit_unixtime` = the run's start time), then `tsdbprobe.py --verify
<selector> <value>` until that exact value reads back. Three properties are load-bearing —
do not re-derive them:

- float-tolerant compare (`abs(got-expected) < 0.5`), never string `==`: VM renders
  `1753300000` as `"1753300000"`, `"…0"` or `"1.7533e+09"`, and all three must match;
- a fetch error is a **RETRY**, not a verdict — the store may be settling under you;
- the 45s default deadline is a **CEILING ON WAITING, NOT A PREDICTION.** A too-generous
  ceiling costs nothing when the read succeeds early; a too-tight one reports a successful
  write as unconfirmed.

⚑ **AND THE MECHANISM THIS SECTION USED TO CITE WAS WRONG IN TWO WAYS** (cassian A109,
2026-08-04, correcting their own earlier guide and ours). It said: *"VM's
`-search.latencyOffset` floor (30s) plus first-run name-index creation. A 30s deadline
verifies nothing on a stock VM."*

- **The 30s is not ours to quote.** `latencyOffset` is an operational parameter of THEIR
  store, now pinned to 1.5× their ingest-buffer flush interval (7.5s at time of writing).
  A number for someone else's knob, frozen in our always-loaded file, ages into a false
  claim the moment they tune it — and an operator reading it sizes against a constant that
  is not one.
- **The "residual first-run name-index creation" was the SAME misdiagnosis, not a second
  effect.** There is no index-lag term; it was `latencyOffset` observed twice and
  attributed to two causes. We carried it as measured because a *different* project had
  measured it.

⚑ **WHAT THE OFFSET ACTUALLY DOES — and it is narrower than we assumed.** It shades the
FRESH EDGE OF A DEFAULT QUERY. It does not delay the datum and does not rewrite its
timestamp: cassian verified a point stamped two minutes in the past stored and read back at
exactly that stamp. Every returned point is an `(observation_timestamp, value)` pair, so a
consumer computing rates does so against observation time and gets an honest answer, and an
explicit `time=` / `query_range` / `export` reads the fresh edge immediately. An empty read
is still a RETRY (the offset is real) — but do not re-derive a deadline from a number that
belongs to the store.

⚑ **NOT CONFIRMED IS NOT FAILED.** An empty read has three causes — not written, written but
not yet queryable, store down — and no predicate distinguishes them. Naming one is an
unestablished cause. Report which you mean; never collapse "absent" into "failed".

**Emitting: pin the Resource.** `Resource(attributes={"service.name": …,
"service.instance.id": socket.gethostname()})` — **never** `Resource.create()`, which injects
a random per-process `service.instance.id` so every run mints a fresh series set (cardinality
churn) instead of UPDATING the same `(target, dir)` series over time.

**A REPLAY IS NOT A RE-MEASUREMENT.** `scratch/spool.py` (producer-side, daemon-free,
`SQLiteAckQueue`) buffers a sample when the store is unreachable — it cannot live on the
store's host, since that shares the outage. A replayed sample carries its OWN timestamp
verbatim; emitting today's numbers under a week-old timestamp (or the reverse) makes the
backfilled series a fiction, which is worse than the gap it fills. The spool is a BUFFER,
never a second store: depth is bounded by delivery lag, not history.

⚑ **TWO EMITTERS EXIST AND BOTH HAND-ROLL THE BOILERPLATE** — `membudget_otlp.emit` and
`run_selftests._emit_one`. Do not add a third; the ledger→gauge shape is one capability
(per-dir TSV, first column a target name, rest named numeric SLIs, aggregated last-K).
`proofcost.py`'s richer `.agda-profile.tsv` has no export path at all.

⚑ **A `--calls <name>` CENSUS IS NAME-SCOPED, NOT CAPABILITY-SCOPED.** `--calls emit` returned
"1 def, 1 call" and I wrote "there is exactly one OTLP emitter" — `run_selftests`'s is spelled
`_emit_one` and was invisible to that query. The census answered the question ASKED, not the
one MEANT: a fact about the method reported as a fact about the substrate. Ask for the
capability, and cross-check with a second spelling.

## Commit policy

Work and commit directly on `main`; the pre-commit hook (CI gates) is the promotion
gate. Commit through `mikemol-commit REPO --waypoint W --subject S [--body B] PATH ...` (the
mtools hooks dist), in the background, and **read only its last line** (`COMMITTED`, `REFUSED`,
`NOT COMMITTED`; the cause of a refusal is above it in the log). It commits through a private
index over a snapshot of the repo where the repo's own pre-commit runs with `MIKEMOL_REAL_ROOT`
set, which `.githooks/pre-commit` names (a hook that does not name it silently falls back to the
plain commit path). **Never `--no-verify`**: the harness refuses it, and post-commit refuses to
push a tree whose gate did not run. A commit that cannot pass is WORK, or an explicit operator
ruling recorded on a waypoint (the 2026-10-10 bootstrap is W332 and W333).

After a commit, the `post-commit` hook AMENDS the commit (advisory) —
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

**FASTEST first check before a new `data`/`record`:
`uv run mdstruct rows catalog/reuse-index.md --where <name>`** for the concept name
(`V4`, `Real`, `Wedge`, `Monoid`, `Stream`, `DivStr`, …; reports `n row(s)`). ⚑ The in-repo
`scratch/mdstruct.py` is RETIRED (operator 2026-09-21): the tool is mtools' `mikemol-mdstruct`,
declared in `pyproject.toml` from its git remote, modes spelled as SUBCOMMANDS. ⚑ **THIS LINE SAID `grep`
UNTIL 2026-08-13** — in the file whose FIRST section forbids grepping a structured artifact, naming a `.md`
the structural-query hook actively REFUSES, when `mdstruct` had already built `--rows --where` and named
`catalog/reuse-index.md` in its own help text as the reason. *The always-loaded file instructed a violation
of its own top rule, against a mode built to replace it.* Recorded rather than quietly corrected: the
standing rule's own statement of itself was the thing out of compliance. It is the mechanically-generated (from the
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

**AND THE SEARCH DOES NOT STOP AT THIS REPO — `summit` is the cross-repo arm.** `~/github` holds 53 repos;
substrate is an ENROLLED delegate owning `bibstruct`, `membudget`, `structural-query-hook`. Before
concluding a capability does not exist *anywhere*:

    ~/github/summit/scripts/summit                       # 9 modes; run bare
    ~/github/summit/scripts/summit capability <name>     # resolves through registered ALTERNATE SPELLINGS
    ~/github/summit/scripts/summit capability --unknown-to substrate
    ~/github/summit/scripts/summit next                  # the ranked board

⚑ **A miss prints "no entry for that spelling", NEVER "no such capability"** — the first is a fact about the
index, the second a claim the index cannot support. Same distinction as the `--calls emit` census that
missed `_emit_one`. **A miss is a finding to FILE, not a conclusion to act on**; intake is a 4–6 line bib
entry in `~/github/summit/floor/asks.bib` whose `check` must FAIL while the ask is open (no status field,
so nothing about status can go stale).

⚑⚑ **THIS POINTER IS HERE BECAUSE THE SECTION YOU ARE READING — the repo's own search-before-you-build law
— DID NOT NAME SUMMIT UNTIL 2026-08-13.** Summit's declared reach is *"this skill and opt-in session-entry
pointers"*, and substrate had neither, while gabion's docflow was rediscovered here by a USER POINTER on
2026-08-12. On every trial this repo has run, the discovery channel was the user, not the forum. **A measure
parked where the reader must already know to look is not covered** — which is why it now lives in the
always-loaded file rather than in a plan item promising to remember.

## SQL / relational algebra: ask the oracle, do not answer from memory

This repo's SQL surface is large (a live postgres store, ~90 compiled query builders, the
⟡graded-relational-carrier lift arc, a tabular allegory in Agda), spread across ~15 modules that do not
name each other, and **it moves**. Before answering any question about the store, a query builder, whether
a python op can be lifted into SQL, or relational algebra in the Agda tree — and **before writing that some
relational capability is missing, residue, irreducible, or would need a new table** — invoke the
`sql-relalg` skill, which routes to the `sql-oracle` agent.

    python3 jea/metalanguage/sql_lift.py --check-census   # is the generated map current?
    python3 jea/metalanguage/sql_lift.py --sync-census    # regenerate it

The map lives in `.claude/skills/sql-relalg/SKILL.md` as a GENERATED block (`sql-census`), derived from the
tools that own each figure and gated in pre-commit — the third member of the `query cache` / `mode census`
family, and the last of the three to get a gate.

⚑ **THE GATE IS HERE BECAUSE THE DRIFT WAS MEASURED, NOT ANTICIPATED.** During the session that built this,
a research sweep reported the compiled-query cache STALE; minutes later the same command reported it FRESH
at 90 builders. Both readings were honest — the tree moved between them. A hand-written map would have
frozen whichever one it caught, and the next reader would have trusted the sentence over the tool.

⚑ **AND THE FIRST DERIVATION OF THAT BLOCK PRINTED `0 tier(s)` BESIDE A CORRECT RELATION COUNT** — the
census read a public-looking `TIERS` that does not exist (the declaration spells it `_TIERS`), and
`getattr(..., {})` swallowed the miss. A false figure in the artifact built to prevent false figures,
caught only because the selftest asserts `> 0`. **A census cannot distinguish "none declared" from "read
the wrong attribute"**; only a case can.
