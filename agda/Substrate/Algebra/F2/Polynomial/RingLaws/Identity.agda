------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Identity  (was RingLaws §AI-7d)
--
-- The multiplicative identity (graded / length-agnostic form). The "one" of
-- F₂[x] is the leading-𝟙 basis vector; multiplying by it preserves every
-- coefficient. (A length-1 `[𝟙]` is the n=0 case.) This is the coefficient-
-- level identity that reduce-mod-m (AI-6) carries down to GF(2⁸); a fixed-
-- carrier `[𝟙] *P q ≡ q` is NOT well-typed here (*P is length-additive: 1+m ≠ m).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Identity where

open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; trans)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (nth-*P)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Basis using (convCoeff-basis-fz)

*P-identityˡ-nth : ∀ {n m} (q : Polynomial m) (k : ℕ)
                 → nth (basis {suc n} fzero *P q) k ≡ nth q k
*P-identityˡ-nth q k = trans (nth-*P (basis fzero) q k) (convCoeff-basis-fz q k)
