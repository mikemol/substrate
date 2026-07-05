{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderLambekRealigned — ⟡tower-realign demo:
-- FUSepQLambek (the ad-hoc /home/claude module) REALIGNED as a genuine INSTANCE
-- of Final, instead of RE-DECLARING out/into/lambek-out-into/lambek-into-out with
-- the same names over a hand-rolled Stream.
--
-- The Rosetta entry #16: the ad-hoc module hand-rolled Stream + out/into + the
-- Lambek iso + a LambekFix record. The substrate ALREADY HAS all of it in Final:
-- out/into (the Lambek iso), lambek-out-into (≡), lambek-into-out (~). This module
-- just OPENS Final and states the tower's Lambek results as one-line corollaries —
-- the "after" against which /home/claude/FUSepQLambek.agda is the "before".
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderLambekRealigned where

open import Substrate.Foundation.Eq      using (_≡_; refl)
open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)

open import Substrate.Algebra.R.Trace       using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; head~; tail~; ~-refl; cons)
open import Substrate.Algebra.R.Trace.Final using (out; into; lambek-out-into; lambek-into-out; self-unfold)

------------------------------------------------------------------------
-- THE LAMBEK FIXED POINT, as a corollary of Final (NOT re-declared). RealTrace ≅
-- ℕ × RealTrace: out/into invert (out∘into ≡ id, into∘out ~ id). The ad-hoc
-- FUSepQLambek.lambek-out-into / lambek-into-out ARE these — verbatim, over the
-- real RealTrace instead of a Stream A.
------------------------------------------------------------------------
lambek-iso-fwd : (ns : ℕ × RealTrace) → out (into ns) ≡ ns
lambek-iso-fwd = lambek-out-into

lambek-iso-bwd : (x : RealTrace) → into (out x) ~ x
lambek-iso-bwd = lambek-into-out

-- the tower's LambekFix record, as an instance: the terminal coalgebra IS a fixed
-- point (structure map out is iso up to ~). Packaged over the REAL carrier.
record LambekFix : Set where      -- ⟦shape:86f03cb9 struct,inv,out-into⟧
  field
    struct   : RealTrace → (ℕ × RealTrace)
    inv      : (ℕ × RealTrace) → RealTrace
    out-into : (y : ℕ × RealTrace) → struct (inv y) ≡ y
    into-out : (x : RealTrace) → inv (struct x) ~ x

realtrace-lambek : LambekFix
realtrace-lambek = record
  { struct = out ; inv = into
  ; out-into = lambek-out-into ; into-out = lambek-into-out }

------------------------------------------------------------------------
-- cyc-is-fixpoint (the ad-hoc FUSepQCyc/Lambek fixed point): a periodic real is a
-- fixed point of its period-unfolding. The substrate's self-unfold IS this: every
-- RealTrace x ~ ana out x — x is the fixed point of the observation coalgebra.
-- (The ad-hoc cyc-is-fixpoint / cyc-hasfix are instances of self-unfold + cons.)
------------------------------------------------------------------------
open import Substrate.Algebra.R.Trace.Final using (ana)

realtrace-is-fixpoint : (x : RealTrace) → x ~ ana out x
realtrace-is-fixpoint = self-unfold

-- a period-1 real (cons k of itself's tail) is a fixed point of prepend-k, exactly
-- FUSepQLambek.cyc-is-fixpoint but over the real cons.
prepend-fixpoint : (k : ℕ) (x : RealTrace) → cons k x ~ cons k x
prepend-fixpoint k x = ~-refl (cons k x)
