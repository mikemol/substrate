# NEXT — session handoff (REWRITTEN W15, 2026-06-11; supersedes the
# d5962fd version, which listed since-completed work as opening moves)

Trust DISK over any summary. Memory: el-atlas-cotype.md (S0-S60).
Recovery replay: python3 tools/wal-check.py FIRST, every session.

## State
- HEAD: see git; tree clean at last END. Instrument v3.8.5, space
  S_49a935bae7dc; WITNESS_RELATIONS COMPLETE (no unregistered pairs).
- WAL: 15 moves; BEGIN lines now carry pre=<sha> (W14 convention;
  check (5) enforces pre..head ancestry). Flush-recovery doctrine
  unchanged (resent prompt => wal-check, match open BEGIN, complete
  not re-run).
- Proof tier OPEN: proofs/VerdictCrossbar.agda checked clean
  (--safe --without-K, Agda 2.6.3, zero imports). Reinstall recipe in
  proofs/CHECKED.md (container is ephemeral; source is durable).
- Corpus: v2.22 full snapshot recovered/system-pi-v2.22/v2.22-full.md
  (sha 8216a229f629; ONE physical line — substring windows, never
  line tools). v2.37.1 set recovered/system-pi-v2.37.1/. Lineage:
  recovered/lineage-map.md (christening 2025-07-22T19:02Z verified).
- Cocycle ledger CLOSED: COC-1..5 all confirmed/resolved (S55 forms).

## Opening moves, in order
1. A2/B2 brick layers for part 4 + treatise — DECAY-GATED: their A/B
   reads were post-flush in the prior window; a new session satisfies
   the decay condition. Ledgers in reading-ledgers/.
2. Read "Nedge G-Value Calculus: Formal Specification (Agda)" (Drive,
   by title): the ancestor's own proof tier; check its NedgeGCalculus
   module against our VerdictCrossbar and against the spec's
   line-1987 postulate-vs-derive note (its preamble claims to resolve
   exactly that). Companion: "Agda SPPF G-Value Calculus Synthesis".
3. Proof-tier next rungs (registered S58): grades; joiners; the H2
   separation; full S3 over arbitrary quotients (not just Boolean).
4. Pamoi-liste question — RELOCATED to the unsnapshotted v2.23-v2.36
   stream or the v2.37 conversation; needs sources we lack. Parked.

## Standing operational patterns (unchanged; do not relearn)
- After every commit: sh tools/githooks/post-commit.
- Mount stalls: sync; sleep; retry; verify HEAD.
- No interleaved heredocs on chained lines.
- Bricks: fresh prints only (DONE-FRESH / ASSERTED-FROM-HELD-CONTEXT
  / DEFERRED); elision "[...]" is the named Flaw — FIVE violations on
  the ledger now (W15 added: unverifiable truncated doc-IDs written
  to lineage-map; repaired same-window).
- Space moves: ledger with cause; truth content index-only when
  expected.
