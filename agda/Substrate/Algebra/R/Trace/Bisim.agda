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
--   * TRANSCENDENTAL exp/log round-trip as a BISIMULATION, exp-real(log-real x) ~ x,
--     and that is NOT provable from the windowed generators alone — it needs the
--     analytic convergence (digit stability of the growing window + exp∘log = id).
--     Stated below as the open goal; the honest shape of the continuous facet.
--
-- Three el-atlas exp⊣log strengths, each in its true form: `nedge-atlas` exact
-- discrete bijection (a record), `Atlas.GcdBezout` keep⊣forget, and the
-- continuous one — exact-≡ where CF-native, bisimulation-at-the-limit otherwise.
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
-- The TRANSCENDENTAL round-trip (B5 proper) — a BISIMULATION, and OPEN: it is
-- not provable from the windowed exp/log alone but needs the analytic
-- convergence (digit stability + exp∘log = id). The honest capstone goal:
--
--   exp-log-roundtrip : (x : RealTrace) → exp-real (log-real x) ~ x
--
-- `_~_` is the equality it is stated at; `recip-invol` shows the framework
-- captures genuine round-trips exactly where the operation is exact.
------------------------------------------------------------------------
