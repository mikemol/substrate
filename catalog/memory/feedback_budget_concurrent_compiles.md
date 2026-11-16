---
name: feedback_budget_concurrent_compiles
description: "ad-hoc background compiles share ONE machine's RAM — cap memory + kill-before-launch + one heavy compile at a time, or they OOM the box"
metadata:
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

A background compile is NOT a free, isolated task — it draws on the **shared, finite RAM of the user's machine**, and I launch them freely (`run_in_background`, shell `&`) without ever reconciling their COMBINED peak memory. This is [[feedback_structural_not_scalar]] / [[feedback_reread_meters_toctou]] applied to **my own processes**: machine RAM is a live shared topology, not a per-task scalar I can ignore.

**The incident (2026-06-19, AES full-encrypt KAT):** I had the monolithic KAT `refl` compile running at **5.6 GB resident** (a known hog — I'd measured it), AND launched the `Steps.agda` compile (heavy), AND several diagnostic probes, AND the IDE auto-compiled `Full.agda` (which pulls `Steps`) — all concurrently. The machine **OOM'd** ("Everything OOM'd"). Each was "fine alone"; co-resident they weren't. The pre-commit full build is safe precisely because it caps each module (`+RTS -M1024m`, bounded `-j6`); my ad-hoc launches had NO such cap and accumulated.

**Why:** the agent loop has no step that budgets the shared resource across concurrently-launched background work. "Bounded per-module in the gate" ≠ "bounded as I run things by hand."

**How to apply — THE TOOL (built + validated 2026-06-19, user-designed): `scripts/membudget`.**
A two-layer correct-by-construction guard:
- **cgroup cap (per tree):** wraps `systemd-run --user --scope -p MemoryMax=<MB> -p MemorySwapMax=0` — the kernel kills only that scope (exit 137) if it exceeds; the box survives. Strictly better than `+RTS -M` (heap-only, single-process, advisory).
- **semaphore (sum of trees):** a shared cotype ledger (`~/.cache/membudget/budget.cotype`, `TOTAL_MB` − Σ active `LEASE`). `run` atomically LEASES before launching; if the budget can't cover it it **BLOCKS** (WaitForSingleObject-style: wakes on a release, re-attempts, proceeds when it fits) — so a forgotten second concurrent launch *waits its turn*, not OOM/error. REFUSES (exit 3) only the IMPOSSIBLE (request > the level's TOTAL — would block forever); `MEMBUDGET_NOBLOCK=1` fails fast, `MEMBUDGET_TIMEOUT=<s>` gives up. Leases release on exit + auto-GC on dead pid. Deadlock-free: single-resource-per-acquire + impossible-refuse guard; blocking is per-level (top→global, nested→parent).
- **shell injection:** `source scripts/membudget-shrc` auto-wraps bare `agda` (→ `membudget run`, cap `AGDA_MB`); `scripts/membudget shell [MB]` runs a shell inside one scope (cgroup auto-contains the hierarchy). Permanent via a `~/.bashrc` source line.

```
scripts/membudget init --reset 9000                          # set/resize global budget (MB), keeping live leases
scripts/membudget run 4000 KAT.Round3 -- agda --safe -i. <Module>.agda
scripts/membudget status                                     # TOTAL/leased/free + leases
```
Validated: 6000-lease holder + concurrent 4000 request (free 3000) → REFUSED; over-cap child SIGKILL'd, box alive. **Use `membudget run` for EVERY heavy Agda compile** (don't call bare `agda`/`systemd-run` for hogs). Now the session-loaded default via CLAUDE.md (Ⓡ⊕, committed).

**Recursion-aware (Ⓡ⊕ upgrade):** a membudget job may itself call membudget (e.g. a build script wrapping each module). A nested call (detected via the exported `MEMBUDGET_PARENT`) SUBALLOCATES from its parent's reservation — NOT the global pool the ancestor already holds — and runs **in-scope** (no new `systemd-run` scope: a nested scope is a SIBLING cgroup that would escape the parent's cap; staying in-scope keeps the top-level `MemoryMax` bounding the whole subtree). So nesting never deadlocks on the global budget and never double-counts; a child is refused only if its PARENT's reservation can't cover it. Validated 3-deep + sibling-bounded-by-parent + concurrent-top-globally-bounded. Size the top-level budget for the whole subtree.

Also still: kill-before-launch (`pkill -f agda`) and treat a measured multi-GB process as a red flag.

Twin lesson (technical, same incident): a monolithic `refl` over a deep composition blows up (no term sharing); the fix is **per-round-per-file decomposition** with concrete intermediate-state literals as clean handoffs (see [[reference_proved_lookup_table_aes_pattern]]) — "the final state must not carry residues from earlier states."