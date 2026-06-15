------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.BasisComm  (was RingLaws §AI-7e)
--
-- Monomials are deltas at `d + toℕ j`: `nth-xpower-basis-peak` (𝟙 at the peak),
-- `nth-xpower-basis-off` (𝟘 elsewhere). Hence two monomials `xⁱ·basis j` and
-- `xʲ·basis i` agree coefficient-wise (`xpower-basis-symm`), giving basis-level
-- commutativity `convCoeff-basis-comm` — the bottom of the *P-comm route.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.BasisComm where

open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Polynomial.Wedge.XPower using (x-power)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using (+-comm)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Basis using (nth-xpower-add;
  nth-basis-same; nth-basis-other; convCoeff-basis-xpower)

nth-xpower-basis-peak : ∀ d {n} (j : Fin n) → nth (x-power d (basis j)) (d ℕ+ toℕ j) ≡ 𝟙
nth-xpower-basis-peak d j = trans (nth-xpower-add d (basis j) (toℕ j)) (nth-basis-same j)

nth-xpower-basis-off : ∀ d {n} (j : Fin n) (k : ℕ) → ¬ (k ≡ d ℕ+ toℕ j)
                     → nth (x-power d (basis j)) k ≡ 𝟘
nth-xpower-basis-off zero    j k       neq = nth-basis-other j k neq
nth-xpower-basis-off (suc d) j zero    _   = refl
nth-xpower-basis-off (suc d) j (suc k) neq = nth-xpower-basis-off d j k (λ e → neq (cong suc e))

-- the two monomials agree at every k (both = delta at toℕ i + toℕ j = toℕ j + toℕ i).
xpower-basis-symm : ∀ {n m} (i : Fin n) (j : Fin m) (k : ℕ)
                  → nth (x-power (toℕ i) (basis j)) k ≡ nth (x-power (toℕ j) (basis i)) k
xpower-basis-symm i j k with k ≟ (toℕ i ℕ+ toℕ j)
... | yes eq = trans (subst (λ z → nth (x-power (toℕ i) (basis j)) z ≡ 𝟙) (sym eq)
                            (nth-xpower-basis-peak (toℕ i) j))
                     (sym (subst (λ z → nth (x-power (toℕ j) (basis i)) z ≡ 𝟙)
                            (sym (trans eq (+-comm (toℕ i) (toℕ j))))
                            (nth-xpower-basis-peak (toℕ j) i)))
... | no neq = trans (nth-xpower-basis-off (toℕ i) j k neq)
                     (sym (nth-xpower-basis-off (toℕ j) i k
                            (λ e → neq (trans e (+-comm (toℕ j) (toℕ i))))))

-- AI-7e: basis-level commutativity of *P (coefficient form). Feeds AI-7f.
convCoeff-basis-comm : ∀ {n m} (i : Fin n) (j : Fin m) (k : ℕ)
                     → convCoeff (basis i) (basis j) k ≡ convCoeff (basis j) (basis i) k
convCoeff-basis-comm i j k =
  trans (convCoeff-basis-xpower i (basis j) k)
        (trans (xpower-basis-symm i j k) (sym (convCoeff-basis-xpower j (basis i) k)))
