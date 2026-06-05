------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Contextuality.CochainCombine
--
-- Bridging `General.combine` (the selection-fold over a cover) to the
-- `Cochain` group: scaling by 𝟘/𝟙 is drop/keep, the empty combination is the
-- zero cochain, and cons unfolds to a `⊕ᶜ`. So the obstruction is a genuine
-- cochain sum, and it is the NONZERO class (≠ 𝟬ᶜ).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Contextuality.CochainCombine where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2 using (𝟘; 𝟙; 𝟙≢𝟘)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.Wedge.Contextuality using (Constraint; con; rhs; _⊕ᶜ_)
open import Substrate.Algebra.Wedge.Contextuality.General using (combine; scaleᶜ)
open import Substrate.Algebra.Wedge.Contextuality.Cochain using (𝟬ᶜ; ⊕ᶜ-identityˡ)

------------------------------------------------------------------------
-- 29–31. The empty combination is 𝟬ᶜ; scaling is keep (𝟙) / drop-to-𝟬ᶜ (𝟘).
------------------------------------------------------------------------

combine-[] : combine {0} [] [] ≡ 𝟬ᶜ
combine-[] = refl

scaleᶜ-𝟙 : ∀ {n} (c : Constraint n) → scaleᶜ 𝟙 c ≡ c
scaleᶜ-𝟙 c = refl

scaleᶜ-𝟘 : ∀ {n} (c : Constraint n) → scaleᶜ 𝟘 c ≡ 𝟬ᶜ
scaleᶜ-𝟘 c = refl

------------------------------------------------------------------------
-- 32–33. Cons of the fold: 𝟙 keeps (a ⊕ᶜ), 𝟘 drops (the tail).
------------------------------------------------------------------------

combine-cons-𝟙 : ∀ {n m} (c : Constraint n) (cs : Vec (Constraint n) m) (sel : Vector m) →
                 combine (c ∷ cs) (𝟙 ∷ sel) ≡ (c ⊕ᶜ combine cs sel)
combine-cons-𝟙 c cs sel = refl

combine-cons-𝟘 : ∀ {n m} (c : Constraint n) (cs : Vec (Constraint n) m) (sel : Vector m) →
                 combine (c ∷ cs) (𝟘 ∷ sel) ≡ combine cs sel
combine-cons-𝟘 c cs sel = ⊕ᶜ-identityˡ (combine cs sel)

------------------------------------------------------------------------
-- 34. The obstruction cochain (𝟎ⱽ, 𝟙) is the NONZERO class.
------------------------------------------------------------------------

obstruction-ne-𝟬ᶜ : ∀ {n} → ¬ (con (𝟎ⱽ {n}) 𝟙 ≡ 𝟬ᶜ)
obstruction-ne-𝟬ᶜ eq = 𝟙≢𝟘 (cong rhs eq)
