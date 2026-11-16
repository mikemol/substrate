------------------------------------------------------------------------
-- Substrate.Foundation.Eq.Neq
--
-- Defines: _≢_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Eq; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Eq.Neq where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Level
private variable a b c : Level
open import Substrate.Foundation.Eq.Preamble
open import Substrate.Foundation.Eq

infix 4 _≢_


_≢_ : {A : Set a} → A → A → Set a
x ≢ y = x ≡ y → ⊥
