------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ComputeTrace
--
-- compute-trace : (a b : ℕ) → Σ ℕ (EEATrace a b).
-- Constructs an EEATrace via Acc-encapsulated recursion on the
-- substrate-native well-foundedness of `_<_` on ℕ. The Acc usage is
-- hidden inside `compute-trace-acc`; downstream code uses the trace
-- structurally.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ComputeTrace where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.Nat.GCD.Wedge using (Wedge; remainder; r<b)
open import Substrate.Algebra.Nat.GCD.ConstructWedge using (construct-wedge)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)

private
  compute-trace-acc :
    (a b : ℕ) → Acc _<_ b → Σ ℕ (EEATrace a b)
  compute-trace-acc a zero    _         = a , base a
  compute-trace-acc a (suc b) (acc rec) =
    let w        = construct-wedge a b
        r-fits   = r<b w
        sub      = compute-trace-acc (suc b) (remainder w) (rec _ r-fits)
        sub-g    = proj₁ sub
        sub-trace = proj₂ sub
    in sub-g , step b w sub-trace

compute-trace : (a b : ℕ) → Σ ℕ (EEATrace a b)
compute-trace a b = compute-trace-acc a b (<-wellFounded b)
