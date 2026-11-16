------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusComm
--
-- Defines: +-comm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusComm where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF



+-comm : (x y : F₂) → (x +F y) ≡ (y +F x)
+-comm 𝟘 𝟘 = refl
+-comm 𝟘 𝟙 = refl
+-comm 𝟙 𝟘 = refl
+-comm 𝟙 𝟙 = refl
