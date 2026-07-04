{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQBridge — ⟡FU-sep-Q-bridge, instantiating the SUBSTRATE'S generic pattern
-- (operator: EEATrace + everything touching it parameterizes ONE structure;
-- instantiate it precisely the same way, don't re-derive; study the code first).
--
-- ⟡H0 (read RationalAdjunction + EEATrace + Final): the pattern is
--   Coalg S = S → Obs × S              -- emit an observation, advance state
--   ana : Coalg S → S → stream         -- embed, FORCED by ana-unique (terminal)
--   the FINITE side is a trace WITH `base`: EEATrace = base a | step b w rest,
--     where `step` carries a WEDGE w with the reconstruction eq a ≡ q·b + r.
--   the RETRACTION is `reconstruct`: fold the finite trace with `reconStep`
--     (the LOCAL step-inverse q·b+r), bottoming at `base` — NOT the global
--     `convergent`, which DRIFTS past the CF length (unit-drift: 4/3 ≠ 3/2).
--   `eea-unit : reconstruct t ≡ (a,b)` — the general unit, by STRUCTURAL
--     INDUCTION, using `wedge-eq` (a ≡ q·b+r) at every step.
--
-- THE BRIDGE (same instantiation): a normalizing SKI term's observation carries
-- this trace; its finite content IS a Böhm tree. The retraction folds the finite
-- trace with the local step-inverse and RECOVERS the start — the eea-unit analog.
-- Abstracted over the observation H and the reconstruction equation (the Wedge),
-- so it instantiates for GCD (EEATrace), for SKI-BT, or any observation coalgebra.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQBridge where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)

private
  ≡trans : {A : Set} {x y z : A} → x ≡ y → y ≡ z → x ≡ z
  ≡trans refl q = q
  cong : {A B : Set} (f : A → B) {x y : A} → x ≡ y → f x ≡ f y
  cong f refl = refl
  cong₂ : {A B C : Set} (f : A → B → C) {x x' : A} {y y' : B}
        → x ≡ x' → y ≡ y' → f x y ≡ f x' y'
  cong₂ f refl refl = refl

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
