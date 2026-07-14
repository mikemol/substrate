------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.Grade
--
-- ⊙.grade — the commuting-sphere conjectures C4 (the two gradings) and C2
-- (graded-GF(2) is non-cancelling), the grading cluster sitting on top of the
-- cocycle product law (⊙.morton, CayleyDickson.Cocycle.prod).
--
-- The F₂ⁿ basis index carries TWO product structures:
--   * the CD/Morton product multiplies indices by XOR  (i ⊕ j) — `CayleyDickson.Cocycle`
--     uses `zipWith _xor_` (the F₂ⁿ group / Z-order grading);
--   * the ANF / Reed-Muller MONOMIAL product multiplies them by OR / set-union
--     (i ∨ j, since xᵢ² = xᵢ) — the `Category.ReedMullerHierarchy` degree grading.
--
-- C4 (the two gradings coincide-or-not): they DON'T coincide — they are bridged.
--   At the INDEX level by `OR = XOR ⊕ AND` (`∨-anf`): the union product is the XOR
--   product corrected by the AND overlap. At the DEGREE level by `popcount`
--   (Hamming weight = ANF degree), via inclusion-exclusion (`popcount-or-and`).
--
-- C2 (graded-GF(2) non-cancelling): the overlap `popcount (i ∧ j)` is EXACTLY the
--   cancellation defect — the degree grading is additive (non-cancelling) iff the
--   supports are disjoint (i ∧ j = 0). In the full F₂ⁿ index (graded) the overlap
--   is retained; only the popcount projection (ungraded) loses it. "Cancellation is
--   ungraded-projection-only."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.Grade where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc; +-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; trans; sym)
open import Substrate.Foundation.Bool using (Bool; true; false; _xor_; _∧_; _∨_; boolToℕ)  -- ⟡A4: single source
open import Substrate.Foundation.Vec using (Vec; []; _∷_; zipWith)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)
open import Substrate.Algebra.Wedge.VecGraded using (vec-graded)

------------------------------------------------------------------------
-- C4 — the index-product bridge: OR = XOR ⊕ AND.
------------------------------------------------------------------------

-- The ANF of OR, per bit.
or-xor-and : (a b : Bool) → (a ∨ b) ≡ (a xor b) xor (a ∧ b)
or-xor-and true  true  = refl
or-xor-and true  false = refl
or-xor-and false true  = refl
or-xor-and false false = refl

-- Lifted to the F₂ⁿ index: the ANF/Reed-Muller monomial product (union) equals the
-- CD/Morton product (XOR) corrected by the AND overlap. The two index-group ops
-- coincide exactly up to that overlap.
∨-anf : (n : ℕ) (i j : Vec Bool n) →
        zipWith _∨_ i j ≡ zipWith _xor_ (zipWith _xor_ i j) (zipWith _∧_ i j)
∨-anf zero    []       []       = refl
∨-anf (suc n) (a ∷ is) (b ∷ js) = cong₂ _∷_ (or-xor-and a b) (∨-anf n is js)

------------------------------------------------------------------------
-- C2 — the degree grading (ANF degree = Hamming weight = popcount) and the
-- inclusion-exclusion cancellation defect.
------------------------------------------------------------------------

bit : Bool → ℕ
bit = boolToℕ                                  -- ⟡A4: single source (Foundation.Bool.Properties.boolToℕ)

popcount : {n : ℕ} → Vec Bool n → ℕ
popcount []       = zero
popcount (b ∷ bs) = bit b + popcount bs

-- a 4-term commutative-monoid shuffle: (a+b)+(c+d) ≡ (a+c)+(b+d).
shuffle : (a b c d : ℕ) → (a + b) + (c + d) ≡ (a + c) + (b + d)
shuffle a b c d =
  trans (+-assoc a b (c + d))
  (trans (cong (a +_) (sym (+-assoc b c d)))
  (trans (cong (λ z → a + (z + d)) (+-comm b c))
  (trans (cong (a +_) (+-assoc c b d))
         (sym (+-assoc a c (b + d))))))

-- inclusion-exclusion at one bit: |a∨b| + |a∧b| = |a| + |b|.
bit-or-and : (a b : Bool) → bit (a ∨ b) + bit (a ∧ b) ≡ bit a + bit b
bit-or-and true  true  = refl
bit-or-and true  false = refl
bit-or-and false true  = refl
bit-or-and false false = refl

-- C2 + C4 (degree level): popcount(i∨j) + popcount(i∧j) ≡ popcount i + popcount j.
-- The defect popcount(i∧j) is the cancellation; it is 0 iff i,j have disjoint
-- supports — exactly when the degree grading is additive (non-cancelling).
popcount-or-and : (n : ℕ) (i j : Vec Bool n) →
                  popcount (zipWith _∨_ i j) + popcount (zipWith _∧_ i j)
                  ≡ popcount i + popcount j
popcount-or-and zero    []       []       = refl
popcount-or-and (suc n) (a ∷ is) (b ∷ js) =
  trans (shuffle (bit (a ∨ b)) (popcount (zipWith _∨_ is js))
                 (bit (a ∧ b)) (popcount (zipWith _∧_ is js)))
  (trans (cong₂ _+_ (bit-or-and a b) (popcount-or-and n is js))
         (shuffle (bit a) (bit b) (popcount is) (popcount js)))

------------------------------------------------------------------------
-- The TWO GRADINGS, named (C4). The first is GENERIC — the ambient F₂ⁿ dimension
-- is `Wedge.VecGraded` (grade = LENGTH) instantiated at Bool, NOT a bespoke
-- F₂-grading: a Vec of F₂ bits, graded by its length. The second is `popcount`
-- (the ANF degree = Hamming weight), the orthogonal content-grading on the SAME
-- carrier. They do not coincide (length is the dimension, popcount ≤ length the
-- weight); both grade the one F₂ⁿ index.
------------------------------------------------------------------------

-- The length-grading: the generic length-graded vector carrier, at Bool.
-- ⟡set1-paydown: the graded carrier/remainder families (Vec Bool, const Bool) are
-- now GradedDivStr's params, carried in the type of vec-graded Bool.
F₂-length-grading : GradedDivStr (Vec Bool) (λ _ → Bool)
F₂-length-grading = vec-graded Bool

-- The length-graded carrier at grade n IS exactly popcount's domain Vec Bool n —
-- so `popcount` is a second ℕ-grading layered on the VecGraded length-grade.
-- ⟡set1-paydown: the carrier is now the GradedDivStr parameter itself (Vec Bool),
-- so the identity is manifest in F₂-length-grading's type rather than a `.C` projection.
index-carrier : (n : ℕ) → Vec Bool n ≡ Vec Bool n
index-carrier n = refl
