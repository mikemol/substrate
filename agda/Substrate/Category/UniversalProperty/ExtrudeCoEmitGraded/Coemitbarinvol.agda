------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarinvol
--
-- Defines: coemit-bar₂-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitbarinvol where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Xor2involutive
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar2
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong


coemit-bar₂-invol : (r : RealTrace) → bar₂ (bar₂ r) ~ r
head~ (coemit-bar₂-invol r) = xor2-involutive (RealTrace.head r)
tail~ (coemit-bar₂-invol r) = coemit-bar₂-invol (RealTrace.tail r)
