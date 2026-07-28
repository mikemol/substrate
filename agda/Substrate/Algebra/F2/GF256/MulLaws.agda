------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.MulLaws  (was GF256 §AI-6e, part 2)
--
-- The remaining `gmul` ring laws — unit (left/right), zero-absorb (left/right),
-- associativity — TRANSPORTED from the graded field's `_*Q_` laws across the seam
-- `*Q ≡ gmul` (GF256.HornerSeam).  Since `gmul` IS the field multiply, its laws
-- ARE the field's, conjugated by `*Q-is-gmul` (with `one₈ ≡ oneC`, `𝟎ⱽ ≡ 𝟎C` by
-- refl).  This replaces the earlier hand-proofs, each "`_*P_`'s law pulled through
-- `reduce`" — the seam does that pulling once, for every law at once; the bespoke
-- `reduce-*-homˡ` associativity helper is no longer needed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.MulLaws where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ)
open import Substrate.Algebra.F2.Polynomial.Wedge.GUnit.Base using (m-lo)
open import Substrate.Algebra.F2.GF256.Idempotent using (one₈)
open import Substrate.Algebra.F2.GF256.Mul using (gmul)
open import Substrate.Algebra.F2.GF256.HornerSeam using (*Q-is-gmul)
import Substrate.Algebra.Polynomial.Graded.Quotient as Quot
open Quot.Over F₂-CommRing 7 m-lo
  using (_*Q_; *Q-identityˡ; *Q-identityʳ; *Q-zeroˡ; *Q-zeroʳ; *Q-assoc)

gmul-identityˡ : (b : Vector 8) → gmul one₈ b ≡ b
gmul-identityˡ b = trans (sym (*Q-is-gmul one₈ b)) (*Q-identityˡ b)

gmul-identityʳ : (b : Vector 8) → gmul b one₈ ≡ b
gmul-identityʳ b = trans (sym (*Q-is-gmul b one₈)) (*Q-identityʳ b)

gmul-zeroˡ : (b : Vector 8) → gmul 𝟎ⱽ b ≡ 𝟎ⱽ
gmul-zeroˡ b = trans (sym (*Q-is-gmul 𝟎ⱽ b)) (*Q-zeroˡ b)

gmul-zeroʳ : (b : Vector 8) → gmul b 𝟎ⱽ ≡ 𝟎ⱽ
gmul-zeroʳ b = trans (sym (*Q-is-gmul b 𝟎ⱽ)) (*Q-zeroʳ b)

gmul-assoc : (a b c : Vector 8) → gmul (gmul a b) c ≡ gmul a (gmul b c)
gmul-assoc a b c =
  trans (cong (λ z → gmul z c) (sym (*Q-is-gmul a b)))
  (trans (sym (*Q-is-gmul (a *Q b) c))
  (trans (*Q-assoc a b c)
  (trans (*Q-is-gmul a (b *Q c))
         (cong (gmul a) (*Q-is-gmul b c)))))
