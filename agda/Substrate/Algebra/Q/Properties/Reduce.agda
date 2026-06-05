------------------------------------------------------------------------
-- Substrate.Algebra.Q.Properties.Reduce
--
-- Soundness of ℚ reduction: q ≈ℚ reduce q. The reduced fraction has the SAME
-- value (cross-multiplication equal) as the original — the EEA→ℚ functional
-- correspondence is value-preserving. Proven directly from the kept cofactor
-- witnesses (n ≡ qn·g, den ≡ qd·g): cross-multiplication reduces to the ℕ
-- identity n·(den/g) ≡ (n/g)·den.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Properties.Reduce where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Nat.Properties.Mul using (*-assoc; *-comm)
open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Reduce using (reduce; reduce-build)
open import Substrate.Algebra.Q.Reduction using (abs-ℤ)
open import Substrate.Algebra.Nat.GCD using (gcd-ℕ)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)

-- The shared ℕ cross-mult identity, with the cofactor witnesses substituted:
--   n · (den/g) ≡ (n/g) · den.
nat-xmul : (n qn g qd′ d : ℕ) →
           n ≡ qn * g → suc d ≡ suc qd′ * g → n * suc qd′ ≡ qn * suc d
nat-xmul n qn g qd′ d eqn eqd =
  trans (cong (_* suc qd′) eqn)
  (trans (*-assoc qn g (suc qd′))
  (trans (cong (qn *_) (*-comm g (suc qd′)))
         (cong (qn *_) (sym eqd))))

------------------------------------------------------------------------
-- Soundness: q and its reduced form are cross-multiplication equal.
------------------------------------------------------------------------

-- Lemma over the worker (pattern-matches its own witness args, so reduce-build
-- reduces transparently); ≈-canonical specializes it to the gcd witnesses.
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

≈-canonical : (q : ℚ) → q ≈ℚ reduce q
≈-canonical q =
  ≈-build q (gcd-divides-left  (abs-ℤ (num q)) (denominator q))
            (gcd-divides-right (abs-ℤ (num q)) (denominator q))

------------------------------------------------------------------------
-- Worked examples: reduce computes by refl on closed inputs (the cofactor
-- gcd reduces definitionally).
------------------------------------------------------------------------

private
  open import Substrate.Foundation.Eq using (refl)
  -- 2/4 → 1/2
  _ : reduce (mkℚ (+ 2) 3) ≡ mkℚ (+ 1) 1
  _ = refl
  -- -3/6 → -1/2
  _ : reduce (mkℚ (-suc 2) 5) ≡ mkℚ (-suc 0) 1
  _ = refl
  -- already reduced: 1/2 → 1/2
  _ : reduce (mkℚ (+ 1) 1) ≡ mkℚ (+ 1) 1
  _ = refl
