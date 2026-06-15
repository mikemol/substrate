------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.MulLaws  (was GF256 §AI-6e, part 2)
--
-- The remaining `gmul` ring laws: unit (left/right), zero-absorb (left/right),
-- and associativity. Associativity needs `reduce-*-homˡ` (reduce in the LEFT
-- multiplicative slot, got by commuting into §Idempotent's right-slot hom);
-- everything is again `_*P_`'s law pulled through `reduce`, substs vanishing at 8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.MulLaws where

open import Substrate.Foundation.Nat.Properties renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; 𝟎ⱽ)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Algebra.F2.Polynomial.RingLaws using (*P-comm; *P-assoc)
open import Substrate.Algebra.F2.GF256.Reduce using (reduce-mod-m)
open import Substrate.Algebra.F2.GF256.Expand using (hsum; reduce-subst; reduce-𝟎ⱽ; reduce-*P-expand)
open import Substrate.Algebra.F2.GF256.Idempotent using (one₈; reduce-idempotent; reduce-*-hom)
open import Substrate.Algebra.F2.GF256.Mul using (gmul; gmul-comm; hsum-one-id; hsum-zero; hsum-zeroʳ)

gmul-identityˡ : (b : Vector 8) → gmul one₈ b ≡ b
gmul-identityˡ b =
  trans (reduce-*P-expand one₈ b) (trans (hsum-one-id (reduce-mod-m b)) (reduce-idempotent b))

gmul-identityʳ : (b : Vector 8) → gmul b one₈ ≡ b
gmul-identityʳ b = trans (gmul-comm b one₈) (gmul-identityˡ b)

gmul-zeroˡ : (b : Vector 8) → gmul 𝟎ⱽ b ≡ 𝟎ⱽ
gmul-zeroˡ b = trans (reduce-*P-expand (𝟎ⱽ {8}) b) (hsum-zero {8} (reduce-mod-m b))

gmul-zeroʳ : (b : Vector 8) → gmul b 𝟎ⱽ ≡ 𝟎ⱽ
gmul-zeroʳ b = trans (reduce-*P-expand b (𝟎ⱽ {8}))
                     (trans (cong (hsum b) (reduce-𝟎ⱽ {8})) (hsum-zeroʳ b))

reduce-*-homˡ : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
              → reduce-mod-m (reduce-mod-m p *P q) ≡ reduce-mod-m (p *P q)
reduce-*-homˡ {n} {m} p q =
  trans (cong reduce-mod-m (*P-comm (reduce-mod-m p) q))
  (trans (reduce-subst (+ℕ-comm m 8) (q *P reduce-mod-m p))
  (trans (sym (reduce-*-hom q p))
  (trans (cong reduce-mod-m (*P-comm q p)) (reduce-subst (+ℕ-comm n m) (p *P q)))))

gmul-assoc : (a b c : Vector 8) → gmul (gmul a b) c ≡ gmul a (gmul b c)
gmul-assoc a b c =
  trans (reduce-*-homˡ (a *P b) c)
  (trans (sym (reduce-subst (+ℕ-assoc 8 8 8) ((a *P b) *P c)))
  (trans (cong reduce-mod-m (*P-assoc a b c)) (reduce-*-hom a (b *P c))))
