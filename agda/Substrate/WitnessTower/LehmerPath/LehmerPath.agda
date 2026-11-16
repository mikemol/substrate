------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.LehmerPath
--
-- Defines: LehmerPath, _◂_, start
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.LehmerPath where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin

infixl 5 _◂_


------------------------------------------------------------------------
-- 1. The decorated witness path: Core.Path with an insertion-CHOICE at each
--    step. At rung k the new top witnesses the rung below by choosing one of
--    the (suc k) positions — exactly the factoradic digit Fin (suc k).
------------------------------------------------------------------------

data LehmerPath : ℕ → Set where
  start : LehmerPath zero
  _◂_   : ∀ {k} → LehmerPath k → Fin (suc k) → LehmerPath (suc k)
