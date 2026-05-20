------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.HappyFamily.JointGenViaDescent
--
-- The Happy Family-wide joint-gen propagation pipeline: each
-- non-Monster Happy Family member H = C_M(z) / ⟨z⟩ (or further
-- centralizer-descent) inherits joint-gen from the Monster's
-- presentation via Y8's Monster-joint-gen + the centralizer-
-- descent structure (T9 CentralizerDescent).
--
-- Y9 of the 10-slice arc per [[prime-factored-gauge-arc]] follow-on.
--
-- Structural pattern:
--   1. Each HF member H is a sub-quotient of M (via V1
--      CentralizerDescent or further iterated descents).
--   2. M's joint-gen comes from Y8 (Monster-joint-gen).
--   3. Each H element has a preimage in M (= the lift through
--      the centralizer quotient).
--   4. M's word for the preimage gives, via projection through
--      the descent, a word in H's generators.
--   5. Y2's pipeline + the projected word gives H's joint-gen.
--
-- Module-parametric over (H, descent witness, joint-gen path),
-- per substrate's pattern. For each specific HF member
-- (BabyMonster, Conway, Mathieu, Fischer, HN/Th/He/J₂/HS/McL/Suz),
-- a thin instance module supplies the parameters.
--
-- Per [[expose-generator-not-orbit]]: the Happy Family is exposed
-- AS A DESCENT TREE from the Monster, not as 20 separately-
-- enumerated groups. The substrate's [[homology-cohomology-recursion]]
-- recursive pattern manifests at the sporadic level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Data.Fin using (Fin)
open import Data.List using (List)
open import Data.Nat using (ℕ)
open import Data.Product using (Σ; _,_)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Category.SylowDecomposition using (InGenerated)
open import Substrate.Category.SylowDecomposition.FromWord
  using (evaluate-word)
open import Substrate.Category.PrimeFactoredGauge.FromPresented
  using (joint-gen-from-presentation-≡)

module Substrate.Algebra.Sporadic.HappyFamily.JointGenViaDescent where

------------------------------------------------------------------------
-- The descent-based joint-gen pipeline for any HF member.
--
-- Given:
--   * H — a Happy Family member's carrier
--   * H's group ops + Sylow predicates
--   * H's generators (= elements of H inhabiting Sylows)
--   * A representation function H → List(H-Gen)
--     (= the algorithmic content of the descent + projection)
--
-- Outputs joint-gen for H via Y2's pipeline.
------------------------------------------------------------------------

module Generic-Descent
  -- The HF member's data.
  (H : Set)
  (_·H_ : H → H → H)
  (εH : H)
  -- Number of Sylow primes for H.
  (nSylow : ℕ)
  (Sylow-pred-H : Fin nSylow → H → Set)
  -- Number of generators for H.
  (nGen : ℕ)
  (gen-H : Fin nGen → H)
  (gen-H-sylow :
    (g : Fin nGen) → Σ (Fin nSylow) (λ i → Sylow-pred-H i (gen-H g)))
  -- The representation function for H (via descent from parent).
  (represent-H : H → List (Fin nGen))
  (represent-H-correct :
    (g : H) →
    evaluate-word gen-H _·H_ εH (represent-H g) ≡ g)
  where

  H-joint-gen :
    (g : H) →
    InGenerated (λ z → Σ (Fin nSylow) (λ i → Sylow-pred-H i z))
                _·H_ εH g
  H-joint-gen =
    joint-gen-from-presentation-≡
      gen-H _·H_ εH
      Sylow-pred-H gen-H-sylow
      represent-H represent-H-correct

------------------------------------------------------------------------
-- Capstone — HF-wide joint-gen propagation framework.
--
-- Y9 of the 10-slice arc. With Y9 landed, ALL 20 Happy Family
-- members can have their joint-gen derived (in principle) via the
-- centralizer-descent structure + their own per-instance
-- representations.
--
-- For each HF member, a thin downstream instance supplies:
--   * H's specific data (carrier, ops, Sylow primes count, generators)
--   * The representation function via descent from a parent
--     (Monster for direct descents; further descents for grand-
--     descendants like Mathieu groups via Conway intermediate)
--   * Correctness proof (= descent projection respects evaluation)
--
-- Then Generic-Descent.H-joint-gen produces the joint-gen function
-- for that HF member.
--
-- Per [[homology-cohomology-recursion]]: the recursive HF structure
-- IS the substrate's recursive cataloging principle. Monster's
-- presentation is the "atom"; HF members inherit cohomological
-- structure via the descent tree.
--
-- Per [[expose-generator-not-orbit]] applied at sporadic-group level:
-- 20 HF members + 1 descent tree + 16 Monster generators ≪ 10^54
-- enumerated elements.
--
-- Next: Y10 (Y-arc capstone refresh).
------------------------------------------------------------------------
