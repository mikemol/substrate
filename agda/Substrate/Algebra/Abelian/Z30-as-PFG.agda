------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.Z30-as-PFG
--
-- Z/30 = Z/2 × Z/3 × Z/5 as an AbelianPFG instance — the 3-prime
-- CRT abelian PrimeFactoredGauge.
--
-- W3 of the 20-slice arc per [[prime-factored-gauge-arc]] follow-on.
-- Demonstrates the framework extends to multi-prime CRT
-- decomposition.
--
-- Structural framing. Z/30 has order 30 = 2 · 3 · 5. Three Sylow
-- subgroups:
--   Sylow-2 = {0, 15} ⊂ Z/30 (cyclic of order 2)
--   Sylow-3 = {0, 10, 20} ⊂ Z/30 (cyclic of order 3)
--   Sylow-5 = {0, 6, 12, 18, 24} ⊂ Z/30 (cyclic of order 5)
--
-- By CRT: every element n ∈ Z/30 factors as n = a·15 + b·10 + c·6
-- (mod 30) for (a, b, c) ∈ Z/2 × Z/3 × Z/5. 30 cases mechanical
-- (a small finite enumeration).
--
-- Per [[multi-field-tower-architecture]] + [[tree-shaped-field-bonds]]:
-- Z/30 → (Z/2, Z/3, Z/5) is naturally a FieldFanOut 3 instance.
-- This AbelianPFG instance + the existing FieldFanOut form a
-- composable view of the same CRT decomposition.
--
-- Module-parametric over the joint-gen witness (= 30-case CRT
-- enumeration). Concrete proof deferred to consumer modules per the
-- W2 pattern.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁; ₂)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_)

open import Substrate.Category.AbelianPFG
  using (AbelianPFG; mkAbelianPFG)
open import Substrate.Category.PrimeFactoredGauge
  using (PrimeFactoredGauge; mkPFG)
open import Substrate.Category.SylowDecomposition
  using (SylowDecomposition; mkSylowDecomposition; InGenerated)
open import Substrate.Category.GTorsor using (GTorsor)

module Substrate.Algebra.Abelian.Z30-as-PFG
  -- The Z/30 carrier.
  (Z30 : Set)
  -- Group operations.
  (_+Z30_ : Z30 → Z30 → Z30)
  (0Z30 : Z30)
  (-Z30_ : Z30 → Z30)
  -- Equivalence.
  (_≈Z30_ : Z30 → Z30 → Set)
  -- The 3 Sylow predicates:
  --   Sylow-pred zero               = "in Sylow-2 = {0, 15}"
  --   Sylow-pred ₁         = "in Sylow-3 = {0, 10, 20}"
  --   Sylow-pred ₂   = "in Sylow-5 = {0, 6, 12, 18, 24}"
  (Sylow-pred-Z30 : Fin 3 → Z30 → Set)
  -- Joint-generation witness.
  (joint-gen-Z30 :
    (g : Z30) →
    InGenerated (λ z → Σ (Fin 3) (λ i → Sylow-pred-Z30 i z))
                _+Z30_ 0Z30 g)
  -- Commutativity.
  (Z30-abelian-comm : (a b : Z30) → (a +Z30 b) ≈Z30 (b +Z30 a))
  -- Self-torsor.
  (Z30-torsor : GTorsor Z30 Z30 _+Z30_ 0Z30 _≈Z30_ _≈Z30_)
  where

------------------------------------------------------------------------
-- 1. The Sylow decomposition for Z/30.
------------------------------------------------------------------------

Z30-primes : Fin 3 → ℕ
Z30-primes zero             = 2
Z30-primes ₁       = 3
Z30-primes ₂ = 5

Z30-multiplicities : Fin 3 → ℕ
Z30-multiplicities zero             = 1
Z30-multiplicities ₁       = 1
Z30-multiplicities ₂ = 1

Z30-SylowDecomposition : SylowDecomposition Z30 _+Z30_ 0Z30 3
Z30-SylowDecomposition = mkSylowDecomposition
  Z30-primes
  Z30-multiplicities
  Sylow-pred-Z30
  joint-gen-Z30

------------------------------------------------------------------------
-- 2. The PrimeFactoredGauge for Z/30.
------------------------------------------------------------------------

Z30-PFG : PrimeFactoredGauge Z30 Z30 _+Z30_ 0Z30 _≈Z30_ _≈Z30_ 3
Z30-PFG = mkPFG Z30-SylowDecomposition Z30-torsor

------------------------------------------------------------------------
-- 3. The AbelianPFG instance.
------------------------------------------------------------------------

Z30-AbelianPFG : AbelianPFG Z30 Z30 _+Z30_ 0Z30 _≈Z30_ _≈Z30_ 3
Z30-AbelianPFG = mkAbelianPFG Z30-PFG Z30-abelian-comm

------------------------------------------------------------------------
-- 4. Capstone — Z/30 as 3-prime CRT instance.
--
-- W3 of the 20-slice arc. With W2 + W3, the substrate demonstrates
-- the AbelianPFG framework at 2- and 3-prime CRT decompositions.
-- Higher n (Z/(p₁·...·pₙ)) follows the same template parametrically.
--
-- Per [[multi-field-tower-architecture]] + [[multi-route-equivariance-
-- recovery]]: the abelian case is the "free" specialization of the
-- multi-route theorem — joint-generation comes from product structure
-- directly, without needing simplicity arguments (which were needed
-- for the GL(3, F₂) non-abelian case).
--
-- Next: W4 (GL3F2 joint-gen enumeration), W5 (capstone refresh).
------------------------------------------------------------------------
