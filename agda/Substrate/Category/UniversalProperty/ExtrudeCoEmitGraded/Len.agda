------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Len
--
-- Defines: len
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Len where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Algebra.R.Trace
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitMonad ℕ
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitViaTrace.CoemitTrace
open import Substrate.Category.Allegory.Refinement.Preamble
open import Substrate.Algebra.R.Trace.Bisim.Trans
open import Substrate.Category.UniversalProperty.ExtrudeBisimUpTo
open import Substrate.Algebra.R.Trace.Bisim.Refl
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Fin
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Anon2
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Tracemul
open import Substrate.Foundation.Eq
open import Substrate.Groups.SemidirectProduct.Stab   -- Stab X σ = applyₛ σ X ≡ X (σ FIXES X)
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans


------------------------------------------------------------------------
-- The ORBIT is the COALGEBRA of the LEAST FIXED POINT μ (operator refines 334: NOT the fixed point itself, and the
-- CARRIER is the COMPOSITION — RealTrace acting on RealTrace via the coalgebraic morphism = trace-mul, not a
-- single Φ_T step). μΦ = ⋃ₙ Φⁿ⊥ = all FINITE traces (TraceKleeneColimit, the algebraic/finite side). Each of the 3
-- axes is a FINITE perspective (a μ-projection: bounded-depth view); the orbit (S₃-transitive) is the coalgebra of μ.
------------------------------------------------------------------------
-- (1) coemit-perspective-finite: each axis = a FINITE (μ) perspective. The finite datum per axis (a bounded view):
--     μν = the finite prefix (take n : List ℕ); head-tail = the finite head (one ℕ); cyc-aper = a finite depth n.
-- a local length (Foundation.List defers it) — the finiteness measure.
len : List ℕ → ℕ
len []       = 0
len (_ ∷ xs) = suc (len xs)
