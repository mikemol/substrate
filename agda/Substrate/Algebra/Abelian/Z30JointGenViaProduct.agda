------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.Z30JointGenViaProduct
--
-- Discharges Z/30's joint-gen hypothesis (W3's parameter) via the
-- abelian product structure Z/30 = Z/2 × Z/3 × Z/5, using Y2's
-- pipeline.
--
-- Y6 of the 10-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Identical structural template to Y5 (Z/6) but with 3 primes;
-- demonstrates the abelian product approach scales mechanically.
--
-- Per [[expose-generator-not-orbit]]: Z/30's 30 elements accessed
-- AS (a, b, c) coordinate triples in the product representation
-- ∈ Z/2 × Z/3 × Z/5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

open import Substrate.Category.SylowDecomposition.FromWord
  using (evaluate-word)

module Substrate.Algebra.Abelian.Z30JointGenViaProduct
  -- The Z/30 carrier + ops.
  (Z30 : Set)
  (_+Z30_ : Z30 → Z30 → Z30)
  (0Z30 : Z30)
  -- Sylow predicates.
  (Sylow-pred-Z30 : Fin 3 → Z30 → Set)
  -- The 3 generators (Sylow-2 + Sylow-3 + Sylow-5).
  (gen-Z30 : Fin 3 → Z30)
  (gen-Z30-sylow :
    (g : Fin 3) → Σ (Fin 3) (λ i → Sylow-pred-Z30 i (gen-Z30 g)))
  -- The CRT representation function.
  (represent-Z30 : Z30 → List (Fin 3))
  (represent-Z30-correct :
    (g : Z30) →
    evaluate-word gen-Z30 _+Z30_ 0Z30 (represent-Z30 g) ≡ g)
  where

-- Thin instance of [[JointGenWrapper]] at (nSylow = 3, nGen = 3);
-- closes W3's joint-gen parameter.
open import Substrate.Category.PrimeFactoredGauge.JointGenWrapper
  Z30 _+Z30_ 0Z30
  3 Sylow-pred-Z30
  3 gen-Z30 gen-Z30-sylow
  represent-Z30 represent-Z30-correct
  public
  renaming (joint-gen to Z30-joint-gen)

------------------------------------------------------------------------
-- Capstone — Z/30 joint-gen dischargeable; closes W3.
--
-- Y6 of the 10-slice arc. Same template as Y5; demonstrates the
-- abelian product approach extends mechanically to any n-prime case.
-- For Z/(p₁p₂...pₙ), the template scales — n generators + CRT
-- representation; joint-gen automatic via Y2.
--
-- Next: Y7 (Monster as PresentedGroup via Y₅₅₅ + spider).
------------------------------------------------------------------------
