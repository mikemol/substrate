------------------------------------------------------------------------
-- Substrate.Foundation.Negation.FromNotNot
--
-- Defines: from-¬¬
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Negation; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation.FromNotNot where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Dec



-- Decidable propositions are ¬¬-stable (the constructive elimination
-- of double negation that the substrate otherwise withholds, available
-- exactly when the proposition is decidable).
from-¬¬ : {A : Set} → Dec A → ¬ ¬ A → A
from-¬¬ (yes a)  _   = a
from-¬¬ (no  ¬a) ¬¬a = ⊥-elim (¬¬a ¬a)
