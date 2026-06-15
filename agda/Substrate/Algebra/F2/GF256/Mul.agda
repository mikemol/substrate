------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Mul  (was GF256 §AI-6e, part 1)
--
-- `gmul a b = reduce-mod-m (a *P b)` — a THIN SKIN over `Polynomial.RingLaws`'
-- `_*P_`. The additive-side ring laws (commutativity, both distributivities)
-- are `_*P_`'s laws PULLED THROUGH the `reduce` homomorphism (§Reduce/§Expand);
-- the graded length-`subst`s vanish at the fixed carrier 8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Mul where

open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_; 𝟎ⱽ; +ⱽ-identityˡ;
  +ⱽ-identityʳ; *ₛ-identityˡ; *ₛ-absorbˡ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Nat.Properties renaming (+-comm to +ℕ-comm)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Algebra.F2.Polynomial.RingLaws using (*P-comm; *P-distribʳ; *P-distribˡ)
open import Substrate.Algebra.F2.GF256.Xtime using (xtime)
open import Substrate.Algebra.F2.GF256.Reduce using (reduce-mod-m; reduce-+ⱽ; *ₛ-zeroʳ)
open import Substrate.Algebra.F2.GF256.Expand using (hsum; xtime-zero; reduce-subst)
open import Substrate.Algebra.F2.GF256.Idempotent using (one₈)

hsum-zero : ∀ {n} (r : Vector 8) → hsum (𝟎ⱽ {n}) r ≡ 𝟎ⱽ
hsum-zero {zero}  r = refl
hsum-zero {suc n} r = trans (cong₂ _+ⱽ_ (*ₛ-absorbˡ r) (hsum-zero {n} (xtime r))) (+ⱽ-identityˡ 𝟎ⱽ)

hsum-zeroʳ : ∀ {n} (p : Polynomial n) → hsum p 𝟎ⱽ ≡ 𝟎ⱽ
hsum-zeroʳ []      = refl
hsum-zeroʳ (a ∷ p) =
  trans (cong₂ _+ⱽ_ (*ₛ-zeroʳ a) (trans (cong (hsum p) xtime-zero) (hsum-zeroʳ p))) (+ⱽ-identityˡ 𝟎ⱽ)

hsum-one-id : (r : Vector 8) → hsum one₈ r ≡ r
hsum-one-id r = trans (cong₂ _+ⱽ_ (*ₛ-identityˡ r) (hsum-zero {7} (xtime r))) (+ⱽ-identityʳ r)

gmul : Vector 8 → Vector 8 → Vector 8
gmul a b = reduce-mod-m (a *P b)

gmul-comm : (a b : Vector 8) → gmul a b ≡ gmul b a
gmul-comm a b = trans (cong reduce-mod-m (*P-comm a b)) (reduce-subst (+ℕ-comm 8 8) (b *P a))

gmul-distribˡ : (a b c : Vector 8) → gmul a (b +ⱽ c) ≡ gmul a b +ⱽ gmul a c
gmul-distribˡ a b c = trans (cong reduce-mod-m (*P-distribˡ a b c)) (reduce-+ⱽ (a *P b) (a *P c))

gmul-distribʳ : (a b c : Vector 8) → gmul (a +ⱽ b) c ≡ gmul a c +ⱽ gmul b c
gmul-distribʳ a b c = trans (cong reduce-mod-m (*P-distribʳ a b c)) (reduce-+ⱽ (a *P c) (b *P c))
