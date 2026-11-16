------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Conv  (was RingLaws §AI-7 base, cont'd)
--
-- The convolution coefficient `convCoeff` (defined to MATCH the *P recursion,
-- so it IS the real Σ_{i+j=k} pᵢ·qⱼ), the bridge `nth-*P` (the k-th coefficient
-- of p *P q is that convolution), and observation-equality `nth-ext`. Together
-- `nth-*P` +F `nth-ext` are THE method: polynomial equalities reduce to per-
-- coordinate F₂ facts.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Conv where

open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityR
open import Substrate.Algebra.F2.Polynomial
  using (Polynomial; _*P_; x-shift; pad-end; shift-to-suc-on-left; _·c_)
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth; nth-replicate;
  nth-subst; nth-pad-end; nth-x-shift-zero; nth-x-shift-suc; nth-+ⱽ; nth-*ₛ)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong2

-- The convolution coefficient, defined to MATCH the *P recursion (so it IS the
-- real Σ_{i+j=k} pᵢ·qⱼ: (a∷p)₀=a, and the rest is p convolved, shifted by one).
convCoeff : ∀ {n m} → Polynomial n → Polynomial m → ℕ → F₂
convCoeff []      q k       = 𝟘
convCoeff (a ∷ p) q zero    = a · nth q zero
convCoeff (a ∷ p) q (suc k) = a · nth q (suc k) +F convCoeff p q k

-- GENERAL lookup-*P (nth form): the k-th coefficient of p *P q is the convolution.
nth-*P : ∀ {n m} (p : Polynomial n) (q : Polynomial m) (k : ℕ)
       → nth (p *P q) k ≡ convCoeff p q k
nth-*P {zero}  {m} []      q k       = nth-replicate m k
nth-*P {suc n} {m} (a ∷ p) q zero    =
  trans (nth-+ⱽ lo hi zero)
        (trans (cong₂ _+F_
                  (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) zero)
                         (trans (nth-pad-end (suc n) (a ·c q) zero) (nth-*ₛ a q zero)))
                  (nth-x-shift-zero (p *P q)))
               (+-identityʳ (a · nth q zero)))
  where
    lo : Polynomial (suc n ℕ+ m)
    lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
    hi : Polynomial (suc n ℕ+ m)
    hi = x-shift (p *P q)
nth-*P {suc n} {m} (a ∷ p) q (suc k) =
  trans (nth-+ⱽ lo hi (suc k))
        (cong₂ _+F_
           (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) (suc k))
                  (trans (nth-pad-end (suc n) (a ·c q) (suc k)) (nth-*ₛ a q (suc k))))
           (trans (nth-x-shift-suc (p *P q) k) (nth-*P p q k)))
  where
    lo : Polynomial (suc n ℕ+ m)
    lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
    hi : Polynomial (suc n ℕ+ m)
    hi = x-shift (p *P q)

-- nth analog of ≡-from-lookup (observation-equality = the substrate's universal law method).
nth-ext : ∀ {n} (u v : Polynomial n) → (∀ k → nth u k ≡ nth v k) → u ≡ v
nth-ext []      []      _  = refl
nth-ext (x ∷ u) (y ∷ v) eq = cong₂ _∷_ (eq zero) (nth-ext u v (λ k → eq (suc k)))
