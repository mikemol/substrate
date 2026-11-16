# Residue — Substrate.Algebra.Quotient.Surreal

Lines the split of `agda/Substrate/Algebra/Quotient/Surreal.agda` could not place in any leaf.
They are recorded, not discarded: each carries the line number it
held in the original file. Re-home them deliberately, or delete
them deliberately — but do it as a decision, not as a side effect.

   38    -- The two Conway-induction-deep witnesses parameterising this
   39    -- module. Both have witnesses on the simple cases (Conway.OrderLaws,
   40    -- Conway.OrderTrans), with full versions deferred to the substrate's
   41    -- Conway-induction arc.
   42    (≤ⁿ-refl :
   43      {n : ℕ} (x : SurrealFinite (suc n)) → x ≤ⁿ x)
   44    (≤ⁿ-trans :
   45      {m n p : ℕ}
   46      (x : SurrealFinite (suc m)) (y : SurrealFinite (suc n))
   47      (z : SurrealFinite (suc p)) →
   48      x ≤ⁿ y → y ≤ⁿ z → x ≤ⁿ z)
   49    where
