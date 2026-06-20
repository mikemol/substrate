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
`membudget run` (cap/lease `AGDA_MB`, default 2048; `AGDA_MB=8000 agda …` for heavy modules). The ledger is a shared file, so this budgets agda across separate
shells too (concurrent background compiles can't OOM the box — a second is refused).
For a whole contained session, `scripts/membudget shell [MB]` opens a shell inside one
top-level scope (the cgroup auto-contains the entire process hierarchy) with the rc
loaded. To make it permanent for every shell:
`echo 'source ~/github/substrate/scripts/membudget-shrc' >> ~/.bashrc`.

Rationale + history: memory `feedback_budget_concurrent_compiles`. The pre-commit
full build already caps each module at `+RTS -M1024m`; `membudget` is the same
discipline for the ad-hoc compiles I run by hand.

## Building the tree: `make -j` self-throttles by RAM

The build is recursive make (`agda/Makefile` → per-dir, `AGDA ?= agda`, one process per file).
With the shim active, **`make -j` with NO number is the right invocation** — it spawns the
whole dependency frontier and each `agda` blocks on the budget semaphore, so effective
parallelism self-tunes to memory availability, in dependency order (no `-jN` guess, no OOM):

    cd agda
    source ../scripts/membudget-shrc        # puts the agda shim on PATH
    ../scripts/membudget init 8192           # RAM to devote (MB)
    AGDA_MB=2048 make -j                      # unbounded; throttles to ~budget/AGDA_MB concurrent

`make`'s recipes resolve `agda` via PATH → the shim → `membudget run` → blocks/leases. The
per-file `+RTS -M1024m` heap cap keeps each job under `AGDA_MB`. Tune `AGDA_MB` to the heap
cap + overhead (~1.5–2 GB). (Demonstrated: `make -j` over a 2-subdir node under a 1-job budget
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
(`/usr/bin/time -v` maxRSS → the `peak_mb` 3rd ledger column) and, when the lease is `auto`, SIZES it
from that history: `max(peak)·1.3 + 256`, clamped to `[512, AGDA_MB_MAX=8000]`, falling back to
`AGDA_MB_DEFAULT=2048` with no history. So a light module (e.g. 65 MB peak) leases ~512 MB instead of
2048 → more `make -j` modules fit the global budget concurrently; a heavy module leases big → still
safe. `AGDA_MB=<N>` pins a fixed lease; `scripts/buildtime.py --mem` shows the per-module peaks/leases.

## Commit policy

Work and commit directly on `main`; the pre-commit hook (CI gates) is the promotion
gate. After `git commit`, the `post-commit` hook AMENDS the commit (advisory) —
**wait for the marker `post-commit advisory (auto-captured)` in HEAD before pushing**,
then `git fetch` + fast-forward. See memory `feedback_commit_on_main_ci_gated` and
`feedback_wait_for_postcommit_amend_before_push`.
