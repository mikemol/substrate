---
name: feedback_hunt_opacity_after_green
description: "after a green result / \"complete\" model, do NOT declare completeness — hunt the residual opacity (what's still a measured primitive / black box?)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

After any green/PASS result or a model that feels "complete," do NOT declare completeness ("opacity
dissolved", "complete theory", "done", "fully unified"). Run one pass asking: **what in this result
is still treated as a measured primitive / a black box / an ephemeral residue?** Name the next
recursion rung explicitly, even if deferring it.

This session (kernel-perf nedge arc, 2026-06-14): I declared "opacity dissolved" / "complete
performance theory" ~5 times in one arc, and EACH time the user found the next opaque primitive I had
stopped short of: measured-rate → eval strategy (fused vs eager); "ephemeral" residual → page-faults +
cpufreq governor (controllable); the REASONING itself → a self-falsifying cost cotype; min() → not an
operator at all, the read-off of the circuit's minimum-dissipation settle. The user drove the best of
the session by supplying the "what's still opaque?" question my loop wasn't asking. Every "X is a
primitive we measure" turned out to be structure not yet modeled.

**Why:** the closure-reflex (framing a green pilot as DONE) stops the structural analysis exactly one
layer too early. Success is the most dangerous place to stop, because the green result feels like
permission. Success-side twin of [[feedback_test_the_wall_before_declaring_it]] (which guards premature
WALL / give-up; this guards premature COMPLETION / victory); same family as
[[feedback_governing_law_before_special_case]] and [[feedback_never_discard_residue]] (the residue/
opacity is always more structure).

**How to apply:** before saying "done/complete/dissolved", enumerate (a) which inputs are still
measured-not-derived, (b) which terms are still opaque/ephemeral, (c) the next recursion rung — and
say them out loud even when deferring. This IS the retrospective's G8 (the cross-pass blind spot) run
proactively at every green, not just at session end. If you cannot name a residual opacity, say "I
can't find the next opaque primitive" rather than "this is complete."
