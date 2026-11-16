------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIShedDuality.Chain
--
-- Defines: Chain
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.SKIShedDuality; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.SKIShedDuality.Chain where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.Wedge.Product
open import Substrate.Algebra.Wedge.Product.Term
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Eq
open import Substrate.Algebra.R.Trace.SKIShedDuality.SkiProduct



Chain : ℕ → Set
Chain n = WedgeTerm ski-product n
