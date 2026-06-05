------------------------------------------------------------------------
-- Substrate.Algebra.Q.Reduce
--
-- ℚ reduction to lowest terms — the EEA→ℚ functional correspondence.
--
-- "We never discard residue": the cofactor num/gcd and den/gcd are NOT a new
-- division — they are the witness quotients already kept by the gcd-divisibility
-- proofs (Nat.GCD.GcdDivides{Left,Right} : gcd ∣ a = `divides q (a ≡ q*gcd)`).
-- `reduce` projects those kept residues; soundness (q ≈ℚ reduce q) lives in
-- Q.Properties.Reduce. (Supersedes the "deferred — needs ℤ÷ℕ" note in
-- Q.Reduction.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Reduce where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; num; den-1; denominator)
open import Substrate.Algebra.Q.Reduction using (abs-ℤ)
open import Substrate.Algebra.Nat.Divides using (_∣_; divides)
open import Substrate.Algebra.Nat.GCD.GcdDividesLeft using (gcd-divides-left)
open import Substrate.Algebra.Nat.GCD.GcdDividesRight using (gcd-divides-right)

-- Reattach the sign of the original numerator to a magnitude.
sign-of : ℤ → ℕ → ℤ
sign-of (+ _)    n = + n
sign-of (-suc _) n = -ℤ (+ n)

-- Worker taking the cofactor witnesses EXPLICITLY (ordinary pattern match, so it
-- reduces transparently in proofs — unlike a `with`-defined reduce). The den
-- cofactor's 0 case forces den ≡ 0, absurd.
reduce-build : ℤ → {a d g : ℕ} → g ∣ a → g ∣ suc d → ℚ
reduce-build sgn (divides qn _) (divides (suc qd′) _) = mkℚ (sign-of sgn qn) qd′
reduce-build sgn (divides _  _) (divides zero    ())

-- reduce q = (sign(num q) · |num q|/g) / (den/g), where g = gcd(|num q|, den).
-- The cofactors are the kept divisibility witnesses — no new division.
reduce : ℚ → ℚ
reduce q = reduce-build (num q)
             (gcd-divides-left  (abs-ℤ (num q)) (denominator q))
             (gcd-divides-right (abs-ℤ (num q)) (denominator q))
