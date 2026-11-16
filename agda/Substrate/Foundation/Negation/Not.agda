------------------------------------------------------------------------
-- Substrate.Foundation.Negation.Not
--
-- Defines: ¬_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Negation; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation.Not where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Preamble

infix 3 ¬_


¬_ : Set → Set
¬ A = A → ⊥
