---
name: chirality-pair-completeness
description: "When one half of a Left/Right (or Forward/Backward, In/Out) chirality pair is named, the other half must exist too. A solo \"-right\" or \"-left\" lemma is a rigidification flag."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d49d2868-8ade-4add-9d72-b31958685ef0
---

A name like `normalize-cong-right`, `append-right`, `foo-forward` carries a chirality marker. That marker only makes sense if its mirror also exists. A solo "-right" suffix is a sign that the gauge-free choice between the two halves was frozen into the lemma surface — usually because only one half was needed by the immediate downstream consumer, and the other was never reached for.

This pattern shows up across the substrate (Coxeter.Core had `NormalizeAppend.{Left,Right}` as a pair but `NormalizeCongRight` as a solo). The fix is mechanical: the mirror lemma follows the same skeleton, swapping the role of the two operands and using the mirror helper from one layer down.

**Why:** Solo chirality markers hide structural symmetry from the similarity checker and from human readers. They also forecast where a future downstream consumer will hit a wall and re-derive the missing half locally (LLM-flavoured choice-rigidification, per [[feedback-choice-rigidification-in-substrate]]). Completing the pair preemptively eliminates the wall.

**How to apply:**
- When touching a file, scan for chirality-marked names (`*-left`, `*-right`, `*-forward`, `*-backward`, `*-in`, `*-out`, `*-fst`, `*-snd`). If the named half is present but the mirror is absent, that is a flag.
- The mirror's body is almost always derivable by swapping operand roles + substituting the mirror helper from the dependency layer.
- Restructure: rename the section/directory to drop the chirality suffix and add both halves as siblings. E.g. `NormalizeCongRight` → `NormalizeCong/{Left, Right}`.
- Do not preemptively complete chirality pairs you haven't run into. The rule is *when touching* — scan only the file you're already in.

See also: [[feedback-ordering-is-chirality-choice]] (same idea at the algebra/cocycle layer), [[feedback-choice-rigidification-in-substrate]] (the LLM failure mode this guards against), [[feedback-section-then-lemma-for-parametric]] (the file-per-lemma pass that makes chirality asymmetries visible at the file boundary).
