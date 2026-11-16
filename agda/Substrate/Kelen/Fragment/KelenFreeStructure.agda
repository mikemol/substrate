------------------------------------------------------------------------
-- Substrate.Kelen.Fragment.KelenFreeStructure
--
-- Defines: kelen-free-structure
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Kelen.Fragment; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment.KelenFreeStructure where

open import Substrate.Groups.Coxeter.Word
open import Substrate.Category.FreeOverBasis
open import Substrate.Kelen.Fragment.Relational
open import Substrate.Kelen.Fragment.KelenWord
open import Substrate.Kelen.Fragment.Single



------------------------------------------------------------------------
-- 4. The DISTINGUISHING note: Kēlen relations are NOT functions.
--
-- A relation R : A ↔ B is a subset of A × B (multiple outputs per
-- input allowed; some inputs may have NO outputs). This is
-- fundamentally different from Lojban's Selbri (a function-like
-- n-ary morphism) or Toki Pona's modify (a binary commutative-
-- monoid op).
--
-- Per [[feedback-comments-dont-overclaim]] the full Rel-category
-- machinery (dagger, residuals, etc.) is not in this slice; the
-- FreeOverBasis witness here records that the cell IS occupied,
-- with deeper relation-algebra structure deferred.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. The FreeOverBasis instance.
------------------------------------------------------------------------

kelen-free-structure : FreeOverBasis Relational KelenWord
kelen-free-structure = mkFreeOverBasis single
