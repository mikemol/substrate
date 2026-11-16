------------------------------------------------------------------------
-- Substrate.Algebra.F2.Dec
--
-- Defines: _≟_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Dec where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.OneNeqZero
open import Substrate.Algebra.F2.ZeroNeqOne



------------------------------------------------------------------------
-- Decidable equality (used by Vec F₂ n and downstream modules).
------------------------------------------------------------------------

_≟_ : (x y : F₂) → Dec (x ≡ y)
𝟘 ≟ 𝟘 = yes refl
𝟘 ≟ 𝟙 = no 𝟘≢𝟙
𝟙 ≟ 𝟘 = no 𝟙≢𝟘
𝟙 ≟ 𝟙 = yes refl
