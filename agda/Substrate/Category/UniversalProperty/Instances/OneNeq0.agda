------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Instances.OneNeq0
--
-- Defines: 1≢0
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.Instances; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Instances.OneNeq0 where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq



1≢0 : (1 ≡ 0) → ⊥
1≢0 ()
