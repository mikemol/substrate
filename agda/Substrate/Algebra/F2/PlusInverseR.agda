------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusInverseR
--
-- Defines: +-inverseʳ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusInverseR where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.Op2



+-inverseʳ : (x : F₂) → (x +F (- x)) ≡ 𝟘
+-inverseʳ 𝟘 = refl
+-inverseʳ 𝟙 = refl
