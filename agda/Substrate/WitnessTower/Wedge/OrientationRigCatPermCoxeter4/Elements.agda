------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Elements
--
-- The 24 S₄ elements (BFS order, e0 = id), the generator datatype AdjGen4, and
-- each element's explicit generator-word.
--
-- ⟡cap-128-forcing: split from the completeness proof, which is the expensive
-- half — `AllAdjGen4` is a 24-deep nested ⊎ and each `coxeter-complete` clause
-- matches a 23-deep `inj₂` chain, so that elaboration is quadratic in the
-- nesting while these constants are linear. Two units, each under the cap.
--
-- SYNTHESIZED by jea/metalanguage/synth_agda_prototype.py (⟡pipeline-driver,
-- `orbit` class). Zero postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeter4.Elements where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)

-- the 24 orbit elements (e0 = id, BFS order):
e0 e1 e2 e3 e4 e5 e6 e7 e8 e9 e10 e11 e12 e13 e14 e15 e16 e17 e18 e19 e20 e21 e22 e23 : Perm 4
e0 = zero ∷ suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ []
e1 = suc zero ∷ zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ []
e2 = zero ∷ suc (suc zero) ∷ suc zero ∷ suc (suc (suc zero)) ∷ []
e3 = zero ∷ suc zero ∷ suc (suc (suc zero)) ∷ suc (suc zero) ∷ []
e4 = suc (suc zero) ∷ zero ∷ suc zero ∷ suc (suc (suc zero)) ∷ []
e5 = suc zero ∷ zero ∷ suc (suc (suc zero)) ∷ suc (suc zero) ∷ []
e6 = suc zero ∷ suc (suc zero) ∷ zero ∷ suc (suc (suc zero)) ∷ []
e7 = zero ∷ suc (suc (suc zero)) ∷ suc zero ∷ suc (suc zero) ∷ []
e8 = zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc zero ∷ []
e9 = suc (suc zero) ∷ suc zero ∷ zero ∷ suc (suc (suc zero)) ∷ []
e10 = suc (suc (suc zero)) ∷ zero ∷ suc zero ∷ suc (suc zero) ∷ []
e11 = suc (suc zero) ∷ zero ∷ suc (suc (suc zero)) ∷ suc zero ∷ []
e12 = suc zero ∷ suc (suc (suc zero)) ∷ zero ∷ suc (suc zero) ∷ []
e13 = zero ∷ suc (suc (suc zero)) ∷ suc (suc zero) ∷ suc zero ∷ []
e14 = suc zero ∷ suc (suc zero) ∷ suc (suc (suc zero)) ∷ zero ∷ []
e15 = suc (suc (suc zero)) ∷ suc zero ∷ zero ∷ suc (suc zero) ∷ []
e16 = suc (suc (suc zero)) ∷ zero ∷ suc (suc zero) ∷ suc zero ∷ []
e17 = suc (suc zero) ∷ suc zero ∷ suc (suc (suc zero)) ∷ zero ∷ []
e18 = suc (suc zero) ∷ suc (suc (suc zero)) ∷ zero ∷ suc zero ∷ []
e19 = suc zero ∷ suc (suc (suc zero)) ∷ suc (suc zero) ∷ zero ∷ []
e20 = suc (suc (suc zero)) ∷ suc (suc zero) ∷ zero ∷ suc zero ∷ []
e21 = suc (suc (suc zero)) ∷ suc zero ∷ suc (suc zero) ∷ zero ∷ []
e22 = suc (suc zero) ∷ suc (suc (suc zero)) ∷ suc zero ∷ zero ∷ []
e23 = suc (suc (suc zero)) ∷ suc (suc zero) ∷ suc zero ∷ zero ∷ []

data AdjGen4 : Perm 4 → Set where
  gen-id : AdjGen4 e0
  gen-g0 : AdjGen4 e1
  gen-g1 : AdjGen4 e2
  gen-g2 : AdjGen4 e3
  gen-∘  : {σ τ : Perm 4} → AdjGen4 σ → AdjGen4 τ → AdjGen4 (compose σ τ)

-- every orbit element as an explicit word in the generators:
orbit-0 : AdjGen4 e0
orbit-0 = gen-id
orbit-1 : AdjGen4 e1
orbit-1 = gen-g0
orbit-2 : AdjGen4 e2
orbit-2 = gen-g1
orbit-3 : AdjGen4 e3
orbit-3 = gen-g2
orbit-4 : AdjGen4 e4
orbit-4 = gen-∘ gen-g1 orbit-1
orbit-5 : AdjGen4 e5
orbit-5 = gen-∘ gen-g2 orbit-1
orbit-6 : AdjGen4 e6
orbit-6 = gen-∘ gen-g0 orbit-2
orbit-7 : AdjGen4 e7
orbit-7 = gen-∘ gen-g2 orbit-2
orbit-8 : AdjGen4 e8
orbit-8 = gen-∘ gen-g1 orbit-3
orbit-9 : AdjGen4 e9
orbit-9 = gen-∘ gen-g0 orbit-4
orbit-10 : AdjGen4 e10
orbit-10 = gen-∘ gen-g2 orbit-4
orbit-11 : AdjGen4 e11
orbit-11 = gen-∘ gen-g1 orbit-5
orbit-12 : AdjGen4 e12
orbit-12 = gen-∘ gen-g2 orbit-6
orbit-13 : AdjGen4 e13
orbit-13 = gen-∘ gen-g1 orbit-7
orbit-14 : AdjGen4 e14
orbit-14 = gen-∘ gen-g0 orbit-8
orbit-15 : AdjGen4 e15
orbit-15 = gen-∘ gen-g2 orbit-9
orbit-16 : AdjGen4 e16
orbit-16 = gen-∘ gen-g1 orbit-10
orbit-17 : AdjGen4 e17
orbit-17 = gen-∘ gen-g0 orbit-11
orbit-18 : AdjGen4 e18
orbit-18 = gen-∘ gen-g1 orbit-12
orbit-19 : AdjGen4 e19
orbit-19 = gen-∘ gen-g0 orbit-13
orbit-20 : AdjGen4 e20
orbit-20 = gen-∘ gen-g1 orbit-15
orbit-21 : AdjGen4 e21
orbit-21 = gen-∘ gen-g0 orbit-16
orbit-22 : AdjGen4 e22
orbit-22 = gen-∘ gen-g0 orbit-18
orbit-23 : AdjGen4 e23
orbit-23 = gen-∘ gen-g0 orbit-20
