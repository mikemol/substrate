------------------------------------------------------------------------
-- Substrate.Algebra.F2.F2Cases
--
-- Defines: F₂-cases
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.F2Cases where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Sum.Op
open import Substrate.Foundation.Sum.Op2
open import Substrate.Foundation.Sum.Private
open import Substrate.Foundation.Sum.Sum
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2



-- The two-element trichotomy: every F₂ element is 𝟘 or 𝟙. This is
-- the structural-extensionality lemma that lets downstream code
-- prove F₂-valued equalities by 2 cases instead of arbitrary
-- pattern-matching.
F₂-cases : (x : F₂) → (x ≡ 𝟘) ⊎ (x ≡ 𝟙)
F₂-cases 𝟘 = inj₁ refl
F₂-cases 𝟙 = inj₂ refl
