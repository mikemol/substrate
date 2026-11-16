------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj
--
-- Defines: Objₚ
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Wedge.OrientationRigCatPerm; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRigCatPerm.Obj where

open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Hedberg.DecidableUIP
open import Substrate.WitnessTower.Wedge.OrientationRigCat
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Subst



------------------------------------------------------------------------
-- S0 — THE OBJECTS AND MORPHISMS. One object per grade (Objₛ, the grade-indexed
-- singleton; its automorphisms ARE the permutations), and the FULL Sₙ as
-- morphisms: a grade-equality PLUS a permutation of the target grade. Honest
-- Σ-data (the perm ℕ+ the grade witness that makes it grade-respecting).
------------------------------------------------------------------------

Objₚ : ℕ → Set
Objₚ = Objₛ
