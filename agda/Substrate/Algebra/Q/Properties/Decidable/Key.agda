------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Decidable.Key
--
-- The shape key: the interned CF of |num|/den.  `ℕ-shape` ignores the gcd
-- index, so transporting it (coprime-trace = subst on gcd-trace) does not
-- change the shape — that is `subst-shape`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Decidable.Key where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; subst)
open import Substrate.Algebra.Q using (ℚ; num; denominator)
open import Substrate.Algebra.Q.Reduction using (abs-ℤ)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)
open import Substrate.Algebra.Wedge using (ℕ-div)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape; WedgeShape)

-- ⟡cap-128-forcing: `q-key` is SEALED.  Unsealed, a `with q-key (reduce a) ≟ˢ
-- q-key (reduce b)` scrutinee drags the whole EEA/shape-interning stack into
-- the elaborator (>128MB heap).  Opaque makes it a non-reducing HANDLE, so the
-- decision procedure elaborates against the handle; the files that genuinely
-- need it to COMPUTE (Faithful, Fires) say `unfolding q-key` explicitly.
opaque
  q-key : ℚ → WedgeShape ℕ-div
  q-key q = ℕ-shape (gcd-trace (abs-ℤ (num q)) (denominator q))

subst-shape : {a b g g′ : ℕ} (eq : g ≡ g′) (t : EEATrace a b g) →
              ℕ-shape (subst (EEATrace a b) eq t) ≡ ℕ-shape t
subst-shape refl t = refl
