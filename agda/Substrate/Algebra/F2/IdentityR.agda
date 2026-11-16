------------------------------------------------------------------------
-- Substrate.Algebra.F2.IdentityR
--
-- Defines: ·-identityʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.IdentityR where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op



·-identityʳ : (x : F₂) → (x · 𝟙) ≡ x
·-identityʳ 𝟘 = refl
·-identityʳ 𝟙 = refl
