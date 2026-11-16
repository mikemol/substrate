---
name: feedback_reread_meters_toctou
description: "a hardware/perf reading is DEPENDENTLY TYPED on the runtime state at read-time; caching it and reasoning later is a TOCTOU race — re-read meters at point-of-use, co-read meter+state atomically, never carry a bare scalar across time"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

A measurement of a live system (bandwidth, efficiency, clock, link state, temperature) is **not a scalar** —
its type is `(runtime state at read-time) → value`. It is **dependently typed on the state it was read in**.
The environment is STATEFUL; these structures are not static. Two consequences I keep violating:

1. **TOCTOU (time-of-check / time-of-use).** If you read meter A at time t1, read state B at time t2, and
   COMBINE them at t3, you are composing readings from DIFFERENT world-states — the invariant moved between
   check and use. (Concrete: I measured PCIe efficiency with a saturating transfer that TRAINED the link to
   gen4, then multiplied it by the IDLE link_state from an earlier poll → double-counted; the two readings
   were from different link states. My "fix" was to PIN link_state=1.0 to make them agree — treating the
   symptom by forcing a world-state, the rigidification reflex, NOT a fix.)
2. **Dependent-type mismatch.** Using `efficiency@gen4` where `efficiency@gen1` is required is a TYPE ERROR
   that surfaces as a wrong number, not an exception. A bare-scalar cache erases the state index that would
   have caught it.

This is the structural-not-scalar law ([[feedback_structural_not_scalar]]) extended to the TEMPORAL axis:
not only is a perf bound a topology not a scalar, every READING is state-indexed and stale the instant it is
cached. It is also why the user keeps advocating "re-read the metrics/meters before reasoning" and why audits
must ground on CURRENT measurement, not remembered values ([[feedback_silo_sprawl_orphans_fixes]],
[[feedback_validate_outputs_not_inputs]]).

**How to apply:**
1. Where you CAN re-read the meter at point-of-use, DO — a fresh read inherently carries the current state, so
   the race cannot open. Prefer measure-at-use over measure-then-reason. Do not cache a reading and compute
   with it a turn/window later.
2. Where you MUST predict a config you're not currently running, carry the factor as a STATE-INDEXED reading
   (co-read meter + its state atomically, stamp the reading with link_state/T/governor) and apply it only at
   the matching state — re-read or reject on state-mismatch, never blind-multiply a stale factor by a fresh
   live_state.
3. Treat any "I measured X earlier, so X is …" as suspect: X was true at its read-state. Re-read before
   reasoning. A pinned/forced world-state that makes cached readings agree is a symptom-patch, not a fix.
