------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetReciprocal
--
-- THE HETEROGENEOUS RECIPROCAL — extends Q.HetV4 from the homogeneous HetQ A A
-- (where recip is an endo) to the genuinely cross-basis HetQ A B (e.g. ℚ =
-- HetQ ℤ ℕ, num in ℤ, den in ℕ).
--
-- KEY: the reciprocal does NOT need sign-normalization. It swaps num ↔ den
-- ACROSS the bases, landing in the TRANSPOSED quotient: recip : HetQ A B →
-- HetQ B A. (For ℚ: HetQ ℤ ℕ → HetQ ℕ ℤ — the denominator becomes a ℕ-numerator
-- and the numerator becomes a possibly-negative ℤ-denominator; no |·| needed,
-- because HetQ B A genuinely allows a ℤ denominator.)
--
-- THE BRIDGE is one law: a TRANSPOSE law `T : (a ⊗ b) ≈R (b ⊗ᵀ a)` relating the
-- forward cross ⊗ : A → B → R and the transposed cross ⊗ᵀ : B → A → R. This is
-- the ℤ↔ℕ basis bridge made into the only hypothesis: for ℚ = HetQ ℤ ℕ it is
-- `a *ℤ (ℕ↪ℤ b) ≡ (ℕ↪ℤ b) *ℤ a` = *ℤ-commutativity. With it, the cross-equality
-- is preserved by the cross-basis reciprocal (`≈H-recip`).
--
-- Specializes to Q.HetV4 (the homogeneous V₄'s `recip`) when A = B, ⊗ = ⊗ᵀ, and
-- T = ⊗-comm. So this is the heterogeneous arm of "cross-multiplication is a
-- Klein rotation": recip is the ℤ/2 num↔den swap, now across bases.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetReciprocal where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Z using (ℤ; +_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (*ℤ-comm)
open import Substrate.Algebra.Q.HetBasis using (HetQ; hnum; hden; module CrossEq)

module Cross
  {A B R : Set}
  (_⊗_  : A → B → R)
  (_⊗ᵀ_ : B → A → R)
  (_≈R_     : R → R → Set)
  (≈R-refl  : {x : R} → x ≈R x)
  (≈R-sym   : {x y : R} → x ≈R y → y ≈R x)
  (≈R-trans : {x y z : R} → x ≈R y → y ≈R z → x ≈R z)
  -- THE BRIDGE: the forward and transposed crosses agree under transposition.
  (T : (a : A) (b : B) → (a ⊗ b) ≈R (b ⊗ᵀ a))
  where

  open CrossEq {A} {B} {R} _⊗_  _≈R_ ≈R-refl ≈R-sym
    renaming (_≈H_ to _≈AB_)
  open CrossEq {B} {A} {R} _⊗ᵀ_ _≈R_ ≈R-refl ≈R-sym
    renaming (_≈H_ to _≈BA_; ≈H-sym to ≈BA-sym)

  ------------------------------------------------------------------------
  -- The cross-basis reciprocal and its transpose; they invert (eta).
  ------------------------------------------------------------------------

  recip : HetQ A B → HetQ B A
  recip h = record { hnum = hden h ; hden = hnum h }

  recipᵀ : HetQ B A → HetQ A B
  recipᵀ h = record { hnum = hden h ; hden = hnum h }

  recip-recip : (h : HetQ A B) → recipᵀ (recip h) ≡ h
  recip-recip h = refl

  ------------------------------------------------------------------------
  -- The reciprocal preserves the cross-equality (across the basis swap),
  -- using only the transpose bridge law T (+ the carrier's ≈R laws).
  --   from  e : (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p)   [p ≈AB q]
  --   show     (hden p ⊗ᵀ hnum q) ≈R (hden q ⊗ᵀ hnum p)  [recip p ≈BA recip q]
  ------------------------------------------------------------------------

  ≈H-recip : (p q : HetQ A B) → p ≈AB q → (recip p) ≈BA (recip q)
  ≈H-recip p q e =
    ≈R-trans (≈R-sym (T (hnum q) (hden p)))
             (≈R-trans (≈R-sym e) (T (hnum p) (hden q)))

  -- the cross-basis Klein rotation (recip + swap of the two fractions).
  ≈H-klein : (p q : HetQ A B) → p ≈AB q → (recip q) ≈BA (recip p)
  ≈H-klein p q e = ≈BA-sym (≈H-recip p q e)

------------------------------------------------------------------------
-- The concrete ℚ instance: ℚ = HetQ ℤ ℕ. The ℤ↔ℕ basis bridge IS *ℤ-comm.
-- recip : HetQ ℤ ℕ → HetQ ℕ ℤ — the rational reciprocal across bases (the
-- ℤ-numerator becomes a ℤ-denominator in the transposed quotient; no |·|).
------------------------------------------------------------------------

module ℤℕ where
  _⊗_ : ℤ → ℕ → ℤ
  a ⊗ b = a *ℤ (+ b)

  _⊗ᵀ_ : ℕ → ℤ → ℤ
  b ⊗ᵀ a = (+ b) *ℤ a

  bridge : (a : ℤ) (b : ℕ) → (a ⊗ b) ≡ (b ⊗ᵀ a)
  bridge a b = *ℤ-comm a (+ b)

  open Cross _⊗_ _⊗ᵀ_ _≡_ refl sym trans bridge public
  -- exports: recip : HetQ ℤ ℕ → HetQ ℕ ℤ, recipᵀ, recip-recip, ≈H-recip, ≈H-klein.
