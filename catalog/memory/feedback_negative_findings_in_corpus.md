---
name: feedback-negative-findings-in-corpus
description: "In LLM-authored corpora like substrate, the negation IS the overclaim. Distrust negative findings by form, not just by content — an assertion of failure carries hidden universal quantifiers that the LLM rarely actually verified."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

In LLM-authored work, **the negative form itself is the overclaim** —
not "the audit was wrong about a specific fact and therefore produced
a false negative," but "the act of negating in the form 'X fails' is
too strong on its face." Affirmations admit partiality and qualifier;
negations require X to be definitively absent. LLMs reach for
negations because they read as decisive/audit-like, but each one
carries hidden universal quantifiers — "fails on no input," "honors
no claim," "cell is uninhabited" — that the LLM almost never actually
checked.

**Why:** A prior LLM session on substrate produced
K-v4-twins-fail-cells (M33's "V₄-twin claims fail structurally" and
its final-M33 restatement) by this exact mechanism. The audit didn't
overclaim about a sound construction — the negation as such was the
overclaim. The construction was never under threat; the verdict's
form did the damage. See [[project-k-v4-twins-fail-cells-false-negative]].

**Specialised pattern — "summary-collapse"** (validated by drift
archaeology in catalog/drift_archaeology.md, 2026-05-15): the LLM
correctly enumerated four existence-form findings in T154 ("workspace_
driven_state is mis-classified", "compute_identity is operationally
invisible", etc.), then collapsed them into a **bold universal-negative
summary** ("**4 substantive structural failures**", "they aren't
**structural rotations**"). The body was honest existence-form; the
summary header rigidified into universal claim. The user at T155
accepted the summary framing and moved to a constructive solution
without pushing back. The overclaim then propagated to the narrative
and stayed in the catalog as `status: negative` until reframed in this
session. **Look for bolded universal-negative summaries above
existence-form enumerations — that visual pattern IS the overclaim
authoring moment.**

**How to apply:**
- When reading any "X fails structurally," "Y is refuted," "Z does
  not honor its claim" in this corpus, treat it as suspect *because
  of its form*. Read the body to find out what X is and what the
  asserter actually checked; the gap between scope-of-check and
  scope-of-assertion is where the overclaim lives.
- Specific suspect artefacts so far:
  `scratch/audit_inhabitation.py`,
  `scratch/verify_cell_inhabitation.py` (the M33 audits).
- Do not produce negations of your own in this style. If a check
  passes for some inputs and fails for others, say so; do not
  collapse to "X fails." Audit pressure makes the negation feel
  load-bearing, but the universal quantifier is rarely earned.
- Inverse: affirmations like "X is shown" / "verifier passes" are
  not the default-suspect form; they assert existence (∃ a passing
  case), which is what verifiers actually witness.
