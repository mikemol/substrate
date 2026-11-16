------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusF
--
-- Defines: _+F_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusF where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2

infixl 6 _+F_


_+F_ : F₂ → F₂ → F₂
𝟘 +F y = y
𝟙 +F 𝟘 = 𝟙
𝟙 +F 𝟙 = 𝟘
