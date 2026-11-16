---
name: feedback_trace_state_is_sppf_not_adhoc
description: "trace-shaped state (a decision log / WAL / sequence of computed steps) IS an EEA/SPPF trace -- hold it in the term-algebra SPPF (the project's never-discard-residue structure), do not reinvent an ad-hoc array"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

When you find yourself building an ad-hoc array/log to hold a SEQUENCE of computed steps (a decision
trace, a "WAL", a history of operating points), STOP: that is an EEA/SPPF trace, and the substrate's
term-algebra SPPF is the structure built to hold it. Reinventing it as a flat device array
(jea_apex's `dout`) is the same orphaning reflex one level up. (User, 2026-06-16: "the pattern you're
looking for is a WAL... that's kinda what the SPPF is supposed to help with -- holding the decision
traces. Since the decision trace is an EEA trace, if you used the term algebra properly. And did we
orphan the SPPF work?" -- an import-audit then confirmed jea_agda_dag (Agda SPPF-on-GPU) + jea_intern
(device dedup) + the sppf/trace cluster were imported by NOBODY.)

**Why:** the substrate's whole point is never-discard-residue traces held in ONE structure. The EVAL
trace (the SPPF DAG of shared subterms), the gcd/EEA REDUCTION residue (quot+rem+cofactor), and a
SUPERVISOR DECISION trace (the WAL) are the SAME never-discard-residue object. Built separately they
fragment and the SPPF machinery rots orphaned -- you lose sharing/memoization (the charter's "on-GPU
resident MEMOIZING traces") and re-derive what the trace already holds.

**How to apply:**
- Before adding any array/log of computed steps, ask "is this a trace?" If yes, route it through the
  term-algebra SPPF/EEA (jea_agda_dag / jea_intern / sppf_*), not a new array. Reuse, don't reinvent.
- Run the import-audit ([[feedback_demo_proven_is_not_wired]]) on the SPPF cluster: if the trace
  structure is orphaned, that is the work to compose, not route around.
- Recurse "find the common structure": eval-trace = gcd/EEA-residue = decision-WAL = one SPPF.
See [[feedback_never_discard_residue]] (the residue spine) and the charter (memoizing traces = SPPF).
