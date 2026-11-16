------------------------------------------------------------------------
-- Substrate.Foundation.Nat.Lt2
--
-- Defines: _<?_
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Foundation.Nat; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Nat.Lt2 where

open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.DecNot
open import Substrate.Foundation.Negation.FromNotNot
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Preamble
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Le2



_<?_ : (m n : ℕ) → Dec (m < n)
m <? n = suc m ≤? n
