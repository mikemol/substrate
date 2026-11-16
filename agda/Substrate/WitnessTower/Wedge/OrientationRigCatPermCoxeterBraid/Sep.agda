------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Sep
--
-- Defines: Sep, sep0, sepS
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPermCoxeterBraid.Sep where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong



------------------------------------------------------------------------
-- 1. Sep a b — the "b is at least 2 above a" gap witness (disjointness of the
--    adjacent transpositions (a,a+1) and (b,b+1)).
------------------------------------------------------------------------

data Sep : {m : ℕ} → Fin m → Fin m → Set where
  sep0 : {m : ℕ} (k : Fin m) → Sep {suc (suc m)} zero (suc (suc k))
  sepS : {m : ℕ} {a b : Fin m} → Sep a b → Sep (suc a) (suc b)
