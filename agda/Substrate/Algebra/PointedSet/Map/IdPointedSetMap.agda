------------------------------------------------------------------------
-- Substrate.Algebra.PointedSet.Map.IdPointedSetMap
--
-- Defines: id-PointedSetMap
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.PointedSet.Map; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PointedSet.Map.IdPointedSetMap where

open import Substrate.Algebra.PointedSet
open import Substrate.Foundation.Eq
open import Substrate.Algebra.PointedSet.Map.Anon


------------------------------------------------------------------------
-- 2. Identity + composition.
------------------------------------------------------------------------

id-PointedSetMap : {A : Set} (P : PointedSet A) → PointedSetMap P P
id-PointedSetMap P = record
  { apply        = λ x → x
  ; base-preserv = refl
  }
