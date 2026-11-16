------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.TraceLen
--
-- Defines: trace-len
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.TraceDescent.TraceLen where

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace



-- number of EEA steps in a trace.
trace-len : {a b g : QPoly} → PolyEEATrace a b g → ℕ
trace-len (base a)        = zero
trace-len (step d f-lo s) = suc (trace-len s)
