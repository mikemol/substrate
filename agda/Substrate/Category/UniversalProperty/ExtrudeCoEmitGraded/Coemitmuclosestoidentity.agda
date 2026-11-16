------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuclosestoidentity
--
-- Defines: coemit-mu-closes-to-identity
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitmuclosestoidentity where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfinaleqcomposedfwd
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- LEAST-FIXED-POINT-AS-HODGE-IDENTITY: the finite (μ) perspectives — the least fixed point — CLOSE into the
-- identity. Each finite perspective carries a genuine ≡ (take n t ≡ take n r); their TOTALITY is the trace ≡ (~).
-- So the identity on the ν-carrier is the μ-perspectives' totality: μ closes to the Hodge identity.
coemit-mu-closes-to-identity : (r t : RealTrace)
                             → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n)
                             → t ~ r
coemit-mu-closes-to-identity = coemit-final-eq-composed-fwd
