------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.OrbitCloudRung3  (Ⓟ.3′ — rung-3 idempotent species)
--
-- The corrected rung-3 orbit cloud (POINT_CLOUD §0, updated + the
-- jea_parity_species_probe). Rung 3 = K₄, cycle space ℚ³. Of the 24 vertex
-- frames the cloud has EXACTLY 22 points (exact rational, probe-verified — NOT a
-- float artifact, NOT an orbit size): the unsigned cycle-space map identifies two
-- pairs, each related by the V₂ double-transposition τ = (0 1)(2 3), which acts as
-- the reflection T below. T is the IDEMPOTENT SPECIES (T² = I, e = (I+T)/2
-- idempotent) — the same clean / orthogonal-idempotent genus mechanized in
-- CenterIsStarCRT (Ξ★.cⁿ), as opposed to the NILPOTENT species (Ξ★.g, the graded
-- cross_term residue) which the probe confirms is INVISIBLE to the cloud (rungs
-- ≥ 4 are faithful: 120→120, 720→720).
--
-- T = M(τ) extracted exactly from the authoritative unsigned construction
-- (C·P·Cpinv, jea_parity_species_probe): T(a,b,c) = (b, a, a−b+c), integer.
--
-- VERIFY-BY-COMPILE FLAG: T is a reflection — it negates the 1-dim line
-- ⟨(1,−1,−1)⟩ and fixes the 2-plane ⟨(1,1,0),(0,0,1)⟩. The doc identifies that
-- −1 line with the antisymmetric-form WITNESS kernel; but B₃'s kernel (Ξ★.1) is
-- (1,−1,1), and T·(1,−1,1) = (−1,1,3) ≠ −(1,−1,1). So in this cycle basis the
-- reflection's −1 line is (1,−1,−1) ≠ the B₃ witness line — they do NOT coincide.
-- The reflection / idempotent structure holds; the geometric identification with
-- the B₃ kernel does not (flagged for the handoff to reconcile).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.OrbitCloudRung3 where

open import Substrate.Foundation.Vec using (Vec; _∷_; [])
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Z using (ℤ; +_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_)

V3 : Set
V3 = Vec ℤ 3

-- The V₂ reflection T = M(τ), τ=(0 1)(2 3), on cycle space: (a,b,c) ↦ (b, a, a−b+c).
act-T : V3 → V3
act-T (a ∷ b ∷ c ∷ []) = b ∷ a ∷ ((a +ℤ (-ℤ b)) +ℤ c) ∷ []

------------------------------------------------------------------------
-- T² = I (the IDEMPOTENT/involution species), witnessed on the standard basis
-- (a linear map equals its action on a basis): T²·eᵢ ≡ eᵢ.
------------------------------------------------------------------------

T²-e₁ : act-T (act-T ((+ 1) ∷ (+ 0) ∷ (+ 0) ∷ [])) ≡ ((+ 1) ∷ (+ 0) ∷ (+ 0) ∷ [])
T²-e₁ = refl
T²-e₂ : act-T (act-T ((+ 0) ∷ (+ 1) ∷ (+ 0) ∷ [])) ≡ ((+ 0) ∷ (+ 1) ∷ (+ 0) ∷ [])
T²-e₂ = refl
T²-e₃ : act-T (act-T ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])) ≡ ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])
T²-e₃ = refl

------------------------------------------------------------------------
-- The reflection eigenstructure: eigenvalue −1 on ⟨(1,−1,−1)⟩, +1 on the
-- 2-plane ⟨(1,1,0),(0,0,1)⟩ — so T is a reflection (the V₂ parity reroute).
------------------------------------------------------------------------

-- −1 eigenline: T·(1,−1,−1) = −(1,−1,−1) = (−1,1,1).
neg-eigenline : act-T ((+ 1) ∷ (-ℤ (+ 1)) ∷ (-ℤ (+ 1)) ∷ [])
              ≡ ((-ℤ (+ 1)) ∷ (+ 1) ∷ (+ 1) ∷ [])
neg-eigenline = refl

-- +1 eigenplane: T fixes (1,1,0) and (0,0,1).
pos-eigen-1 : act-T ((+ 1) ∷ (+ 1) ∷ (+ 0) ∷ []) ≡ ((+ 1) ∷ (+ 1) ∷ (+ 0) ∷ [])
pos-eigen-1 = refl
pos-eigen-2 : act-T ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ []) ≡ ((+ 0) ∷ (+ 0) ∷ (+ 1) ∷ [])
pos-eigen-2 = refl
