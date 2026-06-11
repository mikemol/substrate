# NEXT — session handoff (written at d5962fd, 2026-06-11, pre-flush)

The context window is volatile; this file is the refresh. A new
session should trust DISK over any summary: cotype (S0-S46) is the
memory; reading-ledgers/ hold brick states; the obligation register
is spec-src/15/00/ (one leaf per OB).

## State at handoff
- HEAD d5962fd; tree clean; instrument v3.8.3; space S_6c040a08a0f2
  (moves ledgered S44a/S45/S46); spec sha f4eaedf73341 (composed).
- spec-src/ is a btree: numeric node folders mirror document numbers
  ('0' preamble < '00' ... '15' < 'A','B','C'); METADATA per node
  (frontmatter, never composed); leaves NN.md; LAZY SPLITTING — split
  any node you touch that is too big to rewrite whole in one pass;
  every split must reassemble byte-identically (assert it).
- Composer: tools/compose-spec.py (recursive sorted walk, no-shrink
  guard). MANIFEST is retired.

## Standing operational patterns (hard-won; do not relearn)
- After every commit: `sh tools/githooks/post-commit` (the mount
  drops exec bits; sh needs none; gc is memoized via --auto).
- Mount stalls: sync; sleep; retry with timeout. A failed `git add`
  leaves work on disk — verify HEAD before assuming a commit landed.
- Never interleave heredocs on one chained line; sequential
  statements only.
- Before building on the spec: compare its bytes to the last
  ledgered compose (interrupted turns can leave executed-but-
  unledgered deltas; S43 caught one).
- Brick reading: fresh prints only — "content in hand" is not a
  verification class (ledger states: DONE-FRESH /
  ASSERTED-FROM-HELD-CONTEXT / DEFERRED). Captures carry a
  provenance stratum (documents can be temporally composite).
- Space fingerprint moves are universe moves: ledger every move with
  its cause, verify truth content index-only when expected.

## WAL protocol (S47 — this supersedes ad-hoc pre-flush prep)
- wal.md is write-ahead: BEGIN (intent + expected artifacts) is
  COMMITTED BEFORE a multi-step move executes; END (outcome,
  head=<sha>, artifacts=<paths>) commits with the result; ABORT with
  reason if abandoned. tools/wal-check.py enforces: no dirty tree
  without an open BEGIN; last END's head an ancestor of HEAD;
  declared artifacts exist. SESSION START = run wal-check FIRST (the
  recovery replay); an open BEGIN at start means the prior window
  died mid-move — verify, redo, or ABORT before anything else.

## Opening moves, in order
0. python3 tools/wal-check.py  (recovery replay — before all else)
1. A/B/A2/B2 brick layers for parts 2-5 (ledgers mark them DEFERRED)
   — structurally fresh in a new context; the M/Q layers yielded
   4/4 and 5/6, so expect catches, and report zero-yields honestly.
2. System Pi v2.22 read (Drive doc 10GrDUQdXh_uLc-bUGBiuXPyYSY8C8Zxw
   XKd1s3F-dMc, ~115KB — acquire-once, digest-in-bricks). Targets:
   (a) COC-5 fork — is Functorial_Integrity_Check defined there?
   (internal-pending vs self-containment-violation); (b) the Lojban
   "pamoi liste" locale-verdict question (proc1 H1 pointer); (c)
   does RationalDef exist in the v2.22 lineage? (If yes: COC-2
   becomes a transmission-loss finding — defined in the lineage,
   lost in the v2.37.1 rewrite, sealed anyway.)
3. Standing candidates needing machinery, from the cotype queue:
   witness-relations joiner tests ({LOC,L26},{PUR,PRO}), the
   {TWN,D4C} 2-cell, homological-stability split-test (thread 20),
   COC-4 (classical LUB vs intuitionism — confirmed candidate,
   banked), christening-artifact hunt (bound <= 2025-07-22T19:27),
   proof tier (the Agda rung — still the registered empty).

## Cocycle ledger (for orientation)
COC-1 confirmed (nominal seal; mistyped scan); COC-2 confirmed
(pending item at closure — RationalDef; boot predicted to fail the
terminal coherence check); COC-3 resolved (Boolean-where-decidable);
COC-4 candidate (LUB vs intuitionism); COC-5 candidate (fork on
v2.22). All in Earley vocabulary per S40.
