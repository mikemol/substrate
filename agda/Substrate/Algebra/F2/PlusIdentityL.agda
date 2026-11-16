------------------------------------------------------------------------
-- Substrate.Algebra.F2.PlusIdentityL
--
-- Defines: +-identityˡ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.PlusIdentityL where

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
-- Additive axioms.
--
-- Identity-left and absorb-zero are `refl` by the operations' pivot
-- choice. The other axioms are 2- or 4-case enumerations on F₂.
------------------------------------------------------------------------

+-identityˡ : (x : F₂) → (𝟘 +F x) ≡ x
+-identityˡ _ = refl
