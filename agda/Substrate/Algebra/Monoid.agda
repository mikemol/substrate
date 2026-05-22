------------------------------------------------------------------------
-- Substrate.Algebra.Monoid
--
-- M3 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- A Monoid is a Semigroup + identity element + identity laws.
-- The standard categorical name. Closes the
-- L8-WordAlgebra-MonoidLaws inline-record and the RuleAction /
-- GeneratorOperad operad-laws gaps.
--
-- **F₁ lands here** as the trivial 1-element Monoid. Per the
-- user's question (2026-05-21): the substrate now formalises F₁
-- as the degenerate base case of the algebra ladder.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Monoid where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup; magma; ·-assoc)

------------------------------------------------------------------------
-- 1. The Monoid record.
------------------------------------------------------------------------

record Monoid (A : Set) : Set where
  field
    semigroup : Semigroup A
    ε         : A
    ε-left :
      (a : A) →
      let _·_ = Magma._·_ (magma semigroup)
      in ε · a ≡ a
    ε-right :
      (a : A) →
      let _·_ = Magma._·_ (magma semigroup)
      in a · ε ≡ a

open Monoid public

------------------------------------------------------------------------
-- 2. F₁ as the trivial Monoid `{*}`.
--
-- The "field with one element" in the Tits/Manin sense: a single
-- absorbing point. As a Monoid: 1-element carrier with the unique
-- binary op + identity = that one element.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Algebra.Magma using (trivial-Magma)

F₁-Semigroup : Semigroup ⊤
F₁-Semigroup = record
  { magma   = trivial-Magma
  ; ·-assoc = λ _ _ _ → refl
  }

F₁-Monoid : Monoid ⊤
F₁-Monoid = record
  { semigroup = F₁-Semigroup
  ; ε         = tt
  ; ε-left    = λ _ → refl
  ; ε-right   = λ _ → refl
  }

------------------------------------------------------------------------
-- 3. Capstone for M3.
--
-- Monoid + F₁ instance. M4 extends with inverse → Group.
------------------------------------------------------------------------
