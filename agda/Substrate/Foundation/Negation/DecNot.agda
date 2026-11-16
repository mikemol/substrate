------------------------------------------------------------------------
-- Substrate.Foundation.Negation.DecNot
--
-- Defines: dec-¬
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Negation; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation.DecNot where

open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Dec



-- Negation of a decidable proposition is decidable.
dec-¬ : {A : Set} → Dec A → Dec (¬ A)
dec-¬ (yes a)  = no (λ ¬a → ¬a a)
dec-¬ (no  ¬a) = yes ¬a
