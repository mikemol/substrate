------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.InsertAt
--
-- Defines: insert-at
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.InsertAt where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate.Perm



------------------------------------------------------------------------
-- 2. The witnessing-insertion move. Given a perm σ of Fin n and a target
--    position p : Fin (suc n) for the NEW bottom index, build a perm of
--    Fin (suc n):
--      * the new index `zero` (the witness) maps to p;
--      * each old index `suc i` maps to punchIn p (σ i) — the old image,
--        shifted to dodge p (keeps injectivity).
------------------------------------------------------------------------

insert-at : {n : ℕ} → Fin (suc n) → Perm n → Perm (suc n)
insert-at p σ = p ∷ map (punchIn p) σ
