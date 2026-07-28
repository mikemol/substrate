------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver,
-- `orbit` class — the full group structure ⟨gens⟩ mapped as generator-words).
--   grade 4; generators [[1, 0, 2, 3], [0, 2, 1, 3], [0, 1, 3, 2]]; |orbit| = 24 = 4! ⇒ ⟨gens⟩ = ALL of S4 (COXETER-COMPLETENESS at grade 4).
--   Every element carries an explicit generator-word (BFS-shortest); `complete`
--   exhausts the orbit. Imports from catalog/reuse-index.md. Zero postulates/holes.
--
-- ⟡cap-128-forcing: the elements, the generator datatype and the 24 orbit-words
-- live in .Elements. What is left here is the COMPLETENESS proof, the expensive
-- half: `AllAdjGen4` is a 24-deep nested ⊎ and each clause matches a 23-deep
-- `inj₂` chain, so its elaboration is quadratic in the nesting.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Elements
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Tail

AllAdjGen4 : Perm 4 → Set
AllAdjGen4 σ = (σ ≡ e0) ⊎ ((σ ≡ e1) ⊎ ((σ ≡ e2) ⊎ ((σ ≡ e3) ⊎ ((σ ≡ e4) ⊎ ((σ ≡ e5) ⊎ ((σ ≡ e6) ⊎ ((σ ≡ e7) ⊎ ((σ ≡ e8) ⊎ ((σ ≡ e9) ⊎ ((σ ≡ e10) ⊎ ((σ ≡ e11) ⊎ (AllAdjGen4-tail σ))))))))))))

-- ⟨gens⟩ = Sₙ: every permutation is a generator-word.
coxeter-complete : {σ : Perm 4} → AllAdjGen4 σ → AdjGen4 σ
coxeter-complete (inj₁ refl) = orbit-0
coxeter-complete (inj₂ (inj₁ refl)) = orbit-1
coxeter-complete (inj₂ (inj₂ (inj₁ refl))) = orbit-2
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₁ refl)))) = orbit-3
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))) = orbit-4
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))) = orbit-5
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))) = orbit-6
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))))) = orbit-7
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))))) = orbit-8
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))))))) = orbit-9
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl))))))))))) = orbit-10
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₁ refl)))))))))))) = orbit-11
coxeter-complete (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ (inj₂ t)))))))))))) = coxeter-complete-tail t
