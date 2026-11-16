------------------------------------------------------------------------
-- Substrate.Algebra.F2.IdentityL
--
-- Defines: ·-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.IdentityL where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op



------------------------------------------------------------------------
-- Multiplicative axioms.
--
-- 𝟙 is the multiplicative identity; 𝟘 absorbs. The only invertible
-- element is 𝟙 (which is its own inverse).
------------------------------------------------------------------------

·-identityˡ : (x : F₂) → (𝟙 · x) ≡ x
·-identityˡ _ = refl
