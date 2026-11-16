---
name: feedback_convergence_over_isolation
description: "prefer redundant cross-navigable implementations that prove the same point over isolated single routes; orphan lemmas (proved, no consumer/bridge) are the anti-pattern"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c1329ff9-896f-4600-8952-67ec237e5bbc
---

User (2026-06-09): "I would prefer to have redundant implementations that can
cross-navigate to prove the same points than to have things be isolated. Name of
the game is convergence without loss of demonstrable fluency."

**Why:** multiple fluent routes that provably AGREE are more valuable than one
"canonical" route — the agreement-witness is itself content, and redundancy is
robustness, not waste. This is the constructive face of
[[feedback_choice_rigidification_in_substrate]]: don't freeze one method as THE
proof and discard/orphan the others; keep them all first-class and materialize
the cross-navigation (the 2-path / cocycle, cf. [[discipline/project_homology_cohomology_recursion]],
[[feedback_two_path_commutativity]]).

**How to apply:**
- When two methods prove the same proposition (e.g. interior EEATrace-induction
  vs exterior compute-trace recurrence; shape-uniqueness vs Bézout/Euclid), build
  BOTH and add the lemma witnessing they converge. Don't frame the second as a
  "correction" that leaves the first isolated.
- An ORPHAN lemma — proved but with no consumer and no bridge to the rest — is
  the smell. (cf-step was committed orphaned; the fix is a determinism/agreement
  bridge, not deletion.)
- "Convergence without loss of demonstrable fluency": the routes converge
  (agree) but each stays independently runnable/demonstrable — closed-form
  oracles on each, decision procedures that witness-match the propositional
  proofs ([[feedback_continuous_via_discrete_inference_rules]] finite-domain
  decidability), etc.
- Concretely cheap convergence wins: a lemma is often a one-line corollary of a
  more general one (trace-shape determinism = shape-value-invariance at refl) —
  name it anyway so the bridge is explicit and navigable.
- Proof-irrelevant agreement is NOT convergence — it's the vacuous floor.
  `canonical-respects-≈ hab ≡ canonical-respects-≈-bezout hab` via Hedberg/UIP
  (`Foundation.Hedberg.Decidable⇒UIP` — it EXISTS, verify before claiming absent)
  holds because the codomain is a prop: ANY two proofs agree, so it certifies the
  type, not the routes. Real convergence is the shared assembly + the agreeing
  decision. User's frame (2026-06): read Hedberg as a CHART in an atlas (one
  coordinate system with contractible paths; forbids no other); `--without-K` is
  the phase index; track which chart so "equal (set-chart) ∧ distinct (raw chart)"
  doesn't explode. gcd/Bézout ≅ exp/ln ≅ set/proof-relevant; branch cut at 0/0
  (gcd-index 0). Landed as `Q.Properties.RouteAgreement` (certificate + the
  ≈ℚ-equal / same-reduced / raw-distinct phase-witness triangle).
