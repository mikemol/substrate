------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Scalar  (was RingLaws §AI-7f)
--
-- The preserves-*ₛ pieces (for packaging `_*P_` as a `Linear` map): scalar
-- linearity in each argument (`*P-scalarˡ` / `*P-scalarʳ`), and the fact that
-- the length-recast `subst` is itself linear (`subst-+ⱽ` / `subst-*ₛ`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Scalar where

open import Substrate.Algebra.F2 using (F₂; _+_; _·_; ·-comm; ·-assoc; ·-absorbʳ; ·-distribˡ-+)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth; nth-*ₛ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff; nth-*P; nth-ext)

swap-· : (a c x : F₂) → a · (c · x) ≡ c · (a · x)
swap-· a c x = trans (sym (·-assoc a c x)) (trans (cong (_· x) (·-comm a c)) (·-assoc c a x))

-- preserves-*ₛ in arg 1: (c *ₛ p) *P q ≡ c *ₛ (p *P q)
convCoeff-scalarˡ : ∀ {n m} (c : F₂) (p : Polynomial n) (q : Polynomial m) (k : ℕ)
                  → convCoeff (c *ₛ p) q k ≡ c · convCoeff p q k
convCoeff-scalarˡ c []      q k       = sym (·-absorbʳ c)
convCoeff-scalarˡ c (a ∷ p) q zero    = ·-assoc c a (nth q zero)
convCoeff-scalarˡ c (a ∷ p) q (suc k) =
  trans (cong₂ _+_ (·-assoc c a (nth q (suc k))) (convCoeff-scalarˡ c p q k))
        (sym (·-distribˡ-+ c (a · nth q (suc k)) (convCoeff p q k)))

*P-scalarˡ : ∀ {n m} (c : F₂) (p : Polynomial n) (q : Polynomial m)
           → (c *ₛ p) *P q ≡ c *ₛ (p *P q)
*P-scalarˡ c p q = nth-ext _ _ (λ k →
  trans (nth-*P (c *ₛ p) q k)
  (trans (convCoeff-scalarˡ c p q k)
  (trans (cong (c ·_) (sym (nth-*P p q k))) (sym (nth-*ₛ c (p *P q) k)))))

-- preserves-*ₛ in arg 2: p *P (c *ₛ q) ≡ c *ₛ (p *P q)
convCoeff-scalarʳ : ∀ {n m} (c : F₂) (p : Polynomial n) (q : Polynomial m) (k : ℕ)
                  → convCoeff p (c *ₛ q) k ≡ c · convCoeff p q k
convCoeff-scalarʳ c []      q k       = sym (·-absorbʳ c)
convCoeff-scalarʳ c (a ∷ p) q zero    =
  trans (cong (a ·_) (nth-*ₛ c q zero)) (swap-· a c (nth q zero))
convCoeff-scalarʳ c (a ∷ p) q (suc k) =
  trans (cong₂ _+_ (trans (cong (a ·_) (nth-*ₛ c q (suc k))) (swap-· a c (nth q (suc k))))
                   (convCoeff-scalarʳ c p q k))
        (sym (·-distribˡ-+ c (a · nth q (suc k)) (convCoeff p q k)))

*P-scalarʳ : ∀ {n m} (c : F₂) (p : Polynomial n) (q : Polynomial m)
           → p *P (c *ₛ q) ≡ c *ₛ (p *P q)
*P-scalarʳ c p q = nth-ext _ _ (λ k →
  trans (nth-*P p (c *ₛ q) k)
  (trans (convCoeff-scalarʳ c p q k)
  (trans (cong (c ·_) (sym (nth-*P p q k))) (sym (nth-*ₛ c (p *P q) k)))))

-- subst (length re-cast) is linear: distributes over +ⱽ and *ₛ.
subst-+ⱽ : ∀ {m n} (eq : m ≡ n) (u v : Polynomial m)
         → subst Polynomial eq (u +ⱽ v) ≡ subst Polynomial eq u +ⱽ subst Polynomial eq v
subst-+ⱽ refl u v = refl
subst-*ₛ : ∀ {m n} (eq : m ≡ n) (c : F₂) (v : Polynomial m)
         → subst Polynomial eq (c *ₛ v) ≡ c *ₛ subst Polynomial eq v
subst-*ₛ refl c v = refl
