------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Transcendental
--
-- exp and log as SUSPENDED GENERATORS — `RealTrace → RealTrace`, not
-- `RealTrace → List ℕ` ([[feedback_suspended_generators_not_approximations]]).
-- The List forms (`exp-cf`, `log-cf`) are what you get by FORCING the generator
-- to a window; these are the generators themselves.
--
-- Each output digit k is forced on demand from a window growing with k (here
-- 3+k), assembled by `unfold`. Productive — `unfold` of a TOTAL step — and
-- fuel-free: the window is the OUTPUT INDEX, which is structural
-- ([[feedback_finite_window_constructive_lem]]). (Digit stability across the
-- growing window is the convergence content; the round-trip exp(log x) ~ x is a
-- coinductive bisimulation on the spliced generators — B5.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Transcendental where

open import Substrate.Foundation.Nat     using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List    using (List; []; _∷_)
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Algebra.R.Trace        using (RealTrace)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Exp    using (exp-cf)
open import Substrate.Algebra.R.Trace.Log    using (log-cf)

-- index into a CF-digit list (0 past the end).
nth : ℕ → List ℕ → ℕ
nth _       []       = 0
nth zero    (d ∷ _)  = d
nth (suc k) (_ ∷ ds) = nth k ds

-- exp / log as RealTrace generators: the k-th digit from a (3+k)-window.
exp-real : RealTrace → RealTrace
exp-real x = unfold (λ k → (nth k (exp-cf (3 + k) (3 + k) x) , suc k)) 0

log-real : RealTrace → RealTrace
log-real x = unfold (λ k → (nth k (log-cf (3 + k) (3 + k) x) , suc k)) 0
