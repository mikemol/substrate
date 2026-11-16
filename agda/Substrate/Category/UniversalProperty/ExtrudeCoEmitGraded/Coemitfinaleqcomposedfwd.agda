------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfinaleqcomposedfwd
--
-- Defines: coemit-final-eq-composed-fwd
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitfinaleqcomposedfwd where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Coemitagreesisbisimfwd
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Perspectivefinite
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.GradingAxis
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)


-- (2) coemit-final-eq-composed: the final ≡ (~) is the COALGEBRA OF μ — composed from the 3 S₃-connected finite
--     perspectives. The finite μν-perspective (take n) at ALL depths ⟺ ~ (the finite prefixes COMPOSE to the final ≡).
--     So ~ is NOT a carrier-equality but the LIMIT of the finite (μ) perspectives — the coalgebra of μ realizing ν.
coemit-final-eq-composed-fwd : (r t : RealTrace)
                             → ((n : ℕ) → perspective-finite μν-axis t n ≡ perspective-finite μν-axis r n) → t ~ r
coemit-final-eq-composed-fwd = coemit-agrees-is-bisim-fwd
