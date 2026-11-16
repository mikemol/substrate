# `Grade` — ⊙.grade: the two gradings on the F₂ⁿ index (C4) and the cancellation defect (C2)

The F₂ⁿ basis index carries TWO product structures:

- the **CD/Morton** product multiplies indices by **XOR** (`i ⊕ j`) — the F₂ⁿ group /
  Z-order grading (`CayleyDickson.Cocycle`, `zipWith _xor_`);
- the **ANF / Reed-Muller monomial** product multiplies them by **OR** / set-union
  (`i ∨ j`, since xᵢ² = xᵢ) — the `Category.ReedMullerHierarchy` degree grading.

**C4 — do the two gradings coincide?** They do NOT; they are BRIDGED.

- at the INDEX level by `OR = XOR ⊕ AND` (`OrAnf`): the union product is the XOR
  product corrected by the AND overlap;
- at the DEGREE level by `popcount` (Hamming weight = ANF degree), via
  inclusion-exclusion (`BitOrAnd`, `PopcountOrAnd`).

**C2 — graded-GF(2) is non-cancelling.** The overlap `popcount (i ∧ j)` is EXACTLY
the cancellation defect: the degree grading is additive (non-cancelling) iff the
supports are disjoint (`i ∧ j = 0`). In the full F₂ⁿ index (graded) the overlap is
RETAINED; only the popcount projection (ungraded) loses it — *cancellation is
ungraded-projection-only*.

**The two gradings, named.** `F2LengthGrading` is the generic `Wedge.VecGraded`
length-grade at Bool (the dimension); `Popcount` is the orthogonal content-grade
(the weight, ≤ length) on the SAME carrier — `IndexCarrier` is that identity.
