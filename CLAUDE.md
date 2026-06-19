# substrate — working instructions

## Heavy Agda compiles: ALWAYS via `scripts/membudget` (never bare `agda` for hogs)

A heavy `agda` compile can consume many GB; run concurrently with others (or with
the IDE's background typecheck) it can OOM the whole machine — this happened
2026-06-19 (a 5.6 GB monolithic KAT `refl` stacked with other compiles took the box).
To make that impossible by construction:

    scripts/membudget init 9000                                  # once per boot: global RAM budget (MB)
    scripts/membudget run <MB> <label> -- agda --safe -i. <Module>.agda
    scripts/membudget status                                     # TOTAL / leased / free + active leases

`run` does two things:
1. **cgroup cap (per tree):** launches the compile in a `systemd-run --user --scope`
   with `MemoryMax=<MB>` + `MemorySwapMax=0` — the kernel kills only that scope
   (exit 137) if it exceeds; the machine stays up.
2. **budget semaphore (sum of trees):** leases `<MB>` from a shared cotype ledger and
   **REFUSES (exit 3)** if free budget can't cover it — a forgotten second concurrent
   launch is blocked, not OOM'd. Leases release on exit and auto-GC if an owner dies.

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

Rationale + history: memory `feedback_budget_concurrent_compiles`. The pre-commit
full build already caps each module at `+RTS -M1024m`; `membudget` is the same
discipline for the ad-hoc compiles I run by hand.

## Commit policy

Work and commit directly on `main`; the pre-commit hook (CI gates) is the promotion
gate. After `git commit`, the `post-commit` hook AMENDS the commit (advisory) —
**wait for the marker `post-commit advisory (auto-captured)` in HEAD before pushing**,
then `git fetch` + fast-forward. See memory `feedback_commit_on_main_ci_gated` and
`feedback_wait_for_postcommit_amend_before_push`.
