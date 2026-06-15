------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Basis  (was RingLaws §AI-7e/7d)
--
-- The nth↔basis bridge: the substrate `basis i` is the delta at `toℕ i` under
-- `nth`. Plus the convolution facts for the zero/unit/monomial left factors:
-- `convCoeff-𝟎ⱽ`, `convCoeff-basis-fz` (basis fz = the polynomial 1), and that
-- multiplying by `basis i` (= xⁱ) is an x-power shift (`convCoeff-basis-xpower`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Basis where

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_; _·_; +-identityˡ; +-identityʳ;
  ·-absorbˡ; ·-identityˡ)
open import Substrate.Algebra.F2.Vector using (basis; 𝟎ⱽ)
open import Substrate.Algebra.F2.Polynomial using (Polynomial)
open import Substrate.Algebra.F2.Polynomial.Wedge.XPower using (x-power)
open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff)

nth-𝟎ⱽ : ∀ {n} (k : ℕ) → nth (𝟎ⱽ {n}) k ≡ 𝟘
nth-𝟎ⱽ {zero}  k       = refl
nth-𝟎ⱽ {suc n} zero    = refl
nth-𝟎ⱽ {suc n} (suc k) = nth-𝟎ⱽ {n} k

-- basis i is the delta at toℕ i: 𝟙 there, 𝟘 elsewhere.
nth-basis-same : ∀ {n} (i : Fin n) → nth (basis i) (toℕ i) ≡ 𝟙
nth-basis-same fz     = refl
nth-basis-same (fs i) = nth-basis-same i

nth-basis-other : ∀ {n} (i : Fin n) (k : ℕ) → ¬ (k ≡ toℕ i) → nth (basis i) k ≡ 𝟘
nth-basis-other fz     zero    neq = ⊥-elim (neq refl)
nth-basis-other {suc m} fz (suc k) _ = nth-𝟎ⱽ {m} k
nth-basis-other (fs i) zero    _   = refl
nth-basis-other (fs i) (suc k) neq = nth-basis-other i k (λ e → neq (cong suc e))

convCoeff-𝟎ⱽ : ∀ {n m} (q : Polynomial m) (k : ℕ) → convCoeff (𝟎ⱽ {n}) q k ≡ 𝟘
convCoeff-𝟎ⱽ {zero}  q k       = refl
convCoeff-𝟎ⱽ {suc n} q zero    = ·-absorbˡ (nth q zero)
convCoeff-𝟎ⱽ {suc n} q (suc k) =
  trans (cong₂ _+_ (·-absorbˡ (nth q (suc k))) (convCoeff-𝟎ⱽ {n} q k)) (+-identityˡ 𝟘)

-- basis fz = the polynomial 1 (x⁰): left-multiplication is the identity. (= AI-7d core)
convCoeff-basis-fz : ∀ {n m} (q : Polynomial m) (k : ℕ) → convCoeff (basis {suc n} fz) q k ≡ nth q k
convCoeff-basis-fz q zero    = ·-identityˡ (nth q zero)
convCoeff-basis-fz {n} q (suc k) =
  trans (cong₂ _+_ (·-identityˡ (nth q (suc k))) (convCoeff-𝟎ⱽ {n} q k)) (+-identityʳ (nth q (suc k)))

-- the additive shift: coefficient at d+k of (xᵈ·q) is q's coefficient at k.
nth-xpower-add : ∀ d {m} (q : Polynomial m) (k : ℕ) → nth (x-power d q) (d ℕ+ k) ≡ nth q k
nth-xpower-add zero    q k = refl
nth-xpower-add (suc d) q k = nth-xpower-add d q k

-- multiplying by the monomial basis i (= x^{toℕ i}) shifts q up by toℕ i.
convCoeff-basis-xpower : ∀ {n m} (i : Fin n) (q : Polynomial m) (k : ℕ)
                       → convCoeff (basis i) q k ≡ nth (x-power (toℕ i) q) k
convCoeff-basis-xpower {suc n} fz     q k       = convCoeff-basis-fz q k
convCoeff-basis-xpower (fs i)         q zero    = ·-absorbˡ (nth q zero)
convCoeff-basis-xpower (fs i)         q (suc k) =
  trans (cong₂ _+_ (·-absorbˡ (nth q (suc k))) (convCoeff-basis-xpower i q k))
        (+-identityˡ (nth (x-power (toℕ i) q) k))
