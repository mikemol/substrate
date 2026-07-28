------------------------------------------------------------------------
-- Substrate.Category.PrimeFactoredGauge.JointGenWrapper
--
-- The K-parametric wrapper around `joint-gen-from-presentation-≡`.
--
-- Every Y-arc / W-arc joint-gen discharge — Z/6 (Y5), Z/30 (Y6),
-- Monster (Y8), Happy Family members via descent (Y9) — applies
-- exactly this body:
--
--   site-joint-gen = joint-gen-from-presentation-≡
--                      gen _·_ ε Sylow-pred gen-sylow
--                      represent represent-correct
--
-- The deltas are the site's (carrier, ops, generator/sylow counts,
-- representation function). The body itself is invariant. This
-- file names that invariant micropattern.
--
-- Previously this wrapper was inlined in 4 separate files (Z6 /
-- Z30 / Monster / HappyFamily.Generic-Descent), each with its own
-- module-parametric header repeating the seven parameters.
-- Extracting here gives every joint-gen site a single point of
-- attachment.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.SylowDecomposition using (InGenerated)
open import Substrate.Category.SylowDecomposition.FromWord
  using (evaluate-word)
open import Substrate.Category.PrimeFactoredGauge.FromPresented
  using (joint-gen-from-presentation-≡)

module Substrate.Category.PrimeFactoredGauge.JointGenWrapper
  -- The group carrier + ops.
  (G : Set)
  (_·_ : G → G → G)
  (ε : G)
  -- Sylow primes.
  (nSylow : ℕ)
  (Sylow-pred : Fin nSylow → G → Set)
  -- Generators (count may differ from nSylow — see Monster: 15
  -- Sylows, 16 generators).
  (nGen : ℕ)
  (gen : Fin nGen → G)
  (gen-sylow :
    (g : Fin nGen) → Σ (Fin nSylow) (λ i → Sylow-pred i (gen g)))
  -- Representation function (the algorithmic content — CRT for
  -- abelian, Y₅₅₅/spider for Monster, descent-projection for HF).
  (represent : G → List (Fin nGen))
  (represent-correct :
    (g : G) → evaluate-word gen _·_ ε (represent g) ≡ g)
  where

joint-gen :
  (g : G) →
  InGenerated (λ z → Σ (Fin nSylow) (λ i → Sylow-pred i z)) _·_ ε g
joint-gen =
  joint-gen-from-presentation-≡
    gen _·_ ε
    Sylow-pred gen-sylow
    represent represent-correct
