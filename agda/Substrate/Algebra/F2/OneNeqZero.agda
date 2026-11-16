------------------------------------------------------------------------
-- Substrate.Algebra.F2.OneNeqZero
--
-- Defines: 𝟙≢𝟘
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.OneNeqZero where

open import Substrate.Algebra.F2.F2
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



------------------------------------------------------------------------
-- Distinctness of the two elements (the non-trivial field axiom).
------------------------------------------------------------------------

𝟙≢𝟘 : 𝟙 ≡ 𝟘 → ⊥
𝟙≢𝟘 ()
