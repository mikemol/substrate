------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Reduce.ApproxBuild
--
-- Defines: ≈-build
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Q.Properties.Reduce; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Reduce.ApproxBuild where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Mul
open import Substrate.Algebra.Z.Int
open import Substrate.Algebra.Z.Int2
open import Substrate.Algebra.Z.Properties.Mul
open import Substrate.Algebra.Q.Denominator
open import Substrate.Algebra.Q.Rat
open import Substrate.Algebra.Q.Equiv
open import Substrate.Algebra.Q.Reduce
open import Substrate.Algebra.Q.Reduction.AbsInt
open import Substrate.Algebra.Q.Reduction.Op3
open import Substrate.Algebra.Q.Reduction.Private
open import Substrate.Algebra.Nat.Divides.Type
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Algebra.Q.Properties.Reduce.NatXmul



------------------------------------------------------------------------
-- Soundness: q and its reduced form are cross-multiplication equal.
------------------------------------------------------------------------

-- Lemma over the worker (pattern-matches its own witness args, so reduce-build
-- reduces transparently); ≈-reduce specializes it to the gcd witnesses.
≈-build : (q : ℚ) {g : ℕ}
          (dl : g ∣ abs-ℤ (num q)) (dr : g ∣ denominator q) →
          q ≈ℚ reduce-build (num q) dl dr
≈-build (mkℚ (+ n) d₋)    (divides qn eqn) (divides (suc qd′) eqd) =
          cong +_ (nat-xmul n qn _ qd′ d₋ eqn eqd)
≈-build (mkℚ (+ n) d₋)    (divides _  _)   (divides zero ())
≈-build (mkℚ (-suc m) d₋) (divides qn eqn) (divides (suc qd′) eqd) =
          trans (cong (λ z → -ℤ (+ z)) (nat-xmul (suc m) qn _ qd′ d₋ eqn eqd))
                (sym (neg-*-left (+ qn) (+ suc d₋)))
≈-build (mkℚ (-suc m) d₋) (divides _  _)   (divides zero ())
