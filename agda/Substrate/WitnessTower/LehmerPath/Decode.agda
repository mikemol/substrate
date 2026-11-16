------------------------------------------------------------------------
-- Substrate.WitnessTower.LehmerPath.Decode
--
-- Defines: decode
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.LehmerPath; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.LehmerPath.Decode where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.Perm
open import Substrate.WitnessTower.LehmerPath.LehmerPath
open import Substrate.Foundation.Vec



------------------------------------------------------------------------
-- 2. decode = the witnessing WALK: replay the choices, each `_◂_` an
--    `insert-at`. Every decoded path is a genuine permutation (the walk
--    never leaves Sₙ — insert-at-preserves at each rung).
------------------------------------------------------------------------

decode : ∀ {n} → LehmerPath n → Perm n
decode start    = []
decode (l ◂ p)  = insert-at p (decode l)
