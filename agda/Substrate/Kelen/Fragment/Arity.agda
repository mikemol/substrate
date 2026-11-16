------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.Arity
--
-- Defines: arity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.Arity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Kelen.Fragment.Relational



arity : Relational → ℕ
arity la    = 2
arity nā    = 1
arity pa    = 3
arity jana  = 3
