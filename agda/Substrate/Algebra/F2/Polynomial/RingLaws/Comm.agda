------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Comm  (was RingLaws §AI-7f/7g)
--
-- `*P-comm` via nested `linear-extensionality` (the V4⋊S3 route). The four
-- `Linear` records are the two sides at each level (outer varies the left arg,
-- inner the right); the nest bottoms at the basis-pair fact (`agree-i`, =
-- §BasisComm's `convCoeff-basis-comm`). The Fubini reindex lives inside
-- `preserves-sum`, never written by hand.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Comm where

open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Algebra.F2.Linear.Linear
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Fin.Fin
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth-subst)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (nth-*P; nth-ext)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Distrib using (*P-distribʳ; *P-distribˡ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Scalar using (*P-scalarˡ; *P-scalarʳ;
  subst-+ⱽ; subst-*ₛ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.BasisComm using (convCoeff-basis-comm)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Subst

-- _*P q as a Linear map (outer, varying the left arg).
Lq : ∀ {n m} (q : Polynomial m) → Linear n (n ℕ+ m)
Lq q = record { apply = _*P q ; preserves-+ = λ u v → *P-distribʳ u v q
              ; preserves-*ₛ = λ c v → *P-scalarˡ c v q }
-- subst ∘ (q *P_) as a Linear map (same codomain n+m, via +ℕ-comm m n).
Mq : ∀ {n m} (q : Polynomial m) → Linear n (n ℕ+ m)
Mq {n} {m} q = record
  { apply = λ p → subst Polynomial (+ℕ-comm m n) (q *P p)
  ; preserves-+ = λ u v → trans (cong (subst Polynomial (+ℕ-comm m n)) (*P-distribˡ q u v))
                                (subst-+ⱽ (+ℕ-comm m n) (q *P u) (q *P v))
  ; preserves-*ₛ = λ c v → trans (cong (subst Polynomial (+ℕ-comm m n)) (*P-scalarʳ c q v))
                                 (subst-*ₛ (+ℕ-comm m n) c (q *P v)) }
-- (basis i) *P_  and  subst ∘ (_*P basis i)  as Linear maps (inner, varying the right arg).
Li : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
Li i = record { apply = λ q → basis i *P q ; preserves-+ = λ u v → *P-distribˡ (basis i) u v
              ; preserves-*ₛ = λ c v → *P-scalarʳ c (basis i) v }
Mi : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
Mi {n} {m} i = record
  { apply = λ q → subst Polynomial (+ℕ-comm m n) (q *P basis i)
  ; preserves-+ = λ u v → trans (cong (subst Polynomial (+ℕ-comm m n)) (*P-distribʳ u v (basis i)))
                                (subst-+ⱽ (+ℕ-comm m n) (u *P basis i) (v *P basis i))
  ; preserves-*ₛ = λ c v → trans (cong (subst Polynomial (+ℕ-comm m n)) (*P-scalarˡ c v (basis i)))
                                 (subst-*ₛ (+ℕ-comm m n) c (v *P basis i)) }

-- inner extensionality: bottoms at the basis-pair fact (AI-7e convCoeff-basis-comm).
agree-i : ∀ {n m} (i : Fin n) (q : Polynomial m)
        → basis i *P q ≡ subst Polynomial (+ℕ-comm m n) (q *P basis i)
agree-i {n} {m} i q = linear-extensionality (Li i) (Mi i) basis-pair q
  where
    basis-pair : (j : Fin m) → basis i *P basis j ≡ subst Polynomial (+ℕ-comm m n) (basis j *P basis i)
    basis-pair j = nth-ext _ _ (λ k →
      trans (nth-*P (basis i) (basis j) k)
      (trans (convCoeff-basis-comm i j k)
      (trans (sym (nth-*P (basis j) (basis i) k))
             (sym (nth-subst (+ℕ-comm m n) (basis j *P basis i) k)))))

-- AI-7g: *P COMMUTATIVITY (full).
*P-comm : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
        → p *P q ≡ subst Polynomial (+ℕ-comm m n) (q *P p)
*P-comm p q = linear-extensionality (Lq q) (Mq q) (λ i → agree-i i q) p
