------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Cancel
--
-- SUSPENDED GENERATORS CANCEL — coinductively, without computing the trace.
--
-- The correction (user): "holds only in the limit" classically means "compute
-- the entire infinite trace". But constructively the round-trip is a coinductive
-- BISIMULATION — a FINITE proof of an INFINITE equality. You never force the
-- trace; you give the bisimulation and the step-inverse cancels at every depth.
-- So a round-trip of two INFINITE step-inverse generators is structural, exactly
-- like `recip-invol` (finite), just at infinite depth — no convergence, no limit
-- computation. The Lindemann–Weierstrass obstruction is about FORCING, which the
-- coinductive proof never does. ([[feedback_suspended_generators_not_approximations]];
-- [[feedback_trace_inversion_vs_transcendental_limit]] is corrected by this.)
--
-- Demonstrated on `bump`/`unbump` (add / subtract k at every digit — reversible
-- infinite generators). `unbump k (bump k x) ~ x` holds by coinduction; the tail
-- case is the corecursive call, the head case the per-step inverse. The exp⊣log
-- round-trip is THIS shape once exp/log are co-defined step-inverse (the Wedge-
-- chain: log decomposes keeping residue, exp replays) — the never-discard-residue
-- spine.
--
-- (I once filed "does it compute the RIGHT exp/log values" as a SEPARATE analytic
-- obligation. That was the same reflex, corrected later: the value-IDENTITY
-- exp∘log = 1+u is itself FORMAL (`SeriesCancel`), and "numerically equals a
-- transcendental" is the binary-digit FORCING trap, dissolved by the generator
-- basis (`TranscendentalDigits`). No separate analytic matter survives.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Cancel where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_)
open import Substrate.Foundation.Eq  using (_≡_; refl)

open import Substrate.Algebra.R.Trace       using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~)
open import Substrate.Algebra.R.Trace.StreamMap using (mapT)

------------------------------------------------------------------------
-- Two reversible INFINITE generators: add / subtract k at every digit.
-- ⟡dedup.tree: both are instances of the lifted stream map `mapT` — the same
-- head-function family Ops.addℕ shares, here with the RECURSE (map-all) tail.
------------------------------------------------------------------------

bump : ℕ → RealTrace → RealTrace
bump k = mapT (k +_)

unbump : ℕ → RealTrace → RealTrace
unbump k = mapT (_∸ k)

------------------------------------------------------------------------
-- The per-step inverse: (k + n) ∸ k = n.
------------------------------------------------------------------------

+∸-cancel : (k n : ℕ) → (k + n) ∸ k ≡ n
+∸-cancel zero    n = refl
+∸-cancel (suc k) n = +∸-cancel k n

------------------------------------------------------------------------
-- THE CANCELLATION: unbump undoes bump at every depth — a coinductive
-- bisimulation, a finite proof of an infinite equality. No trace computed.
------------------------------------------------------------------------

bump-cancel : (k : ℕ) (x : RealTrace) → unbump k (bump k x) ~ x
head~ (bump-cancel k x) = +∸-cancel k (head x)
tail~ (bump-cancel k x) = bump-cancel k (tail x)
