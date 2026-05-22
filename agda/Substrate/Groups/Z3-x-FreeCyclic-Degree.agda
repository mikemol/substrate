------------------------------------------------------------------------
-- Substrate.Groups.Z3-x-FreeCyclic-Degree
--
-- The cycle-component degree on the 2-D word algebra Z₃ × ℕ.
-- Demonstrates that the 2-D structure carries a ℕ-grading via its
-- cycle component.
--
-- For a 2-D word `(w-phase, w-cycle)`, the cycle-degree is the
-- length of w-cycle (= the FreeCyclic component's degree). The
-- phase component contributes nothing to this grading.
--
-- Key properties:
--   * cycle-degree ε = 0
--   * cycle-degree (a · b) = cycle-degree a + cycle-degree b
--
-- The second is a homomorphism property: ℕ-grading transports
-- through the product operation. The cycle component reduces under
-- F.normalize via canonical-is-fixed-Free (FreeCyclic's normalize is
-- the identity); then length-distrib closes.
--
-- This is a "graded structure on a 2-D word algebra" instance — not
-- packaged as a full GradedMonoid record (the monoid laws on the
-- normalize-composed _·_ require careful handling), but the
-- structural content (degree function + homomorphism property) is
-- captured.
--
-- Per [[project-graded-bicategorical-arc]]: the cycle component IS
-- the substrate's grading axis. Z₃ × FreeCyclic has the canonical
-- ℕ-grading via its cycle component.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-x-FreeCyclic-Degree where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Product using (_,_; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.FreeCyclic-Coxeter-Length as F-Len
import Substrate.Groups.FreeCyclic-Coxeter-GradedMonoid as F-Grade
import Substrate.Groups.Z3-x-FreeCyclic as Z₃×F

------------------------------------------------------------------------
-- N-1: cycle-degree — the ℕ-degree of a 2-D word via its cycle
-- component.
------------------------------------------------------------------------

cycle-degree : Z₃×F.Word → ℕ
cycle-degree (_ , w-c) = F-Len.length-of-word w-c

------------------------------------------------------------------------
-- N-2: cycle-degree-ε — the identity has degree 0.
--
-- Z₃×F.ε = (Z₃.ε, F.ε) = ([], []). cycle-degree of this is
-- length [] = 0. Refl.
------------------------------------------------------------------------

cycle-degree-ε : cycle-degree Z₃×F.ε ≡ 0
cycle-degree-ε = refl

------------------------------------------------------------------------
-- N-3: cycle-degree-· — the degree homomorphism for the normalized
-- composition.
--
-- For Z₃×F's _·_ (= normalize ∘ ++-prod):
--   a · b = (a₁ ·_Z₃ b₁, a₂ ·_F b₂)
--         = (Z₃.normalize (a₁ ++ b₁), F.normalize (a₂ ++ b₂))
--
-- cycle-degree (a · b) = length (F.normalize (a₂ ++ b₂))
--                      ≡ length (a₂ ++ b₂)  [since F.normalize = id on any word]
--                      ≡ length a₂ + length b₂   [length-distrib]
--                      = cycle-degree a + cycle-degree b.
------------------------------------------------------------------------

cycle-degree-· :
  (a b : Z₃×F.Word) →
  cycle-degree (a Z₃×F.· b) ≡ cycle-degree a + cycle-degree b
cycle-degree-· (_ , a₂) (_ , b₂) =
  trans
    (cong F-Len.length-of-word
          (F.canonical-is-fixed-Free (F.c-any _)))
    (F-Grade.length-distrib a₂ b₂)

------------------------------------------------------------------------
-- N-4: Capstone — Z₃ × FreeCyclic carries a cycle-degree grading.
--
-- After this slice:
--
--   * cycle-degree : Z₃×F.Word → ℕ
--   * cycle-degree-ε    : degree 0 at the identity
--   * cycle-degree-·    : homomorphism (degrees add over ·)
--
-- The grading IS the cycle component's length. The phase component
-- contributes 0 (it's at the Z₃ level, no ℕ-degree).
--
-- Per [[project-graded-bicategorical-arc]]: the 2-D word algebra
-- naturally carries a ℕ-grading on its cycle axis. This makes the
-- 2-D structure a "graded Z₃" in the categorical sense: Z₃ with a
-- distinguished ℕ-grading.
--
-- Per [[project-cycle-generator-as-2-cocycle]]: the cycle generator
-- IS the cocycle data; the grading is the cocycle's degree. Z/4 vs
-- V₄ differ at degree 1 (where the cocycle distinction lives).
--
-- Deferred follow-ons:
--
--   * **Full GradedMonoid record instance**: package Z₃×F with the
--     monoid laws on _·_ + the degree function. Requires the monoid
--     laws to hold on _·_ (= normalize ∘ ++-prod), which needs
--     normalize-associated lemmas.
--
--   * **Same for Z₄ × FreeCyclic**: mechanical mirror.
--
--   * **Cross-multiplicative grading**: degrees on both axes (phase
--     gives a Z/n-valued contribution; cycle gives a ℕ-valued
--     contribution) — the "doubly-graded" structure.
------------------------------------------------------------------------
