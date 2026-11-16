---
name: build-system
description: >-
  Fire this BEFORE answering any question about how this repo BUILDS: the flat Agda import-DAG
  (`agda/Flat.mk`) and its generator, `membudget` leases and memory caps, the agda PATH shim,
  the build-time / proof-cost ledgers, or the pre-commit gate pipeline — and the instant you
  catch yourself about to quote a memory cap, a lease default, a build time, or to say a build
  capability is "missing", "not instrumented", "irreducible", or "would need a new script". It
  routes to the `build-oracle` agent, which holds the map and re-derives every number from the
  file that owns it. It exists because this surface is LARGE (a ~21k-line generated makefile
  over ~3.5k modules, a bash RAM semaphore, three ledgers, ~26 gates in three phases) and
  because its numbers ROTTED: `MEM_CAP` is `128m` at its authority and was restated as `256m`
  in three other files — one of them the ratchet that ENFORCES the cap, whose own docstring
  says "128MiB" two lines above "256m". Anyone answering from memory quotes a cap that is wrong
  by a factor of two, in the direction that silently admits debt.
---

# The build-system oracle

**Route the question; do not answer it from this file.** Dispatch the `build-oracle` agent
(`Agent` tool, `subagent_type: "build-oracle"`). It starts fresh, reads the generated census
below, and runs the owning tools against the tree as it is *now*. This file carries only what a
reader must not get wrong on the way there.

## When this fires

- **How a module gets built** — what depends on what, why `make -j` is safe with no number, why
  a warm build is instant, what `check-sync` refuses.
- **Why a build failed or was killed** — an exit code, an OOM, a heap-cap kill, a gate refusal.
- **Any question naming a cap, a lease, or a budget** — and *especially* one that treats them as
  the same thing.
- **How long / how much RAM** — a module's cost, the full-build estimate, the hot spots, the
  heaviest peaks, where the cost actually lives.
- **What a gate checks** — which phase it runs in, what its statistic is, what a ratchet baseline
  means, why it fired.
- **Where a ledger column comes from** — three ledgers, three owners, two of them carrying a
  column with the same name and different authority.
- **On your own tells:** *"the build caps each module at 256m"*, *"just run `agda` on it"*,
  *"the per-directory Makefiles"*, *"I'll just use `-j8`"* (⚑ the width is ⟡agda-jobs' to
  answer, not yours to pick), *"that's just an OOM"*, *"the build isn't instrumented for that"*,
  *"I'll grep Flat.mk"*, *"peak memory is the same as the heap cap"*.

## The four facts to not get wrong

**1. `MEM_CAP` and `AGDA_MB` are DIFFERENT KINDS, and the asymmetry inverts between them.**
`MEM_CAP` is a GHC **heap gate** applied per module (`+RTS -M`). Exceeding it is a *build
failure* (exit 251) — it is a forcing function that makes a module shard, split def/proof, or
seal a heavy neutral `opaque`. **Wrong-large silently admits debt**, which is what makes it
load-bearing. `AGDA_MB` is a cgroup **lease** over the whole process (maxRSS: heap + RTS +
everything else). It *autosizes* from recorded peaks and *retries* on an OOM-kill (137/143),
doubling until it fits. **Wrong-small costs one retry and self-corrects.** So reading the lease
as a ceiling gets the whole discipline backwards. This is the single most-confused pair here,
and the census below prints them side by side for exactly that reason.

**2. There are no per-directory Makefiles, and targets are REAL FILES.** 280 recursive makefiles
were deleted because directory order encoded only **0.4%** of the real import edges. What
replaced them is one flat DAG in which each `_build/<ver>/agda/<Mod>.agdai` depends on its own
`.agda` *and every direct import's `.agdai`*, source-parsed from `open import`. That is why
make's mtime model is sound here. `touch $@` is a *separate recipe line* because agda 2.8
validates interfaces by content hash, not mtime.
⚑ **⟡agda-jobs: the `-j` width has ONE authority** — `gen_build_makefiles.AGDA_JOBS` (env
`AGDA_JOBS`; read it with `--jobs`). This file used to say *"`make -j` with no number is
correct"*, and the MEMORY half of that is still true: each `agda` blocks on the budget
semaphore, so RAM self-tunes either way. What the semaphore never bounded is **process count** —
an unlimited frontier forks a shell per ready target, thousands of them, which then sleep in
the acquire loop. The cap bounds the queue, not the throttle, and sits at or below the ~21–42
concurrent compiles the default 8 GiB budget already admits.

**3. Three ledgers, three owners — and `peak_mb` appears in two of them meaning the same thing
with only one authority.** `.agda-times.tsv` is where **Agda** peaks live (membudget writes,
`buildtime.py --mem` reads). `.agda-profile.tsv` carries seven columns from `proofcost.py`, and
its `peak_mb` is *deliberately zero* — membudget owns maxRSS. `labels.tsv` is the third, and
`membudget peaks` reads **only** that one: selftest/gate/item labels, zero Agda modules. Asking
`membudget peaks` about a module returns nothing, and that is a fact about the ledger, not the
module.

**4. Five words are overloaded here, and each has produced a real error.**
- **"cap"** — the GHC heap gate (`MEM_CAP`), the cgroup lease ceiling (`AGDA_MB_MAX`), and the
  ratchet's paydown target are three different numbers with three different failure directions.
- **"peak"** — membudget's maxRSS (whole process) vs the profiler's residency (GHC's own view).
  A module can allocate ~31.7 GB inside a 12 MB peak; time and memory are near-independent axes.
- **"build"** — `make all` (which *includes* SPPF ingestion), the pre-commit's Phase B full
  build, and a single module's compile are not the same event.
- **"gate"** — a pre-commit check, a ratchet over a materialized census, and the heap cap acting
  as a forcing function are all called gates.
- **"profile"** — `proofcost`'s Agda phase breakdown, GHC's `+RTS -s` block, and the OTLP series
  are three different instruments.

## Absence claims need a witness

This surface is where "the build can't do that" is most often a fact about the METHOD. Two live
examples, both currently true of the tree:

- **`buildtime.py --mem` exists and the mode census cannot see it.** It dispatches in the
  argument parser, but the generated `toolmodes` census reports buildtime as *"0 undocumented"*
  because the scan missed its tuple-form `("--mem", "-M")` flag. A census-based "there is no
  such mode" would report the instrument, not the substrate — the
  `census-keyed-on-one-spelling` shape, inside the tool built to prevent it.
- **`gate_ledger.py --report` ranks gates it has OBSERVED, not gates that are DECLARED.** It has
  rows for roughly half the hook's `run` call sites, from a single window, and prints no
  recency — so a stale, partial ledger reads as a complete current ranking. The declared
  population is in the gated census below.

Report presence with witnesses; say "no mode by that spelling", never "the build cannot do that".

## The census — GENERATED, do not edit

`python3 scripts/gen_build_makefiles.py --sync-census` rewrites everything between the markers;
`--check-census` is the pre-commit drift gate on the **structural** block. Every figure is
derived from the tool that owns it — the DAG from `gen_build_makefiles.parse_tree`, the lease
defaults *parsed* from `scripts/membudget`, the ledger schemas from `buildtime`/`proofcost`, the
gate roster from the hook's own call sites. **A generated block nobody regenerates is worse than
no block: it reads as authoritative precisely because it looks derived.**

⚑ **THE CENSUS MEASURES ITS OWN TOOLING, so editing the build scripts can move it.** The gate
roster is parsed from the pre-commit hook and the module count from the tree — so adding a gate
or a module shifts the block. A `--check-census` failure right after a build-tooling edit is the
instrument working, not a spurious alarm: re-sync.

⚑ **THE STRUCTURAL FIGURES ARE ONLY AS SOUND AS THE IMPORT REGEX.** `--check` compares `Flat.mk`
against the *same* regex that generated it, which is how it once certified its own blind spot: an
ASCII-only character class silently dropped 8 real edges across 5 modules. The edge and depth
counts below come from that same parse. They are derived, not independently verified.

--- BEGIN build-census ---
⚑ **GENERATED — DO NOT EDIT BY HAND.** `python3 scripts/gen_build_makefiles.py --sync-census`
rewrites everything between the markers; a hand edit is overwritten on the next
sync, and `--check-census` is a pre-commit gate that refuses drift. Every figure is
DERIVED from the tool that owns it — the DAG from `gen_build_makefiles.parse_tree`,
the lease defaults PARSED from `scripts/membudget`, the ledger schemas from
`buildtime`/`proofcost`, the gate roster from the pre-commit hook's own call sites.

⚑ **STRUCTURAL ONLY — the measured figures live in the UNGATED block below.**
Build times and peaks come from `.agda-times.tsv`, which is gitignored and
hardware-specific; gating them would fail on every machine and after every build.

```
── THE FLAT IMPORT DAG (⟡make-import-dag)
   3597 modules · 34272 source-parsed import edges · DAG depth 61
   57 roots (no in-tree import) · 942 leaves (nothing imports them)
   ONE flat makefile. Targets are REAL FILES (_build/2.8.0/agda/<Mod>.agdai), each
   depending on its own .agda AND every direct import's .agdai. There are NO
   per-directory makefiles — 280 of them were deleted because directory order
   encoded only 0.4% of the real import edges.

   ⚑ DAG DEPTH IS THE HONEST PARALLEL FLOOR. `buildtime.py --predict` divides by a
     HARDCODED J=6, which is unrelated to the RAM-derived concurrency `make -j`
     actually achieves. No schedule can beat the critical path: 61.

   most-imported:
     Substrate.Foundation.Eq                                    2441 importers
     Substrate.Foundation.Nat.Nat                               1734 importers
     Substrate.Foundation.Eq.Cong                               1123 importers
     Substrate.Foundation.Eq.Trans                              1035 importers
     Substrate.Foundation.Eq.Sym                                 943 importers

── THE MEMORY DISCIPLINE — ⚑ TWO CAPS, TWO KINDS, INVERTED ASYMMETRY
   MEM_CAP  = 128m    a GHC HEAP GATE, per module (+RTS -M). Exceeding it is a
                     BUILD FAILURE (exit 251) — the forcing function that makes a
                     module shard or seal `opaque`. WRONG-LARGE silently admits debt.
   AGDA_MB  = 192     a cgroup LEASE default (maxRSS: heap + RTS + everything else).
                     It AUTOSIZES from recorded peaks and RETRIES on OOM-kill
                     (137/143), doubling until it fits. WRONG-SMALL costs one retry
                     and self-corrects.
   AGDA_MB_MAX = 384  the top of that SEARCH, not a bound the lease must respect.

   ⚑ SO READING THE LEASE AS A CEILING GETS IT BACKWARDS. For the heap gate a
     too-large value hides debt; for the lease a too-small one self-heals. This is
     the single most-confused pair on this surface.

   membudget subcommands: cgroup init peaks probe run shell status systemd verify verify-ceiling

── THE LEDGERS — three, with three owners
   .agda-times.tsv      module ⇥ seconds ⇥ peak_mb   (last 5/module)
        written by membudget, read by buildtime.py — ⚑ where AGDA peaks live
   .agda-profile.tsv    module ⇥ total_ms ⇥ checkrhs_ms ⇥ cmp_reduce ⇥ alloc_mb ⇥ peak_mb ⇥ gc_pct
        written+read by proofcost.py — ⚑ its peak_mb is deliberately 0;
        membudget is the single maxRSS authority
   labels.tsv           label ⇥ wall_s ⇥ peak_mb ⇥ epoch ⇥ user_s ⇥ sys_s
        `membudget peaks` reads ONLY this — selftest/gate/item labels, ZERO Agda
        modules. Asking it about a module returns nothing, and that is a fact
        about the ledger, not the module.

── THE GATE PIPELINE — 38 DECLARED gates
   ⚑ DECLARED, from the hook's own `run` call sites. `gate_ledger.py --report`
     ranks only what it has OBSERVED and reads as complete — a different number.
   Phase A — cheap gates (BEFORE the build)
     · tool unit tests
     · selftest roster current
     · tool selftests
     · feature coverage
     · def/proof separation
     · UP non-vacuity
     · build makefiles in sync
     · build census in sync
     · gate census in sync
     · baseline health
     · query cache in sync
     · tool mode census in sync
     · sql census in sync
     · worklist tracker integrity
     · worklist predicate resolution
     · shape-node index current
     · import-shape ratchet
     · decl-site shape tags
     · carrier locality
     · ban ratchet
     · claims
     · rederive ratchet
     · discharge ratchet
     · snapshot guard
     · sumtype ratchet
     · mode contracts
     · divergence ratchet
     · public ratchet
     · private ratchet
     · type gate (mypy)
     · stub authority
     · apex gate
     · jea regression (Δ-G2)
     · Σ metalanguage regression (Σ6)
     · scratch-independence (Λ8)
     · scratch-runtime (Λ8b)
   Phase C — core-reading gates (AFTER the build)
     · Set₁ ratchet (elaborated)
     · cap ratchet (128MB)

   ⚑ THE PHASE IS LOAD-BEARING. Phase C gates read what the build PRODUCED, so they
     must run after it — an earlier order let the Set₁ ratchet FALSE-PASS on stale
     cores. Naming a gate without its phase is half an answer.
   ⚑ PHASE B HOLDS NO `run` GATE. The full build is a bare `make -C agda -j`, so it
     is the boundary the gates are partitioned BY, not a phase containing any.
     Its failure blocks Phase C by the same `fail`-guard the others use.

── WHO OWNS WHICH QUESTION
   scripts/gen_build_makefiles.py     THE build authority — MEM_CAP, the import DAG, Flat.mk
   agda/Flat.mk                       the generated flat DAG — one real-file rule per module
   scripts/membudget                  THE lease authority — budget, cgroup scope, retry-on-OOM
   scripts/agda-shim/agda             the PATH shim — every agda routes through membudget
   scripts/buildtime.py               the TIME/PEAK ledger reader — predict, top, module, mem
   scripts/proofcost.py               the PROOF-COST profiler — phases, alloc, GC, the regime oracle
   scripts/cap_diagnose.py            elaboration-bound vs load-bound, by three real compiles
   scripts/check_cap_ratchet.py       the per-module peak DEBT ratchet toward the cap
   scripts/gate_ledger.py             gate outcomes — order, report (OBSERVED, not declared)
   scripts/run_selftests.py           every tool's --selftest suite
   .githooks/pre-commit               THE gate declaration — three phases around the full build
```
--- END build-census ---

## The measured figures — DERIVED, NOT GATED

⚑ **These are deliberately NOT drift-gated, and the reason is structural.** They read
`.agda-times.tsv`, which is **gitignored and hardware-specific**. A `--check` over them would
fail on every machine and after every build — and a gate that cries wolf gets disabled, taking
the structural gate down with it. So: two blocks, one gate.

--- BEGIN build-observations ---
⚑ **DERIVED, NOT TYPED — AND NOT GATED.** Every figure came from the command beside
it. These read `.agda-times.tsv`, which is **gitignored and hardware-specific**, so
they are NOT drift-gated: on your machine they will differ, and that is correct.
**Re-run before asserting any of them.** Refresh with
`python3 scripts/gen_build_makefiles.py --sync-census`.

```
── COST (ledger last written 2026-08-06 18:08)
   scripts/buildtime.py --stats     (run it; no summary available here)
   scripts/buildtime.py --predict   full-build estimate (Σ medians; wall ≈ Σ/J)
   scripts/buildtime.py --top       the hot spots
   scripts/buildtime.py --mem       the heaviest peaks

   ⚑ THE ESTIMATE DRIFTS LOW, IN A KNOWN DIRECTION. It is a MEDIAN of the last
     K runs, and cold elaborations mix with warm no-ops at ~50x separation. Because
     Flat.mk targets are real files, an unchanged module is never re-invoked and
     appends no row — so warm rows accumulate and the forecast decays over time.
     The distribution is heavy-tailed, so a handful of modules own the number.

── THE CAP RATCHET
   scripts/check_cap_ratchet.py --quiet    the over-cap census (DEBT; paydown-only)
   scripts/cap_diagnose.py <mod>           elaboration-bound or load-bound?
   ⚑ Its statistic is the LATEST row, not median or max — both of the others are
     wrong here, and the docstring records why with measured windows.

── PROOF COST
   scripts/proofcost.py --top / --module <rel> / --oracle / --reprofilable
   ⚑ Cost lives in ELABORATION and ALLOCATION CHURN, almost never residency: a
     measured module allocated ~31.7 GB inside a 12 MB peak. Time and memory are
     near-independent axes — which is WHY the heap gate and the lease are
     different kinds rather than two spellings of one budget.
   ⚑ `--top` may show alloc_MB 0.0 for rows predating the `+RTS -s` capture; that
     is a legacy artifact, not a measurement. `--module` shows the real figure.
   ⚑ `--oracle` ranks over ALL profiled modules including the ones
     `--reprofilable` warns are not clean; the filter is not composable onto it.

── GATE OUTCOMES (ledger last written 2026-10-10 12:30)
   scripts/gate_ledger.py --order / --report
   ⚑ OBSERVED, NOT DECLARED. It ranks only gates it has recorded rows for, and
     prints no recency — so a stale ledger reads as a current ranking. The DECLARED
     population is in the gated block above.
```
--- END build-observations ---

## Growing this

A missing mode is WORK, not a finding. Each of these is a question this surface **cannot
currently answer**, and each is a build rather than a wall:

1. **`gate_ledger.py --coverage`** — "which declared gates have never been recorded?" It cannot
   know the declared population, only the observed one, so it reports complete coverage of a
   subset. The hook's `run` call sites are the population; the census above now reads them, and
   the ledger should too.
2. **`gate_ledger.py --staleness`** — nothing surfaces how old the newest row is; `--report`
   prints rates with no recency at all.
3. **`buildtime.py --jobs N` / `--critical-path`** — `J` is hardcoded to 6. The DAG depth is now
   derived and in the census; wiring it in would replace a guess with a bound.
4. **`buildtime.py --bimodal`** — nothing separates cold-elaboration rows from warm no-ops, so
   the median's contamination is invisible even though the gap is ~50×.
5. **A read-only `cap_diagnose`** — every mode compiles, so triaging the over-cap census as
   load-bound vs elaboration-bound currently requires a build.
6. **`membudget peaks --agda`** — `peaks` reads only `labels.tsv`; Agda peaks live in a different
   ledger reached through a different tool. One capability, two spellings.
7. **`proofcost.py --oracle --clean`** — `--oracle` ranks over all profiled modules including the
   ones `--reprofilable` warns are unclean; the filter exists but is not composable onto it.
8. **The `struct-tools` artifact→tool table has no build row.** `Makefile`, `.mk`, and the `.tsv`
   ledgers are unclaimed, so the structural-query hook does not defend them — a textual read of
   `Flat.mk` passes today where the same read of a `.py` or `.md` is refused. Adding the row is
   the work.
