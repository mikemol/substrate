------------------------------------------------------------------------
-- Substrate.Algebra.F1.AsModule.TopF1Module
--
-- Defines: ⊤-F₁-Module
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F1.AsModule; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F1.AsModule.TopF1Module where

open import Substrate.Foundation.Unit
open import Substrate.Algebra.PointedSet
open import Substrate.Algebra.F1.AsModule.F1Module



------------------------------------------------------------------------
-- 2. The trivial F₁-Module (basepoint only).
------------------------------------------------------------------------

⊤-F₁-Module : F₁-Module ⊤
⊤-F₁-Module = Substrate.Algebra.PointedSet.⊤-Pointed
