------------------------------------------------------------------------
-- Substrate.WitnessTower.EEAUnitBezout
--
-- Ⓢ.eea-unit-bezout — a CONNECTION LEAF wiring node (6) the CF / Rational
-- adjunction (Algebra.R.Trace.RationalAdjunction: reconstruct / reconStep /
-- eea-unit) to node (2) the Bézout/gcd spine (Algebra.Z.Bezout: BezoutℤWitness
-- / bezout-ℤ / step-bezout). The two halves are the SAME EEATrace read through
-- two folds:
--
--   • ℕ×ℕ RECONSTRUCTION (node 6) — `reconstruct` folds the trace with
--     `reconStep q (b , r) = q * b + r , b`, rebuilding the start pair (a, b);
--     `eea-unit` certifies it, by the division equation `wedge-eq` at each step.
--   • Bézout WITNESS (node 2) — `bezout-ℤ = eea-fold {BezoutℤWitness}` folds the
--     SAME trace with `step-bezout`, returning the oriented bridge s·a + t·b = g;
--     its `step-bezout` proof opens with `aeq = cong +_ (wedge-eq w)` — the SAME
--     division equation, read over ℤ.
--
-- CLAIM. At every `step b w rest` both folds consume the same Wedge field
-- `quotient w` as their transition digit (reconStep's q; step-bezout's q), and
-- both are governed by the same `wedge-eq`. So the EEATrace is a fold target for
-- ℕ×ℕ reconstruction AND for the Bézout witness; both are applications of the
-- Euclidean division-equation wedge to different algebras (ℕ×ℕ vs ℤ). The
-- per-step agreement (`reconstruct-step-digit`, by refl) plus the two folds run
-- on one concrete trace (`unit-3-2`, `bezout-3-2`) witness the saturation.
--
-- Zero postulates, --safe --without-K --guardedness (RationalAdjunction is a
-- coinductive-stream importer, so guardedness is infective via reconstruct).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.EEAUnitBezout where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Nat.GCD.Wedge using (remainder) renaming (Wedge to Wedge⟦b7e6a995⟧; quotient to quotient⟦b7e6a995⟧)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace; base; step)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)

-- node (6): the ℕ×ℕ reconstruction fold and its unit.
open import Substrate.Algebra.R.Trace.RationalAdjunction
  using (reconStep; reconstruct; eea-unit)

-- node (2): the Bézout witness and its fold.
open import Substrate.Algebra.Z.Bezout
  using (BezoutℤWitness; bezout-ℤ; step-bezout)

------------------------------------------------------------------------
-- 1. THE SHARED STEP DIGIT. At a `step b w rest`, `reconstruct` applies
--    `reconStep` with the digit `quotient w` — the SAME Wedge field that
--    `step-bezout` names `q`. This is definitional (the fold body), so refl:
--    both folds read their transition digit from the one Wedge.
------------------------------------------------------------------------

reconstruct-step-digit :
  {a g : ℕ} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b)) (rest : EEATrace (suc b) (remainder w) g) →
  reconstruct (step b w rest) ≡ reconStep (quotient⟦b7e6a995⟧ w) (reconstruct rest)
reconstruct-step-digit b w rest = refl

------------------------------------------------------------------------
-- 2. THE SAME TRANSITION LAW. `step-bezout` transforms the recursive Bézout
--    witness through the SAME Wedge — its `q` is `quotient w` as well. Pinning
--    the type makes the shared (b , w) interface explicit: both step functions
--    take a `Wedge a (suc b)` and read `quotient w` off it.
------------------------------------------------------------------------

bezout-step-shape :
  {a g : ℕ} (b : ℕ) (w : Wedge⟦b7e6a995⟧ a (suc b)) →
  BezoutℤWitness (suc b) (remainder w) g → BezoutℤWitness a (suc b) g
bezout-step-shape = step-bezout

------------------------------------------------------------------------
-- 3. THE TWO FOLDS ON ONE TRACE. t = the EEA of (3, 2). The reconstruction fold
--    rebuilds (3, 2) exactly (`eea-unit`); the Bézout fold returns the bridge
--    s·3 + t·2 = gcd(3,2). Both are folds of this single t — the saturation.
------------------------------------------------------------------------

t : EEATrace 3 2 (gcd-ℕ 3 2)
t = gcd-trace 3 2

-- node (6) fold target: reconstruction = (3, 2).
unit-3-2 : reconstruct t ≡ (3 , 2)
unit-3-2 = eea-unit t

-- node (2) fold target: the Bézout witness, same t.
bezout-3-2 : BezoutℤWitness 3 2 (gcd-ℕ 3 2)
bezout-3-2 = bezout-ℤ t
