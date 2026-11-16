------------------------------------------------------------------------
-- Substrate.Foundation.Negation.Dec
--
-- Defines: Dec
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Negation; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Negation.Dec where

open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Negation.Not



data Dec (A : Set) : Set where
  yes : A   → Dec A
  no  : ¬ A → Dec A
