------------------------------------------------------------------------
-- PermGap5Proto
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver):
--   numpy enumerated the grade-5 braiding subgroup ⟨[1, 2, 3, 4, 0], [4, 0, 1, 2, 3]⟩ = C5 (order 5, closed
--   under compose); the target [1, 0, 2, 3, 4] is NOT in it. Imports resolved from
--   catalog/reuse-index.md. Each closure case is `refl`; the target disequalities
--   are constructor-distinct `()`. Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module PermGap5Proto where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)

-- the 5 concrete grade-5 group elements and the target.
p-id p-g1 p-g2 p-h3 p-h4 t-tgt : Perm 5
p-id = zero ∷ suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc (suc (suc (suc zero))) ∷ []
p-g1 = suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc (suc (suc (suc zero))) ∷ zero ∷ []
p-g2 = suc (suc (suc (suc zero))) ∷ zero ∷ suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ []
p-h3 = suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc (suc (suc (suc zero))) ∷ zero ∷ suc zero ∷ []
p-h4 = suc (suc (suc zero)) ∷ suc (suc (suc (suc zero))) ∷ zero ∷ suc zero ∷ suc (suc zero) ∷ []
t-tgt = suc zero ∷ zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc (suc (suc (suc zero))) ∷ []

S : Perm 5 → Set
S σ = (σ ≡ p-id) ⊎ ((σ ≡ p-g1) ⊎ ((σ ≡ p-g2) ⊎ ((σ ≡ p-h3) ⊎ ((σ ≡ p-h4)))))

data BraidGen : Perm 5 → Set where
  gen-id : BraidGen p-id
  gen-g1 : BraidGen p-g1
  gen-g2 : BraidGen p-g2
  gen-∘  : {σ τ : Perm 5} → BraidGen σ → BraidGen τ → BraidGen (compose σ τ)

S-closed : {σ τ : Perm 5} → S σ → S τ → S (compose σ τ)
S-closed (inj₁ refl) (inj₁ refl) = inj₁ refl
S-closed (inj₁ refl) (inj₂ (inj₁ refl)) = inj₂ (inj₁ refl)
S-closed (inj₁ refl) (inj₂ (inj₂ (inj₁ refl))) = inj₂ (inj₂ (inj₁ refl))
S-closed (inj₁ refl) (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = inj₂ (inj₂ (inj₂ (inj₁ refl)))
S-closed (inj₁ refl) (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) = inj₂ (inj₂ (inj₂ (inj₂ (refl))))
S-closed (inj₂ (inj₁ refl)) (inj₁ refl) = inj₂ (inj₁ refl)
S-closed (inj₂ (inj₁ refl)) (inj₂ (inj₁ refl)) = inj₂ (inj₂ (inj₂ (inj₁ refl)))
S-closed (inj₂ (inj₁ refl)) (inj₂ (inj₂ (inj₁ refl))) = inj₁ refl
S-closed (inj₂ (inj₁ refl)) (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = inj₂ (inj₂ (inj₂ (inj₂ (refl))))
S-closed (inj₂ (inj₁ refl)) (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) = inj₂ (inj₂ (inj₁ refl))
S-closed (inj₂ (inj₂ (inj₁ refl))) (inj₁ refl) = inj₂ (inj₂ (inj₁ refl))
S-closed (inj₂ (inj₂ (inj₁ refl))) (inj₂ (inj₁ refl)) = inj₁ refl
S-closed (inj₂ (inj₂ (inj₁ refl))) (inj₂ (inj₂ (inj₁ refl))) = inj₂ (inj₂ (inj₂ (inj₂ (refl))))
S-closed (inj₂ (inj₂ (inj₁ refl))) (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = inj₂ (inj₁ refl)
S-closed (inj₂ (inj₂ (inj₁ refl))) (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) = inj₂ (inj₂ (inj₂ (inj₁ refl)))
S-closed (inj₂ (inj₂ (inj₂ (inj₁ refl)))) (inj₁ refl) = inj₂ (inj₂ (inj₂ (inj₁ refl)))
S-closed (inj₂ (inj₂ (inj₂ (inj₁ refl)))) (inj₂ (inj₁ refl)) = inj₂ (inj₂ (inj₂ (inj₂ (refl))))
S-closed (inj₂ (inj₂ (inj₂ (inj₁ refl)))) (inj₂ (inj₂ (inj₁ refl))) = inj₂ (inj₁ refl)
S-closed (inj₂ (inj₂ (inj₂ (inj₁ refl)))) (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = inj₂ (inj₂ (inj₁ refl))
S-closed (inj₂ (inj₂ (inj₂ (inj₁ refl)))) (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) = inj₁ refl
S-closed (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) (inj₁ refl) = inj₂ (inj₂ (inj₂ (inj₂ (refl))))
S-closed (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) (inj₂ (inj₁ refl)) = inj₂ (inj₂ (inj₁ refl))
S-closed (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) (inj₂ (inj₂ (inj₁ refl))) = inj₂ (inj₂ (inj₂ (inj₁ refl)))
S-closed (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = inj₁ refl
S-closed (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) (inj₂ (inj₂ (inj₂ (inj₂ (refl))))) = inj₂ (inj₁ refl)

Gen⊆S : {σ : Perm 5} → BraidGen σ → S σ
Gen⊆S gen-id      = inj₁ refl
Gen⊆S gen-g1      = inj₂ (inj₁ refl)
Gen⊆S gen-g2      = inj₂ (inj₂ (inj₁ refl))
Gen⊆S (gen-∘ g h) = S-closed (Gen⊆S g) (Gen⊆S h)

¬S-tgt : ¬ S t-tgt
¬S-tgt (inj₁ ())
¬S-tgt (inj₂ (inj₁ ()))
¬S-tgt (inj₂ (inj₂ (inj₁ ())))
¬S-tgt (inj₂ (inj₂ (inj₂ (inj₁ ()))))
¬S-tgt (inj₂ (inj₂ (inj₂ (inj₂ (())))))

witness : ¬ BraidGen t-tgt
witness g = ¬S-tgt (Gen⊆S g)
