------------------------------------------------------------------------
-- PyRigS3Orbit
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver,
-- `orbit` class — the full group structure ⟨gens⟩ mapped as generator-words).
--   grade 3; generators [[1, 0, 2], [0, 2, 1]]; |orbit| = 6 = 3! ⇒ ⟨gens⟩ = ALL of S3 (COXETER-COMPLETENESS at grade 3).
--   Every element carries an explicit generator-word (BFS-shortest); `complete`
--   exhausts the orbit. Imports from catalog/reuse-index.md. Zero postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module PyRigS3Orbit where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)

-- the 6 orbit elements (e0 = id, BFS order):
e0 e1 e2 e3 e4 e5 : Perm 3
e0 = zero ∷ suc zero ∷ suc (suc zero) ∷ []
e1 = suc zero ∷ zero ∷ suc (suc zero) ∷ []
e2 = zero ∷ suc (suc zero) ∷ suc zero ∷ []
e3 = suc (suc zero) ∷ zero ∷ suc zero ∷ []
e4 = suc zero ∷ suc (suc zero) ∷ zero ∷ []
e5 = suc (suc zero) ∷ suc zero ∷ zero ∷ []

data S3Gen : Perm 3 → Set where
  gen-id : S3Gen e0
  gen-g0 : S3Gen e1
  gen-g1 : S3Gen e2
  gen-∘  : {σ τ : Perm 3} → S3Gen σ → S3Gen τ → S3Gen (compose σ τ)

-- every orbit element as an explicit word in the generators:
orbit-0 : S3Gen e0
orbit-0 = gen-id
orbit-1 : S3Gen e1
orbit-1 = gen-g0
orbit-2 : S3Gen e2
orbit-2 = gen-g1
orbit-3 : S3Gen e3
orbit-3 = gen-∘ gen-g1 orbit-1
orbit-4 : S3Gen e4
orbit-4 = gen-∘ gen-g0 orbit-2
orbit-5 : S3Gen e5
orbit-5 = gen-∘ gen-g0 orbit-3

AllS3Gen : Perm 3 → Set
AllS3Gen σ = (σ ≡ e0) ⊎ ((σ ≡ e1) ⊎ ((σ ≡ e2) ⊎ ((σ ≡ e3) ⊎ ((σ ≡ e4) ⊎ ((σ ≡ e5))))))

-- ⟨gens⟩ = Sₙ: every permutation is a generator-word.
coxeter-complete : {σ : Perm 3} → AllS3Gen σ → S3Gen σ
coxeter-complete (inj₁ refl) = orbit-0
coxeter-complete (inj₂ (inj₁ refl)) = orbit-1
coxeter-complete (inj₂ (inj₂ (inj₁ refl))) = orbit-2
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = orbit-3
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))) = orbit-4
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (refl)))))) = orbit-5
