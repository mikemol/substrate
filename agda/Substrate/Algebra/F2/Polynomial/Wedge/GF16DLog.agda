------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.GF16DLog
--
-- The discrete-log inverse at GF(2⁴) = F₂[x]/(x⁴+x+1), computed in the
-- DIVISION REGIME — the resolution of the GF(2⁴)/GF(2⁸) `g^order` wall.
--
-- The wall: the antilog by iterated FULL multiplication (`gx *Q gpow n`) builds
-- a deep nested `*Q` term whose normal form grows EXPONENTIALLY in depth — x⁴ is
-- free, x⁸ needs ~1.5GB, x¹⁵ OOMs. Measured; it is why the substrate's other
-- reflections are division-based, not multiplication-chains.
--
-- The fix (user's insight: change the computation's REGIME via the log/exp view —
-- "orthogonal-magnitude 15 at real-magnitude 1, like a root of unity"): compute
-- the antilog as `xpow n oneC = ytimeⁿ oneC` — multiply-by-x `n` times, each step
-- staying degree < 4 (BOUNDED magnitude, no deep term). `x¹⁵ mod m ≡ 1` is then a
-- cheap `refl`, and the inverse `gᵏ · g^(15−k) ≡ 1` is one small `*Q` per element.
--
-- Same field fact, two regimes — the codec/log view is what licenses computing it
-- in the cheap one. Complements `GF4DLog` (GF(4), ℤ/3 enumeration) and the EEA
-- face (`GF16Inverse`). The GENERAL homomorphism `gᵏ·gʲ ≡ g^(k+j)` (which would
-- give GF(2⁸) without per-element enumeration) needs `ytime`-commutes-with-`*Q`
-- — rostered. Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.GF16DLog where

open import Substrate.Foundation.Nat using (ℕ; _∸_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as D

-- GF(2⁴) = F₂[x]/(x⁴+x+1); x is primitive (multiplicative order 15).
m-lo₄ : Vec F2.F₂ 4
m-lo₄ = F2.𝟙 ∷ F2.𝟙 ∷ F2.𝟘 ∷ F2.𝟘 ∷ []

open D.Over F₂-CommRing 3 m-lo₄ using (Poly; _*Q_; oneC; xpow)

-- the antilog g^· in the DIVISION regime: x^n mod m = ytimeⁿ oneC (bounded magnitude).
gpow : ℕ → Poly 4
gpow n = xpow n oneC

-- THE ANCHOR (the former OOM wall): x^15 ≡ 1, cheap `refl` in this regime.
order15 : gpow 15 ≡ oneC
order15 = refl

-- the discrete-log inverse: inv(gᵏ) = g^(15−k) — additive negation in the exponent.
dinv : ℕ → Poly 4
dinv k = gpow (15 ∸ k)

------------------------------------------------------------------------
-- The inverse law per element: gᵏ · g^(15−k) ≡ 1. Exponents 1..14 (paired by
-- the involution k ↔ 15−k, so 7 pairs cover all); exponent 0 is the identity
-- (g⁰ = 1, self-inverse). Each is ONE small `*Q` on reduced operands — cheap.
------------------------------------------------------------------------

inv-1·14 : gpow 1 *Q gpow 14 ≡ oneC ; inv-1·14 = refl
inv-2·13 : gpow 2 *Q gpow 13 ≡ oneC ; inv-2·13 = refl
inv-3·12 : gpow 3 *Q gpow 12 ≡ oneC ; inv-3·12 = refl
inv-4·11 : gpow 4 *Q gpow 11 ≡ oneC ; inv-4·11 = refl
inv-5·10 : gpow 5 *Q gpow 10 ≡ oneC ; inv-5·10 = refl
inv-6·9  : gpow 6 *Q gpow 9  ≡ oneC ; inv-6·9  = refl
inv-7·8  : gpow 7 *Q gpow 8  ≡ oneC ; inv-7·8  = refl

-- and via the `dinv` function (its inverse-law for a representative element):
dinv-law-7 : gpow 7 *Q dinv 7 ≡ oneC ; dinv-law-7 = refl
