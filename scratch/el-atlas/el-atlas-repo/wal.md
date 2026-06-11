# WAL — write-ahead log (append-only; committed before the work it sanctions)

Protocol: every multi-step move opens with a BEGIN entry (intent +
expected artifacts), COMMITTED BEFORE the move executes; the move
closes with an END entry (outcome, head, artifacts), committed with
the resulting state. Recovery rules: a BEGIN without END is an
incomplete move — verify, redo, or append ABORT with reason; any
state delta not covered by a BEGIN..END span is unsanctioned —
investigate before building on it (the S43 class). The cotype
(S0-S46) is the historical log-behind, grandfathered by this genesis;
write-ahead discipline applies from W1 forward. Checker:
tools/wal-check.py (run at session start, before flush, and by the
post-commit hook in warn-only mode).

GENESIS 2026-06-11 :: cotype S0-S46 + 67 commits grandfathered as log-behind history; WAL begins.
BEGIN W1 2026-06-11T23:5x :: implement WAL machinery and adopt write-ahead discipline
  expect: tools/wal-check.py, hook warn-line, NEXT.md protocol section, cotype S47, END W1
END W1 2026-06-11 :: machinery built and bootstrapped :: head=ac0c909 :: artifacts=tools/wal-check.py,NEXT.md,wal.md
BEGIN W2 2026-06-11 :: resolve waiting joiner pairs {LOC,L26}, {PUR,PRO} at the witness stratum; register results in WITNESS_RELATIONS (v3.8.4)
  expect: tools/joiner-pairs-pilot.py(+out), harness v3.8.4 with two new relations, run txt, regen, space-move ledger, cotype S48, END W2
