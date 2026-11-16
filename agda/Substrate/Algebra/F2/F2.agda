------------------------------------------------------------------------
-- Substrate.Algebra.F2.F2
--
-- Defines: F₂
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.F2 where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2



------------------------------------------------------------------------
-- The 2-element carrier.
------------------------------------------------------------------------

data F₂ : Set where
  𝟘 : F₂
  𝟙 : F₂

------------------------------------------------------------------------
-- Operations.
------------------------------------------------------------------------
