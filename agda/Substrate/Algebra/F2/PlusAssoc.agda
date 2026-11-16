------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusAssoc
--
-- Defines: +-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusAssoc where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF



+-assoc : (x y z : F₂) → ((x +F y) +F z) ≡ (x +F (y +F z))
+-assoc 𝟘 _ _ = refl
+-assoc 𝟙 𝟘 _ = refl
+-assoc 𝟙 𝟙 𝟘 = refl
+-assoc 𝟙 𝟙 𝟙 = refl
