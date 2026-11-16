------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule.IdF1Hom
--
-- Defines: id-F₁-Hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.AsModule; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule.IdF1Hom where

open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.PointedSet.Map.Anon
open import Substrate.Algebra.PointedSet.Map.IdPointedSetMap
open import Substrate.Algebra.F1.AsModule.F1Module
open import Substrate.Algebra.F1.AsModule.F1ModuleHom



-- A cleaner shortcut: directly re-export.

------------------------------------------------------------------------
-- 3. Category structure on F₁-Module.
------------------------------------------------------------------------

id-F₁-Hom : {A : Set} (P : F₁-Module A) → F₁-Module-Hom P P
id-F₁-Hom = id-PointedSetMap
