---
name: project-k-v4-twins-fail-cells-false-negative
description: "K-v4-twins-fail-cells in catalog/claims.md is not a \"false negative due to a specific audit error\" — the negation itself is the overclaim. The verdict's form does the damage, independent of any factual gap in the audit body."
metadata: 
  node_type: memory
  type: project
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

In [catalog/claims.md](/home/mikemol/github/substrate/catalog/claims.md),
K-v4-twins-fail-cells is recorded as status `negative`, sourced from
M33 ([cotype-free-self-extending-grammar.md:3653-3782]) and the final
M33 ([cotype-free-self-extending-grammar.md:8029-8157]), backed by
[scratch/audit_inhabitation.py] and [scratch/verify_cell_inhabitation.py].

**Status correction (from the user, 2026-05-15):** the negation IS
the overclaim. Not "the audit was wrong about something specific,
producing a false negative" — the form "V₄-twin claims fail
structurally" / "implementations don't honor their claimed V₄ cells"
is too strong on its face. The universal quantifier the negation
encodes ("no inhabitant," "no honor," "fails on every input") was
never actually checked. The V₄-twin construction is sound because no
negation in that form was ever warranted.

**Why:** This re-framing matters for how the catalog is read and how
future sessions handle similar findings. Treating the issue as "audit
got a specific fact wrong" invites "fix the audit and re-run";
treating it as "the negation form was the overclaim" forbids that
move entirely — the next step is to restate any actual findings in
existence-form ("on input X, property P holds; on input Y, P does
not hold; here is what the construction commits to and what it
doesn't"), not to keep the universal-quantifier verdict and patch the
witness.

**How to apply:**
- Do not treat K-v4-twins-fail-cells as a refutation of
  K-F-populated or any K-V4-twins claim.
- If asked to "address the open finding," the correct response is to
  restate whatever the audit actually checked in existence-form, and
  drop the universal-form negation. Do not patch the construction
  unless an existence-form failure (on a specific input or cell)
  is exhibited.
- The catalog's status field is still `negative`. Pending user
  direction on whether to mark as `disputed-by-form` or similar; see
  pending question raised in the catalog update conversation.
- The general epistemic pattern is captured in
  [[feedback-negative-findings-in-corpus]].
