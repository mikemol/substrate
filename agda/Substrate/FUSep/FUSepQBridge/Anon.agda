------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQBridge.Anon
--
-- Defines: _
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQBridge; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQBridge.Anon where

open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQBridge.Eqtrans
open import Substrate.FUSep.FUSepQBridge.Cong



------------------------------------------------------------------------
-- The GENERIC step-inverse data — EEATrace's `step` abstracted. A `Recon` at
-- state s records: a head observation h, a next state s', and the RECONSTRUCTION
-- EQUATION s ≡ recon h s' (the Wedge a ≡ q·b + r) — this equation is what makes
-- the fold FAITHFUL (the residue kept, no drift). Parameterized by the local
-- inverse `recon : H → S → S` (= reconStep), the ONE thing to instantiate.
------------------------------------------------------------------------
module _ {H S : Set} (recon : H → S → S) where

  -- the finite trace WITH `base` (termination) and step-carrying-its-equation.
  data FinTrace : S → Set where
    base : ∀ s → FinTrace s
    step : ∀ {s} (h : H) (s' : S) → s ≡ recon h s' → FinTrace s' → FinTrace s

  -- RECONSTRUCT (the eea-unit fold): fold with the LOCAL inverse, bottoming at
  -- base. Recurse into the continuation, apply recon at each step.
  reconstruct : ∀ {s} → FinTrace s → S
  reconstruct (base s)          = s
  reconstruct (step h s' _ rest) = recon h (reconstruct rest)

  -- THE UNIT (eea-unit, ∀, by STRUCTURAL INDUCTION): reconstruct recovers exactly
  -- the start state — using the step's reconstruction equation (s ≡ recon h s')
  -- and the IH on the continuation. Bottoms out at base — no padding, no drift.
  fintrace-unit : ∀ {s} (t : FinTrace s) → reconstruct t ≡ s
  fintrace-unit (base s)           = refl
  fintrace-unit (step h s' eq rest) =
    ≡trans (cong (recon h) (fintrace-unit rest)) (sym-eq eq)
    where sym-eq : ∀ {x y : S} → x ≡ y → y ≡ x
          sym-eq refl = refl
