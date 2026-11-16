---
name: feedback-two-path-commutativity
description: "When parametrizing along one axis (e.g., anchor) but enumerating along another (e.g., orbit-key), the two-path structure is the rigidification — collapse both paths through the generator, not just one."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When refactoring a structure with multiple "directions" (e.g., `(anchor, orbit-key) → Permutation`), making ONE direction parametric while leaving the other hand-enumerated leaves a hidden 2-path. The 2-path commutativity is the "did we really remove the privilege?" test.

**Why:** in the substrate Agda refactor, slice 14 made `Stab anchor` fully parametric (anchor-direction parametric), while the cocycle's 6 canonical Stab(D) representatives (`stab-id`, `stab-sw`, `stab-cs`, etc.) remained hand-enumerated as D-specific records. When I proposed "keep the 6 records, add bridges connecting them to `extend D s3-X`", the user pointed out this still privileges D — it observes the equivalence as a pointwise bridge, but doesn't collapse the duplication. The orbit-key direction was NOT anchor-parametric; the bridges merely papered over that fact. Naming like "stab-sw" reads C and S relative to D, which is the residual chirality leakage.

**How to apply:**
- When a structure has axes (parametric_axis × enumerated_axis), check whether the enumerated axis can also be parametrized through the generator (here: `extend anchor s` for s : SFin.Permutation 3). If yes, the named instances are orbit elements of that generator and should be collapsed.
- The square test: draw the commutative diagram (named-instances vs anchor-parametric-form, on both axes). If two corners require independent definitions, you have a 2-path — and probably haven't actually removed the privilege you thought you were removing.
- Bridges proving "named X = extend anchor s_X pointwise" are NOT the fix; they're documentation of the redundancy. The fix is to make the named instances DEFINITIONS via the parametric form, deleting the hand-coded versions.
- Sister to [[feedback-expose-generator-not-orbit]]: that rule is the 1D form ("don't enumerate orbit elements when you can use the generator"); this is the 2D refinement ("don't parametrize one axis while enumerating the other — collapse both through the generator").
- When the user asks "is this commutative? is there a 2-path we're not acknowledging?", take it seriously — it's a structural correctness question, not a stylistic one.
