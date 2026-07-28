------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws
--
-- The commutative-ring laws of F₂[x] multiplication (`_*P_`), proven via
-- the coefficient calculus: ℕ-indexed coefficient extraction `nth`
-- (𝟘 out of range), its convolution characterization `convCoeff`
-- (`nth-*P`), and observation-equality `nth-ext`. From these:
--   * bilinear distributivity   (`*P-distribʳ` / `*P-distribˡ`),
--   * commutativity             (`*P-comm`, via nested `linear-extensionality`),
--   * associativity             (`*P-assoc`, via 3× nested `linear-extensionality`),
--   * graded identity           (`*P-identityˡ-nth`).
--
-- Method: polynomial equalities reduce to per-coordinate F₂ facts
-- (`nth-ext`) and to basis-vector checks (`linear-extensionality`), so
-- the Fubini reindex lives inside `preserves-sum` — never written by hand.
-- `_*P_` is length-additive, so the FIXED-carrier ring is GF(2⁸) =
-- F₂[x]/(m) via reduce-mod-m; these are its graded laws.
--
-- This module is a RE-EXPORT HUB; the development is split theorem-per-stage
-- under RingLaws/ (the `make advise` theorem-per-file idiom):
--   Nth        §AI-7 base   coefficient extraction + its hom lemmas
--   Conv       §AI-7 base   convCoeff, nth-*P (the convolution bridge), nth-ext
--   Distrib    §AI-7 cont   bilinear distributivity
--   Basis      §AI-7e/7d    nth↔basis delta; convCoeff of 𝟎ⱽ/unit/monomial
--   Scalar     §AI-7f       preserves-*ₛ + subst-linearity
--   BasisComm  §AI-7e       monomial deltas ⇒ basis-level commutativity
--   Comm       §AI-7f/7g    *P-comm (nested linear-extensionality)
--   Assoc      §AI-7h       mono-assoc + *P-assoc (3× nested)
--   Identity   §AI-7d       *P-identityˡ-nth
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws where

open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv
open import Substrate.Algebra.F2.Polynomial.RingLaws.Distrib
open import Substrate.Algebra.F2.Polynomial.RingLaws.Basis
open import Substrate.Algebra.F2.Polynomial.RingLaws.Scalar
open import Substrate.Algebra.F2.Polynomial.RingLaws.BasisComm
open import Substrate.Algebra.F2.Polynomial.RingLaws.Comm
open import Substrate.Algebra.F2.Polynomial.RingLaws.Assoc
open import Substrate.Algebra.F2.Polynomial.RingLaws.Identity