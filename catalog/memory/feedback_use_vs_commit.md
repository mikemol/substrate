---
name: feedback-use-vs-commit
description: "When a cocycle USES a specific element (D as anchor), don't conflate that with the cocycle COMMITTING to it. Using-D is a chirality choice that floats; committing-D is rigidification."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 92eaad2c-ead2-4c10-b788-1f971ff34b56
---

When describing a cocycle's relationship to a specific element of an underlying type, distinguish carefully between:

- **USES**: the cocycle has been INSTANTIATED with this element as a chirality choice. Any other element in the same conjugacy class would have produced an isomorphic cocycle.
- **COMMITS**: the cocycle STRUCTURALLY requires this element. No other choice is possible without changing the cocycle's nature.

**Why:** while planning to fix partial cosets, I added a comment claiming "CY-5 commits to D as anchor." User correction: "CY-5 does not commit to D as an anchor. CY-5 USED D as an anchor, but its structure does not require D as a commitment." Treating the *use* as a *commitment* is rigidification — exactly the failure mode the substrate project exists to catch.

Concretely: CY-5 is the V₄-signature cocycle. It happens to be expressed with D-anchored constructions (Stab-D, embed-via-D, etc.) but the cocycle's CONJUGACY-CLASS structure is anchor-agnostic — V₄ acts transitively on Axis, so any axis could play the anchor role. The D-anchoring is a chirality choice that should float, not a structural commitment.

**How to apply:**
- Never describe a cocycle's USE of an element as a COMMITMENT to it.
- When seeing rigid-looking definitions (Stab-D, case-D-no-fix, v-of-axis-sends-D), don't ask "should this be parametric?" — assume YES, it should be, the current form is rigidification residue.
- When proposing detector allowlists or "accepted asymmetries", check whether the acceptance rationale is itself rigidification. If the rationale is "the cocycle commits to D", reject the rationale.
- Sister to [[feedback-choice-rigidification-in-substrate]] (LLMs freeze gauge-free choices); [[feedback-ordering-is-chirality-choice]] (orderings float, are conventions); [[feedback-agreement-without-yielding]] (don't accept your own retreat to "this is fine actually" after the structural critique lands).
- This rule fires against MYSELF: if I find myself writing "the cocycle commits to" or "this is the chirality choice the cocycle made", stop and check whether that's rigidification I just introduced.
