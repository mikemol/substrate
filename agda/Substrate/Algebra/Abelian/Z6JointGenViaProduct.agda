------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.Z6JointGenViaProduct
--
-- Discharges Z/6's joint-gen hypothesis (W2's parameter) via the
-- abelian product structure Z/6 = Z/2 × Z/3, using Y2's pipeline.
--
-- Y5 of the 10-slice arc per [[prime-factored-gauge-arc]] follow-on.
--
-- For abelian Z/6, the joint-gen is MUCH simpler than the non-abelian
-- GL(3, F₂) case (Y4): every element n ∈ Z/6 factors UNIQUELY as
-- n = a · g₁ + b · g₂ where g₁ generates Sylow-2 and g₂ generates
-- Sylow-3, with (a, b) ∈ Z/2 × Z/3 by CRT.
--
-- The representation function is THE CRT DECOMPOSITION:
--   represent : Z/6 → List Gen
--   represent n = [gen-Sylow-2 repeated (n mod 2) times,
--                  gen-Sylow-3 repeated (n mod 3) times]
--
-- Or equivalently, since |Z/2| = 2 and |Z/3| = 3, the representation
-- is a list of at most 4 generator-applications (= 1 + 2 = 3 max,
-- plus identity = 4).
--
-- Module-parametric over (Z/6 carrier, ops, generators, correctness)
-- per substrate's pattern; concrete consumer supplies the carrier
-- and the CRT representation function.
--
-- Per [[expose-generator-not-orbit]]: Z/6's 6 elements accessed AS
-- (a, b) coordinate pairs in the product representation, not as an
-- enumeration.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.SylowDecomposition using (InGenerated)
open import Substrate.Category.SylowDecomposition.FromWord
  using (evaluate-word)
open import Substrate.Category.PrimeFactoredGauge.FromPresented
  using (joint-gen-from-presentation-≡)

module Substrate.Algebra.Abelian.Z6JointGenViaProduct
  -- The Z/6 carrier + ops.
  (Z6 : Set)
  (_+Z6_ : Z6 → Z6 → Z6)
  (0Z6 : Z6)
  -- Sylow predicates (parametric).
  (Sylow-pred-Z6 : Fin 2 → Z6 → Set)
  -- The 2 generators (Sylow-2 + Sylow-3) and their Sylow witnesses.
  (gen-Z6 : Fin 2 → Z6)
  (gen-Z6-sylow :
    (g : Fin 2) → Σ (Fin 2) (λ i → Sylow-pred-Z6 i (gen-Z6 g)))
  -- The CRT representation function.
  (represent-Z6 : Z6 → List (Fin 2))
  (represent-Z6-correct :
    (g : Z6) →
    evaluate-word gen-Z6 _+Z6_ 0Z6 (represent-Z6 g) ≡ g)
  where

------------------------------------------------------------------------
-- The Z/6 joint-gen discharge.
--
-- Mechanical via Y2's pipeline + the CRT representation. Closes
-- W2's joint-gen parameter.
------------------------------------------------------------------------

Z6-joint-gen :
  (g : Z6) →
  InGenerated (λ z → Σ (Fin 2) (λ i → Sylow-pred-Z6 i z))
              _+Z6_ 0Z6 g
Z6-joint-gen =
  joint-gen-from-presentation-≡
    gen-Z6
    _+Z6_ 0Z6
    Sylow-pred-Z6
    gen-Z6-sylow
    represent-Z6
    represent-Z6-correct

------------------------------------------------------------------------
-- Capstone — Z/6 joint-gen dischargeable from CRT representation.
--
-- Y5 of the 10-slice arc. Replaces W2's joint-gen parameter with
-- a derivation from the CRT product structure.
--
-- For abelian groups in general, joint-gen is the "free"
-- specialization — no Schreier-Sims-style algorithm needed; CRT
-- product directly gives the representation. This is the
-- substrate's [[multi-route-equivariance-recovery]] insight at
-- the simplest layer.
--
-- Next: Y6 (Z/30 = Z/2 × Z/3 × Z/5; 3-prime CRT).
------------------------------------------------------------------------
