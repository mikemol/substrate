------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule.ComposeF1Hom
--
-- Defines: compose-F₁-Hom
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.AsModule; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule.ComposeF1Hom where

open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.PointedSet.Map.Anon
open import Substrate.Algebra.PointedSet.Map.ComposePointedSetMap
open import Substrate.Algebra.F1.AsModule.F1Module
open import Substrate.Algebra.F1.AsModule.F1ModuleHom



compose-F₁-Hom :
  {A B D : Set} {P : F₁-Module A} {Q : F₁-Module B} {R : F₁-Module D} →
  F₁-Module-Hom Q R →
  F₁-Module-Hom P Q →
  F₁-Module-Hom P R
compose-F₁-Hom = compose-PointedSetMap

------------------------------------------------------------------------
-- 4. Capstone for F1m3.
--
-- F₁-Module = PointedSet identified. The category of F₁-modules
-- IS the category of pointed sets. F1m4 builds GL(n, F₁) = Sₙ via
-- the basepoint-preserving bijections of (Fin (n+1), 0).
------------------------------------------------------------------------
