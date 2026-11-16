------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule.F1ModuleHom
--
-- Defines: F₁-Module-Hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.AsModule; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule.F1ModuleHom where

open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.PointedSet.Map.Anon
open import Substrate.Algebra.F1.AsModule.F1Module



F₁-Module-Hom : {A B : Set} → F₁-Module A → F₁-Module B → Set
F₁-Module-Hom P Q = PointedSetMap P Q
