---
name: feedback_dont_reconstruct_a_missing_source_and_conclude
description: "when the authoritative generator is missing, a guessed reconstruction's unverified assumptions can flip the conclusion — don't conclude from a reconstruction"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

When a handoff cites a result computed by a SOURCE you don't have (e.g. `jea_orbit_cloud_gen.py`), do NOT reconstruct the source from prose and then draw a CONCLUSION from your reconstruction. The reconstruction's unverified modelling choices can flip the answer.

**The Ⓟ.3 error:** the doc said "rung 3 → 22-not-24 near-degeneracy." I had no orbit-gen, so I reconstructed "Cpinv·P_edge·C" from the prose — guessing a **signed** edge permutation (±1 orientation). That made the S₄ cycle-space rep spuriously **faithful** → 24 → I concluded *"22 is a float artifact, exact is 24"* — and was about to commit it. The user held me up; the updated handoff shipped the actual probe, which uses an **unsigned** edge perm → τ=(0 1)(2 3) acts as a reflection T (T²=I) → the rep is non-faithful → **exact 22** (the idempotent species). My conclusion was the OPPOSITE of the truth, and the whole difference was one unverified assumption (signed vs unsigned) buried in a reconstruction.

**Why:** "verify by compile" only refutes by-read assumptions if you compile the RIGHT object. I compiled my guess, not the real generator — so I "verified" a fiction with full confidence.

**How to apply:** if the authoritative generator is missing, either (1) ask for it / wait for it before concluding, or (2) mark every finding from a reconstruction as PROVISIONAL ("under my reconstruction X; needs the real source to confirm") and never let it overturn the handoff's stated result. A reconstruction that CONTRADICTS the handoff is a flag on the reconstruction first, not on the handoff. Sibling of [[feedback_validate_outputs_not_inputs]] (clean inputs, wrong derivation) and [[feedback_test_the_wall_before_declaring_it]] — here the "wall" was self-built.
