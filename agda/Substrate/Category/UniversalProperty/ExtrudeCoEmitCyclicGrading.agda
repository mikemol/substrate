{-# OPTIONS --safe --without-K --guardedness #-}
------------------------------------------------------------------------
-- ExtrudeCoEmitCyclicGrading — the THIRD grading axis (operator, ADD 313): finitely-generated/CYCLIC (→ a point
-- → ≡) vs non-finitely-generated/APERIODIC (→ ~). A round-trip is a cycle; cover it → a point. The ret/constant
-- stream is PERIOD-1 (next c (ret a) = c → coemit-trace loops). CofreeDual: the ~-obstruction shrinks to the
-- aperiodic tail. This module NAMES the finitely-generated pole (repeat n = the period-1 cover of a point n) and
-- proves it collapses: repeat m ~ repeat n IFF m ≡ n — the cycle covers to the point, the grading's ≡-end.
------------------------------------------------------------------------
module Substrate.Category.UniversalProperty.ExtrudeCoEmitCyclicGrading where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl)

-- the period-1 cover of a point n: the constant stream repeating n (the finitely-generated pole of the grading).
repeat : ℕ → RealTrace
head (repeat n) = n
tail (repeat n) = repeat n

-- COVER → POINT (the ≡-end of the grading): repeat covers a point, and bisimilarity of covers IS point-equality.
-- forward: equal points give bisimilar covers (the cycle lifts the point ≡ self-similarly, guarded).
cover→ : {m n : ℕ} → m ≡ n → repeat m ~ repeat n
head~ (cover→ p) = p
tail~ (cover→ p) = cover→ p

-- backward: bisimilar covers give equal points (read off the head — the cover collapses to the point).
cover← : {m n : ℕ} → repeat m ~ repeat n → m ≡ n
cover← p = head~ p

-- so the finitely-generated/cyclic pole collapses to ≡ (the point); the aperiodic tail is the ~-obstruction
-- (CofreeDual). The 3rd grading axis: repeat (period-1, ≡-collapsing) … aperiodic (genuine ~).
