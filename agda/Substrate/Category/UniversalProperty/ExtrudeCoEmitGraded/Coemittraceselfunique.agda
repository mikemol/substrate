------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceselfunique
--
-- Defines: coemit-trace-self-unique
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceselfunique where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Final.AnaUnique
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemittraceunique
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


-- a GENUINE use of coemit-trace-unique: coemit-trace ITSELF trivially matches (the ≡-conditions ARE ana-head/tail,
-- refl) — the uniqueness says coemit-trace is THE ≡-morphism; any ~-variant (unfold, Lambek) is ~ it by ~-transitivity.
coemit-trace-self-unique : (c : CoEmit ℕ) → coemit-trace c ~ coemit-trace c
coemit-trace-self-unique = coemit-trace-unique coemit-trace (λ _ → refl) (λ _ → refl)
