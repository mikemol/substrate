------------------------------------------------------------------------
-- Substrate.Foundation.Empty.BotElim
--
-- Defines: ⊥-elim
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Empty; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Empty.BotElim where

open import Substrate.Foundation.Empty.Bot



⊥-elim : {A : Set} → ⊥ → A
⊥-elim ()
