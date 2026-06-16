------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape.Double.Interned
--
-- THE ARC CLOSES — the shape-indexed double category run over the interned
-- register. A vertical morphism is a correspondence `Corr t₁ t₂ = shape t₁ ≡
-- shape t₂` (Shape.Double); on a faithful (NoDupᴿ) register where both shapes
-- are interned, that correspondence IS equality of ADDRESSES:
--
--   corr→addr : Corr t₁ t₂ → idx p₁ ≡ idx p₂      (via idx-cong, ⟹)
--   addr→corr : idx p₁ ≡ idx p₂ → Corr t₁ t₂      (via idx-inj, ⟸)
--
-- So the interior reading (a correspondence = equal shapes) and the exterior
-- reading (a correspondence = equal addresses, an O(1) index compare) are the
-- same relation — `idx-inj`/`idx-cong` are the seam. The double category, its
-- twist (companion/conjoint), and the SPPF heap are now one object: a
-- correspondence is "same address," interned once and compared by pointer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape.Double.Interned where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Wedge using (Trace; ℕ-div)
open import Substrate.Algebra.Wedge.Shape using (shape)
open import Substrate.Algebra.Wedge.Shape.Double using (Corr)
open import Substrate.Algebra.Wedge.Shape.Register using (Register; _∈ᴿ_; idx; idx-inj)
open import Substrate.Algebra.Wedge.Shape.Register.Properties using (NoDupᴿ; idx-cong)

-- (At ℕ-div, where the Register lives — its shapes are the ℕ quotient sequences;
-- Corr is the same-carrier correspondence.)

-- (⟹) a correspondence forces equal addresses (needs the faithful heap).
corr→addr : {a₁ b₁ g₁ a₂ b₂ g₂ : ℕ}
            {t₁ : Trace ℕ-div a₁ b₁ g₁} {t₂ : Trace ℕ-div a₂ b₂ g₂} {reg : Register} →
            NoDupᴿ reg →
            (p₁ : shape t₁ ∈ᴿ reg) (p₂ : shape t₂ ∈ᴿ reg) →
            Corr t₁ t₂ → idx p₁ ≡ idx p₂
corr→addr nd p₁ p₂ c = idx-cong nd c p₁ p₂

-- (⟸) equal addresses force a correspondence (sound on any register).
addr→corr : {a₁ b₁ g₁ a₂ b₂ g₂ : ℕ}
            {t₁ : Trace ℕ-div a₁ b₁ g₁} {t₂ : Trace ℕ-div a₂ b₂ g₂} {reg : Register} →
            (p₁ : shape t₁ ∈ᴿ reg) (p₂ : shape t₂ ∈ᴿ reg) →
            idx p₁ ≡ idx p₂ → Corr t₁ t₂
addr→corr p₁ p₂ e = idx-inj p₁ p₂ e
