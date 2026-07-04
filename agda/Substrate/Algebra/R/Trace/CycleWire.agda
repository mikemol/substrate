{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.CycleWire — ⟡N1b-Real-wire. Lands S5Real's
-- periodic-CF (regress) constructor `cycle` onto the substrate's OWN
-- RealTrace, and proves it reproduces the substrate's `twos` = [2̄]
-- BY BISIMULATION (Bisim._~_). So the regress verdict — a productive real
-- built from a finite period (S5Real, ADD 46) — IS the substrate's coinductive
-- RealTrace: finite ⇒ ℚ, productive-periodic ⇒ ℝ, one machinery.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.CycleWire where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail; take; twos)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)

------------------------------------------------------------------------
-- cycle: the periodic-CF constructor over the substrate's RealTrace, from a
-- finite period (x₀ ∷ xs). Guarded corecursion; the tail loops to the period
-- start. THIS is the regress verdict's productive real.
------------------------------------------------------------------------
cycle-go : ℕ → List ℕ → List ℕ → RealTrace
head (cycle-go x₀ xs [])       = x₀
tail (cycle-go x₀ xs [])       = cycle-go x₀ xs xs
head (cycle-go x₀ xs (y ∷ ys)) = y
tail (cycle-go x₀ xs (y ∷ ys)) = cycle-go x₀ xs ys

cycle : ℕ → List ℕ → RealTrace
cycle x₀ xs = cycle-go x₀ xs (x₀ ∷ xs)

------------------------------------------------------------------------
-- THE WIRE: cycle 2 [] ~ twos (the substrate's [2̄]), by BISIMULATION. Both
-- have head 2 and a tail that loops to themselves; the bisimulation is
-- coinductive. This lands S5Real's cycle on the substrate's own periodic real.
------------------------------------------------------------------------
cycle2 : RealTrace
cycle2 = cycle 2 []

-- cycle 2 [] steps to cycle-go 2 [] [] which has head 2, tail cycle-go 2 [] [].
-- So cycle-go 2 [] [] ~ twos, and cycle2 ~ twos follows.
cyclego2~twos : cycle-go 2 [] [] ~ twos
head~ cyclego2~twos = refl
tail~ cyclego2~twos = cyclego2~twos

cycle2~twos : cycle2 ~ twos
head~ cycle2~twos = refl
tail~ cycle2~twos = cyclego2~twos

------------------------------------------------------------------------
-- and the finite observation agrees definitionally (take is fuel-recursive):
-- take n (cycle 2 []) ≡ take n twos for any n — checked at n = 4.
------------------------------------------------------------------------
take4-agrees : take 4 cycle2 ≡ take 4 twos
take4-agrees = refl

-- the period reproduces (S5Real.take-period, on the substrate's take). take-len
-- takes as many digits as the period length, reproducing it.
take-len : List ℕ → RealTrace → List ℕ
take-len []       _ = []
take-len (_ ∷ zs) r = head r ∷ take-len zs (tail r)

take-period-go : (x₀ : ℕ) (xs ys : List ℕ)
               → take-len ys (cycle-go x₀ xs ys) ≡ ys
take-period-go x₀ xs []       = refl
take-period-go x₀ xs (y ∷ ys) = cong (y ∷_) (take-period-go x₀ xs ys)
