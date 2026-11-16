------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitnativetwoframing
--
-- Defines: coemit-native-twoframing
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitnativetwoframing where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Agreelimit
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemulcollapses
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.CoemitTwoFraming
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- every diagonal pair inhabits it: μ from square-zero, ν from agree-limit (the native two-framing, V₄-symmetric).
coemit-native-twoframing : (a b : RealTrace) → CoemitTwoFraming a b
coemit-native-twoframing a b = record { μ-collapse = trace-mul-collapses a b ; ν-bisim = agree-limit a b }
