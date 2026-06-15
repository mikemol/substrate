------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Nth  (was RingLaws §AI-7 base)
--
-- ℕ-indexed coefficient extraction `nth` (𝟘 out of range) and its
-- homomorphism lemmas: nth commutes with replicate/subst/pad-end/x-shift,
-- and is additive (`nth-+ⱽ`) and scalar-linear (`nth-*ₛ`). The base of the
-- whole coefficient calculus.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Nth where

open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_; _·_; ·-absorbʳ)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; x-shift; pad-end)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong₂; subst)

nth : ∀ {n} → Polynomial n → ℕ → F₂
nth []      _       = 𝟘
nth (x ∷ _) zero    = x
nth (_ ∷ v) (suc i) = nth v i

nth-replicate : (k i : ℕ) → nth (replicate k 𝟘) i ≡ 𝟘
nth-replicate zero    _       = refl
nth-replicate (suc _) zero    = refl
nth-replicate (suc k) (suc i) = nth-replicate k i

nth-subst : ∀ {m n} (eq : m ≡ n) (v : Polynomial m) (i : ℕ)
          → nth (subst Polynomial eq v) i ≡ nth v i
nth-subst refl v i = refl

nth-pad-end : ∀ {n} (k : ℕ) (v : Polynomial n) (i : ℕ) → nth (pad-end k v) i ≡ nth v i
nth-pad-end k []      i       = nth-replicate k i
nth-pad-end k (x ∷ v) zero    = refl
nth-pad-end k (x ∷ v) (suc i) = nth-pad-end k v i

nth-x-shift-zero : ∀ {n} (v : Polynomial n) → nth (x-shift v) zero ≡ 𝟘
nth-x-shift-zero v = refl
nth-x-shift-suc : ∀ {n} (v : Polynomial n) (i : ℕ) → nth (x-shift v) (suc i) ≡ nth v i
nth-x-shift-suc v i = refl

nth-+ⱽ : ∀ {n} (u v : Polynomial n) (i : ℕ) → nth (u +ⱽ v) i ≡ nth u i + nth v i
nth-+ⱽ []      []      i       = refl
nth-+ⱽ (x ∷ u) (y ∷ v) zero    = refl
nth-+ⱽ (x ∷ u) (y ∷ v) (suc i) = nth-+ⱽ u v i

nth-*ₛ : ∀ {n} (c : F₂) (v : Polynomial n) (i : ℕ) → nth (c *ₛ v) i ≡ c · nth v i
nth-*ₛ c []      i       = sym (·-absorbʳ c)
nth-*ₛ c (x ∷ v) zero    = refl
nth-*ₛ c (x ∷ v) (suc i) = nth-*ₛ c v i
