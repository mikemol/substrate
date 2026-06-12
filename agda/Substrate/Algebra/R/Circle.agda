------------------------------------------------------------------------
-- Substrate.Algebra.R.Circle
--
-- The universal cover  ℝ → S¹ = ℝ/ℤ  (in TURNS), bridging the substrate-ℝ arc
-- (RealTrace) to the circle. S¹ is "ℝ on a loop"; the cover wraps the real angle
-- onto the loop by dropping the integer part (a₀ → 0) — each real maps to its
-- position in [0,1), and the integer turns are the deck group (the loop
-- identification). ([[feedback_transcendental_phase_is_loop_fact]].)
--
-- This makes e^{iπ}=−1 a LOOP fact, not an analytic limit. In turns the period is
-- 1 and π is just ½ (rational — the "transcendence" was a radian artifact). The
-- HALF-PERIOD (½ turn) is the ANTIPODE, the order-2 element of S¹; e^{iπ} = that
-- antipode = −1, and e^{2iπ}=1 is "the half-turn doubles to the identity". Its
-- discrete realization is already PROVED in Logic.Evidence.Verdict.Phase —
-- `negBoth` (the −id antipode, the F₂ shadow of the rotation via
-- NedgeShadow.recode) with `negBoth-invol : negBoth² = id`. The cover here lifts
-- exactly that; the continuous angles it adds are only WHERE-on-the-loop, which
-- e^{iπ}=−1 (living in ℤ/2 ⊂ S¹) does not need.
--
-- (Layering: this stays in Algebra.R — the phase/antipode is referenced, not
-- imported, since Logic.Evidence sits above Algebra.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Circle where

open import Substrate.Foundation.Nat using (ℕ; zero)
open import Substrate.Foundation.Eq  using (_≡_; refl)

open import Substrate.Algebra.R.Trace     using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Ops using (cons0; addℕ)

------------------------------------------------------------------------
-- The cover map ℝ → S¹: wrap the angle onto the loop (drop the integer part).
------------------------------------------------------------------------

toS¹ : RealTrace → RealTrace
toS¹ x = cons0 (tail x)

------------------------------------------------------------------------
-- It LANDS on the loop: the S¹ position is a fractional turn (leading digit 0).
------------------------------------------------------------------------

toS¹-loop : (x : RealTrace) → head (toS¹ x) ≡ 0
toS¹-loop x = refl

------------------------------------------------------------------------
-- It is a RETRACTION onto S¹: wrapping an S¹ point again is the identity.
------------------------------------------------------------------------

toS¹-idem : (x : RealTrace) → toS¹ (toS¹ x) ≡ toS¹ x
toS¹-idem x = refl

------------------------------------------------------------------------
-- THE DECK TRANSFORMATION — the loop itself: adding integer turns (the integer
-- part) does NOT move the S¹ position. This is the quotient ℝ → ℝ/ℤ: the integer
-- turns are identified. (`addℕ k` = + k turns; `toS¹` collapses them.)
------------------------------------------------------------------------

toS¹-winding : (k : ℕ) (x : RealTrace) → toS¹ (addℕ k x) ≡ toS¹ x
toS¹-winding k x = refl
