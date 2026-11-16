------------------------------------------------------------------------
-- Substrate.Algebra.F2-CommutativeMonoid
--
-- F₂'s additive structure (𝟘, 𝟙, +F) packaged as a CommutativeMonoid.
--
-- The grading group for F₂-graded structures throughout the substrate:
-- V₄'s 3+1 parity, Bivector self-dual vs anti-self-dual axis, etc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2-CommutativeMonoid where

open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Category.CommutativeMonoid

------------------------------------------------------------------------
-- F₂'s additive CommutativeMonoid.
------------------------------------------------------------------------

F₂-CommMonoid : CommutativeMonoid F₂ _+F_ 𝟘
F₂-CommMonoid = record
  { +R-assoc     = +-assoc
  ; +R-identityˡ = +-identityˡ
  ; +R-identityʳ = +-identityʳ
  ; +R-comm      = +-comm
  }

------------------------------------------------------------------------
-- Capstone.
--
-- F₂-CommMonoid is the canonical Z/2 = F₂ grading group. Subsequent
-- slices use it as the R argument to RGradedMonoid for F₂-graded
-- structures.
------------------------------------------------------------------------
