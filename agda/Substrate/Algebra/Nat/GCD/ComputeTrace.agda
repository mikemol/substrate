------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ComputeTrace
--
-- compute-trace : (a b : ℕ) → Σ ℕ (EEATrace a b).
-- Constructs an EEATrace via Acc-encapsulated recursion on the
-- substrate-native well-foundedness of `_<_` on ℕ. Downstream code uses
-- the trace structurally.
--
-- `compute-trace-acc` (the Acc worker) is EXPOSED: its result is independent
-- of WHICH Acc witness it is handed (the step is the uniform `construct-wedge`,
-- Acc-proof-blind). That result-irrelevance — and the step recurrence it
-- yields — are proved in `ComputeTrace.Step`. (General Acc proof-irrelevance
-- needs funext; result-irrelevance does NOT — it is structural induction on
-- the accessibility proofs, applying the wrapped functions pointwise.)
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

-- The accessibility-driven worker. (Exposed for ComputeTrace.Step; ordinary
-- callers use `compute-trace`.)
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
