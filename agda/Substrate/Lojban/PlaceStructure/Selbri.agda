------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure.Selbri
--
-- Defines: Selbri, apply, mkSelbri
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Lojban.PlaceStructure; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure.Selbri where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.Eq.Cong
open import Substrate.Lojban.PlaceStructure.Private



------------------------------------------------------------------------
-- 1. Selbri : the n-ary morphism record.
--
-- A `Selbri n Sumti Sem` is an n-place predicate / relation viewed
-- as a typed n-ary function. The record allows future fields
-- (preservation tags, arity metadata) without breaking the surface.
------------------------------------------------------------------------

record Selbri
  (n : ℕ) (Sumti : Set ℓA) (Sem : Set ℓB) : Set (ℓA ⊔ ℓB) where
  constructor mkSelbri
  field
    apply : Vec Sumti n → Sem

open Selbri public
