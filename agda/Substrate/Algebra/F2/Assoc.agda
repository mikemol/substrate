------------------------------------------------------------------------
-- Substrate.Algebra.F2.Assoc
--
-- Defines: ·-assoc
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Assoc where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op



·-assoc : (x y z : F₂) → ((x · y) · z) ≡ (x · (y · z))
·-assoc 𝟘 _ _ = refl
·-assoc 𝟙 _ _ = refl
