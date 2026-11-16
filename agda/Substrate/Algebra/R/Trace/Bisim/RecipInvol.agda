------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Bisim.RecipInvol
--
-- Defines: recip-invol
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.R.Trace.Bisim; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Bisim.RecipInvol where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Algebra.R.Trace
open import Substrate.Algebra.R.Trace.Ops
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.TransSym
open import Substrate.Algebra.R.Trace.Bisim.Op
open import Substrate.Algebra.R.Trace.Bisim.Cons



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
