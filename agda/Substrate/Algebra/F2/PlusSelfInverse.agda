------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusSelfInverse
--
-- Defines: +-self-inverse
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusSelfInverse where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF



------------------------------------------------------------------------
-- A handful of useful derived facts (all proven by case analysis,
-- finitely small here, but used as inference rules elsewhere).
------------------------------------------------------------------------

-- x +F x ≡ 𝟘 (characteristic 2).
+-self-inverse : (x : F₂) → (x +F x) ≡ 𝟘
+-self-inverse 𝟘 = refl
+-self-inverse 𝟙 = refl
