------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.TraceLenBound
--
-- Defines: trace-len-bound
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.TraceLenBound where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Product
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
open import Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.Qdim
open import Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.TraceLen



-- TERMINATION: the EEA trace length is bounded by the divisor dimension — the
-- well-founded measure for B-EEA-COMPUTE, = the allegory Refinement chain (ALG-7)
-- descent realized for F₂[x].
trace-len-bound : {a b g : QPoly} (t : PolyEEATrace a b g) → trace-len t ≤ qdim b
trace-len-bound (base a)        = z≤n
trace-len-bound (step d f-lo s) = s≤s (trace-len-bound s)
