---
name: feedback-reject-lem-in-substrate
description: "In the substrate repository, the law of the excluded middle is rejected. Reason intuitionistically — affirm only what is constructively shown; do not assert ¬P from absence of a P-witness; the disjunction P ∨ ¬P is not automatic."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

**Epistemic rule for this repository (user-declared, 2026-05-15):
LEM is rejected.** Operate intuitionistically. The disjunction
`P ∨ ¬P` is not automatic; absence-of-affirmation is not negation.

**Why:** This rule makes explicit what the project's foundations
already commit to. M1's realizability charter
(constructible → reachable → observable → coverable) is a stack of
constructive predicates; the topos framing from §Context is
Brouwer-Heyting in spirit; and the failure mode this rule defends
against has already shown up empirically — see
[[feedback-negative-findings-in-corpus]] and
[[project-k-v4-twins-fail-cells-false-negative]]. Under LEM, "the
audit failed to find a V₄-twin inhabitant" silently collapses to
"V₄-twin cells are uninhabited"; under intuitionism that step is
forbidden — the absence of a positive witness is not a negative
witness.

**How to apply:**
- **Asserting P**: produce a construction or proof witness.
  Affirmations are first-class.
- **Asserting ¬P**: produce a derivation `P ⊢ ⊥` (a counterexample,
  an explicit contradiction, an absurdity from assuming P). Without
  one, do not assert ¬P; describe what *was* checked, in
  existence-form ("on input X, property Q was observed; on input Y,
  property Q was not observed; no claim is made about other
  inputs").
- **Avoid LEM disjunctions**. Don't say "either X holds or it
  doesn't"; that's a non-fact. Phrasings like "we either prove X or
  refute it" smuggle LEM in. Replace with: "we will attempt to show
  X; if we cannot, the catalog records X as `open`, not
  `refuted`."
- **`¬¬P` is not `P`.** Double-negation elimination is unsound here.
  "P is not ruled out" does not entail P; "the audit found no
  counterexample" does not entail "the property holds universally."
- **Status taxonomy in catalog/claims.md**: `negative` requires
  constructive disproof. Use `open` or a new `disaffirmed (no
  constructive disproof)` status when an audit reported failure
  without exhibiting absurdity.
- **`refutes` edges in catalog/entailment.md**: require constructive
  warrant. An audit that "failed to verify" is not a `refutes` edge.
- **Negation-as-failure** (Prolog-style closed-world) is permissible
  for finite enumerable domains where the enumeration was actually
  done; cite the enumeration. Anywhere else, do not collapse
  not-found to not-exists.
