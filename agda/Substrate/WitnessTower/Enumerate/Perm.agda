------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Perm
--
-- Defines: Perm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Perm where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec



------------------------------------------------------------------------
-- 1. Permutation rep: image vector. Perm n = Vec (Fin n) n.
------------------------------------------------------------------------

Perm : ℕ → Set
Perm n = Vec (Fin n) n
