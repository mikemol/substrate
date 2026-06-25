------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetV4
--
-- HetQ × V₄ — the cross-equality `_≈H_` of HetBasis is INVARIANT under the Klein
-- four-group, promoting "cross-multiplication is a Klein rotation" (Wedge.StarV4)
-- from the arrangement level to a theorem about the HetQ equivalence ITSELF.
--
-- `p ≈H q = (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p)` is the 2×2 ((a,b),(c,d))
-- whose diagonals a⊗d and c⊗b cross-multiplication compares. The V₄ = ⟨rowSwap,
-- recip⟩ ≅ ℤ/2 × ℤ/2 acting on that square:
--   • rowSwap  (swap the two fractions p,q)   — preserves ≈H by `≈H-sym`.
--   • recip    (num ↔ den, the reciprocal)    — preserves ≈H given a COMMUTATIVE
--     cross ⊗ (this is the user's HetQ ↔ ℤ/2 duality: recip is HetQ's intrinsic
--     num/den ℤ/2). The fourth element (the klein-rot 180°) = rowSwap ∘ recip.
--
-- So the cross-equality is V₄-equivariant: cross-multiplication IS a Klein
-- rotation, on HetQ proper. `recip` here is the HetQ realization of
-- Wedge.StarV4.recip; the central rotation is Wedge.StarV4.klein-rot.
--
-- SCOPE: the HOMOGENEOUS quotient (num, den in one basis A), where recip is an
-- endo. The genuinely-heterogeneous ℚ = HetQ ℤ ℕ has a CROSS-BASIS reciprocal
-- (ℤ ↔ ℕ), which needs the basis bridge — the named next step.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetV4 where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Q.HetBasis using (HetQ; hnum; hden; module CrossEq)

module _
  {A R : Set}
  (_⊗_     : A → A → R)
  (_≈R_    : R → R → Set)
  (≈R-refl  : {x : R} → x ≈R x)
  (≈R-sym   : {x y : R} → x ≈R y → y ≈R x)
  (≈R-trans : {x y z : R} → x ≈R y → y ≈R z → x ≈R z)
  (⊗-comm   : (x y : A) → (x ⊗ y) ≈R (y ⊗ x))
  where

  open CrossEq {A} {A} {R} _⊗_ _≈R_ ≈R-refl ≈R-sym  -- _≈H_, ≈H-refl, ≈H-sym

  ------------------------------------------------------------------------
  -- recip: the num ↔ den reciprocal (the HetQ ℤ/2 duality), an involution.
  ------------------------------------------------------------------------

  recip : HetQ A A → HetQ A A
  recip h = record { hnum = hden h ; hden = hnum h }

  recip-recip : (h : HetQ A A) → recip (recip h) ≡ h
  recip-recip h = refl

  ------------------------------------------------------------------------
  -- The two V₄ generators preserve the cross-equality.
  ------------------------------------------------------------------------

  -- rowSwap: swap the two fractions (= ≈H-sym).
  ≈H-rowSwap : {p q : HetQ A A} → p ≈H q → q ≈H p
  ≈H-rowSwap = ≈H-sym

  -- recip: reciprocate both — preserves ≈H BECAUSE the cross ⊗ commutes.
  -- goal (hden p ⊗ hnum q) ≈R (hden q ⊗ hnum p), from e : (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p).
  ≈H-recip : (p q : HetQ A A) → p ≈H q → (recip p) ≈H (recip q)
  ≈H-recip p q e =
    ≈R-trans (⊗-comm (hden p) (hnum q))
             (≈R-trans (≈R-sym e) (⊗-comm (hnum p) (hden q)))

  -- the central Klein rotation (180° = rowSwap ∘ recip) preserves ≈H.
  ≈H-klein : (p q : HetQ A A) → p ≈H q → (recip q) ≈H (recip p)
  ≈H-klein p q e = ≈H-sym (≈H-recip p q e)
