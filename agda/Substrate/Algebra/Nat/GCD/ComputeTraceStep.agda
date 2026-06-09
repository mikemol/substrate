------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.ComputeTraceStep
--
-- The Acc-recursion's RESULT is proof-irrelevant — constructively, within the
-- finite domain of the recursion, with NO funext and NO K. General Acc
-- proof-irrelevance `(p q : Acc R x) → p ≡ q` would need funext (to equate the
-- wrapped functions); but we never compare functions — we only APPLY them at
-- the actual remainders and discharge by the IH. "The step from frontier-2 to
-- frontier-1 is the same step as frontier-1 to frontier": the step is the
-- uniform `construct-wedge`, blind to the accessibility witness.
--
-- This recovers the continued-fraction recurrence ON the exterior
-- `compute-trace` (`cf-step`) — the statement the "compute-trace can't reduce
-- under --without-K" framing wrongly ruled out. (The interior recurrence
-- `ℕ-shape (step …) ≡ quotient … ∷ …` on the EEATrace constructor is refl; this
-- is its exterior twin, holding propositionally via result-irrelevance.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.ComputeTraceStep where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _<_)
open import Substrate.Foundation.List using (_∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.WellFounded using (Acc; acc)
open import Substrate.Algebra.Nat.WellFounded using (<-wellFounded)
open import Substrate.Algebra.Nat.GCD.Wedge using (quotient; remainder; r<b)
open import Substrate.Algebra.Nat.GCD.ConstructWedge using (construct-wedge)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; step)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace-acc; compute-trace)
open import Substrate.Algebra.Wedge.Shape using (ℕ-shape)

-- RESULT-IRRELEVANCE: the worker's output does not depend on the Acc witness.
cta-irr : (a b : ℕ) (p q : Acc _<_ b) →
          compute-trace-acc a b p ≡ compute-trace-acc a b q
cta-irr a zero    p       q       = refl
cta-irr a (suc b) (acc f) (acc g) =
  cong (λ s → proj₁ s , step b w (proj₂ s))
       (cta-irr (suc b) (remainder w) (f (remainder w) (r<b w)) (g (remainder w) (r<b w)))
  where w = construct-wedge a b

-- THE STEP RECURRENCE for any Acc witness: one Euclidean step peels the leading
-- quotient; the tail is the wedge remainder's own trace.
cta-step : (a b : ℕ) (p : Acc _<_ (suc b)) →
  compute-trace-acc a (suc b) p
  ≡ (proj₁ (compute-trace (suc b) (remainder (construct-wedge a b)))
     , step b (construct-wedge a b)
         (proj₂ (compute-trace (suc b) (remainder (construct-wedge a b)))))
cta-step a b (acc rec) =
  cong (λ s → proj₁ s , step b w (proj₂ s))
       (cta-irr (suc b) (remainder w) (rec (remainder w) (r<b w)) (<-wellFounded (remainder w)))
  where w = construct-wedge a b

-- Specialised to the canonical witness `compute-trace` itself uses (definitional
-- on the result type — `<-wellFounded (suc b)` need not even reduce).
compute-trace-step : (a b : ℕ) →
  compute-trace a (suc b)
  ≡ (proj₁ (compute-trace (suc b) (remainder (construct-wedge a b)))
     , step b (construct-wedge a b)
         (proj₂ (compute-trace (suc b) (remainder (construct-wedge a b)))))
compute-trace-step a b = cta-step a b (<-wellFounded (suc b))

-- The continued-fraction recurrence on the EXTERIOR compute-trace.
cf-step : (a b : ℕ) →
  ℕ-shape (proj₂ (compute-trace a (suc b)))
  ≡ quotient (construct-wedge a b)
    ∷ ℕ-shape (proj₂ (compute-trace (suc b) (remainder (construct-wedge a b))))
cf-step a b = cong (λ s → ℕ-shape (proj₂ s)) (compute-trace-step a b)
