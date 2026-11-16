------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.Phase.V4CommutativeMonoid
--
-- Defines: V₄-CommutativeMonoid
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Logic.Evidence.Verdict.Phase; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.Phase.V4CommutativeMonoid where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Empty.Bot
open import Substrate.Groups.V4.Axioms.Assoc
open import Substrate.Groups.V4.Axioms.Comm
open import Substrate.Groups.V4.Axioms.EpsilonLeft
open import Substrate.Groups.V4.Axioms.EpsilonRight
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Category.CommutativeMonoid
open import Substrate.Logic.Evidence.Verdict
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Logic.Evidence.Verdict.Phase.NegPosCompnegNeg
open import Substrate.Logic.Evidence.Verdict.Phase.Eq



------------------------------------------------------------------------
-- GROUNDED: the diagonal involutions {id, negPos, negNeg, negBoth} ARE V₄
-- (id↦e, negPos↦α, negNeg↦β, negBoth↦γ — the α·β≡γ link above), and V₄ IS a
-- substrate-named `Category.CommutativeMonoid` (abelian, exponent 2), reusing
-- V₄'s own group laws. So the involution structure sits on the categorical
-- spine; the central twist (the commutator cocycle above) is the non-abelian
-- residue D₄ carries on top of this abelian V₄.
------------------------------------------------------------------------

V₄-CommutativeMonoid : CommutativeMonoid V₄ _·₄_ ε
V₄-CommutativeMonoid = record
  { +R-assoc     = ·-assoc
  ; +R-identityˡ = ε-left
  ; +R-identityʳ = ε-right
  ; +R-comm      = ·-comm
  }
