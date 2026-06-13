------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim
--
-- B5: round-trips at the GENERATOR level. The equality at which suspended
-- generators are compared is BISIMILARITY — equal heads, bisimilar tails
-- ([[feedback_suspended_generators_not_approximations]]). Round-trips split by
-- how exact the operation is:
--
--   * CF-NATIVE ops (digit bookkeeping) round-trip as ≡, DEFINITIONALLY. `recip`
--     is the multiplicative-inversion involution: for a real > 1 the CF
--     reciprocal is a digit-shift, so 1/(1/x) = x reduces — `recip-invol` by refl.
--   * exp/log round-trip as a BISIMULATION, exp-real(log-real x) ~ x. This is NOT
--     analytic and NOT "in the limit" (a reflex I was corrected on repeatedly): the
--     round-trip identity exp∘log = 1+u is FORMAL, exact per order, proved in
--     `SeriesCancel`; step-inverse generators cancel coinductively in `Cancel`; and
--     a bisimulation IS equality in the terminal coalgebra, the routine dual of
--     induction (`Final.ana-unique`). The reason it is not a one-liner HERE is
--     purely that `exp-real`/`log-real` are defined as two INDEPENDENT windowed
--     series (they never meet), so the literal `~` needs them re-presented as one
--     step-inverse coalgebra morphism — engineering, not a wall. See `SeriesCancel`,
--     `Cancel`, `Final`, `TranscendentalDigits`.
--
-- Three el-atlas exp⊣log strengths, each in its true form: `nedge-atlas` exact
-- discrete bijection (a record), `Atlas.GcdBezout` keep⊣forget, and the
-- continuous one — exact-≡ where CF-native, coinductive bisimulation otherwise.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq  using (_≡_; refl)

open import Substrate.Algebra.R.Trace            using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Ops        using (recip)
open import Substrate.Algebra.R.Trace.Transcendental using (exp-real; log-real)

------------------------------------------------------------------------
-- Bisimilarity: observational equality of suspended generators.
------------------------------------------------------------------------

record _~_ (x y : RealTrace) : Set where
  coinductive
  field head~ : head x ≡ head y
        tail~ : tail x ~ tail y
open _~_ public

~-refl : (x : RealTrace) → x ~ x
head~ (~-refl x) = refl
tail~ (~-refl x) = ~-refl (tail x)

------------------------------------------------------------------------
-- A general CF cons (head k, tail t) — to name a real > 1.
------------------------------------------------------------------------

cons : ℕ → RealTrace → RealTrace
head (cons k x) = k
tail (cons k x) = x

------------------------------------------------------------------------
-- The EXACT round-trip: recip is the multiplicative-inversion involution. On a
-- real > 1 (leading digit ≥ 1), 1/(1/x) = x holds DEFINITIONALLY — the CF
-- reciprocal is a digit-shift (prepend 0 / drop 0), so the two shifts cancel.
-- A genuine adjoint equivalence (self-inverse) on the CF-native chart, by refl.
------------------------------------------------------------------------

recip-invol : (a : ℕ) (t : RealTrace) →
              recip (recip (cons (suc a) t)) ≡ cons (suc a) t
recip-invol a t = refl

------------------------------------------------------------------------
-- The exp/log round-trip (B5 proper) — a BISIMULATION:
--
--   exp-log-roundtrip : (x : RealTrace) → exp-real (log-real x) ~ x
--
-- NOT analytic, NOT "in the limit". Its mathematical content (exp∘log = 1+u) is
-- the FORMAL series identity, exact per order (`SeriesCancel`); the cancellation
-- mechanism is coinductive step-inverse cancellation (`Cancel.bump-cancel`); and
-- the `~` itself is equality in the terminal coalgebra (`Final.ana-unique`, the
-- dual of induction). It is unproven HERE only because `exp-real`/`log-real` are
-- defined as two independent windowed series rather than one step-inverse
-- coalgebra morphism — re-presenting them so is engineering, not a wall. `_~_` is
-- the equality it is stated at; `recip-invol` shows the framework captures genuine
-- round-trips exactly where the operation is CF-native.
------------------------------------------------------------------------
