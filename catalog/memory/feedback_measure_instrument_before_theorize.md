---
name: feedback_measure_instrument_before_theorize
description: "a perf/resource symptom is a MEASUREMENT to take (MAJFLT/PSI/EXPLAIN QUERY PLAN/exit-code), not a theory to spin (swap/OOM); run long jobs harness-tracked so the exit code exists"
metadata:
  node_type: feedback
  type: feedback
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
  modified: 2026-07-21T14:29:11.464Z
---

When something is slow / heavy / dies, MEASURE the instrument before theorizing a cause. 2026-07-13 I burned
a lot of the user's attention asserting "swap → iowait" and "OOM" with zero evidence; the user corrected each:
memory-PSI stalls are NOT iowait; a zram/zswap box's swap pressure is compressed-RAM (CPU), not disk io;
"if it had OOMed you'd have a specific exit code / an oomd notification." The REAL signal was `MAJFLT` (major
page faults from the disk swapfile) visible in `atop` — which I only saw once the user showed it.

**The instruments (reach for these, in order, before any cause story):**
- process: `atop`/`ps` **MAJFLT** (disk-swap faults = real iowait), RSS/VDATA, `/proc/<pid>/io`, and the
  **exit code** (137 SIGKILL/OOM vs 143 SIGTERM vs 124 timeout vs 0).
- system: `/proc/pressure/io` vs `/proc/pressure/memory` (io PSI ~0 ⇒ NOT disk-stalled), `swapon --show`
  (zram vs disk swapfile), `zramctl`.
- DB: `EXPLAIN QUERY PLAN` (a `MATERIALIZE <view>` / `USE TEMP B-TREE` / `USING AUTOMATIC … INDEX` = a
  missing index, the last literally SQLite saying "index here").

**Run long jobs harness-tracked, never `nohup … &`.** I detached a 25-min run with `nohup &` and thereby
discarded its exit code — so when it died I had no signal and spun OOM/swap theories. A harness-tracked
background job (run_in_background) captures the exit code and notifies; that IS the diagnosis.

**The meter you read must be the COMMAND's, not the PIPELINE's.** `agda … | tail -3; echo $?` reads TAIL's
exit (0) — a proxy meter. 2026-07-16 this nearly blessed a BROKEN Tree.agda as "exit 0" while the visible
text was a ConstructorDoesNotFitInData error fragment; caught only by the error-text-vs-exit contradiction.
Redirect output to a file (`cmd > /tmp/out 2>&1`), THEN read `$?` — or `set -o pipefail`. Same class as the
proxy meters above, one level up: the instrument itself was swapped for a proxy.

**Don't flip-flop before measuring.** I materialized path_text → reverted → re-materialized, arguing each
way, before running `EXPLAIN QUERY PLAN` — which settled it in one shot (the view forces a full
materialization per keyed join; a PK-indexed table is one index seek). Measure first, decide once.

**⚑ NOT ONLY PERF — the class is GATES, POLICIES and DIFFICULTY.** 2026-07-21 I made four claims by READING
an instrument instead of RUNNING it, and execution refuted all four: (1) "`check_carrier_locality` will trip
on this term" — it needs `_` in the name AND a strictly-endo type; RAN IT: clean, rc=0. (2) "a third `Corr ⇔ …`
trips the law-motif apex gate" — the threshold is 3 not 2 AND it counts only `≡`-motifs, so a `⇔` term is
INVISIBLE to it; RAN IT: OK, rc=0. (3) "propagating `--guardedness` costs 8 modules" — the closure is 33, and
15 of them have no coinductive interest at all (which REFINED the policy: propagate along genuine
participation). (4) "proving `x` irrational here is deep mathematics" — a 5-line probe showed the intended
statement is FALSE as posed (`qStep` junk-pads ⇒ every `qToRℚ q` is eventually constant). **Before writing
"this gate will fire" / "this policy implies X" / "this needs new mathematics" — run the script, test the
policy against its own stated purpose, or write the 5-line probe.** Reporting your READING of an instrument as
its BEHAVIOUR is the same error as reporting a property of your ROUTE as a property of the THING
([[feedback_report_presence_never_absence]]) — one level up, at the meter.

This is the perf-domain twin of [[feedback_surprises_are_questions_not_walls]]: a surprise is a question you
CHASE WITH AN INSTRUMENT, not a wall you declare or a theory you spin. Relates to
[[feedback_sql_declarative_over_materialized_enumeration]], [[validate-outputs-inputs]].
