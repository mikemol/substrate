------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Tail
--
-- The SECOND HALF of the grade-4 completeness dispatch: e12 … e23.
--
-- ⟡cap-128-forcing: the 24-way `AllAdjGen4` was ONE right-nested ⊎, so each of
-- the 24 clauses matched an `inj₂` chain up to 23 deep and the elaboration was
-- QUADRATIC in the nesting — 156MB in a single unit, over the cap. Halving the
-- dispatch quarters that cost per unit: this module owns e12…e23 and the parent
-- owns e0…e11, delegating the tail to `coxeter-complete-tail`. The theorem is
-- unchanged; only the elaboration unit is split.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Tail where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Elements

-- e12 … e23 as a 12-way nested ⊎ (same right-nesting as the parent's).
AllAdjGen4-tail : Perm 4 → Set
AllAdjGen4-tail σ = (σ ≡ e12) ⊎ ((σ ≡ e13) ⊎ ((σ ≡ e14) ⊎ ((σ ≡ e15) ⊎ ((σ ≡ e16) ⊎ ((σ ≡ e17) ⊎ ((σ ≡ e18) ⊎ ((σ ≡ e19) ⊎ ((σ ≡ e20) ⊎ ((σ ≡ e21) ⊎ ((σ ≡ e22) ⊎ ((σ ≡ e23))))))))))))

coxeter-complete-tail : {σ : Perm 4} → AllAdjGen4-tail σ → AdjGen4 σ
coxeter-complete-tail (inj₁ refl) = orbit-12
coxeter-complete-tail (inj₂ (inj₁ refl)) = orbit-13
coxeter-complete-tail (inj₂ (inj₂ (inj₁ refl))) = orbit-14
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = orbit-15
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))) = orbit-16
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))) = orbit-17
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))) = orbit-18
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))))) = orbit-19
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))))) = orbit-20
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))))))) = orbit-21
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))))))) = orbit-22
coxeter-complete-tail (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ refl))))))))))) = orbit-23
