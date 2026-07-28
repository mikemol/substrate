------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Assoc  (was RingLaws §AI-7h)
--
-- `*P-assoc` via 3× nested `linear-extensionality` (same costructure as comm,
-- one nesting deeper). Foundations: `convCoeff-comm` (corollary of *P-comm),
-- `convCoeff-basis-right`, general x-power vanishing (`nth-xpower-off`), and the
-- all-basis bottom `mono-assoc` (both triple products are the SAME delta at
-- toℕi+toℕj+toℕk, reconciled at length by ℕ +-assoc).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Assoc where

open import Substrate.Algebra.F2 using (𝟘; 𝟙)
open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Algebra.F2.Polynomial.Wedge.XPower using (x-power)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm) renaming (+-assoc to +ℕ-assoc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Op2
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; subst)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth; nth-subst)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff; nth-*P; nth-ext)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Distrib using (*P-distribʳ; *P-distribˡ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Scalar using (*P-scalarˡ; *P-scalarʳ;
  subst-+ⱽ; subst-*ₛ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Basis using (convCoeff-basis-xpower;
  nth-xpower-add)
open import Substrate.Algebra.F2.Polynomial.RingLaws.BasisComm using (nth-xpower-basis-peak;
  nth-xpower-basis-off)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Comm using (*P-comm)

-- 7h-cc: coefficient-level commutativity, a clean corollary of *P-comm.
convCoeff-comm : ∀ {n m} (p : Polynomial n) (q : Polynomial m) (d : ℕ)
               → convCoeff p q d ≡ convCoeff q p d
convCoeff-comm {n} {m} p q d =
  trans (sym (nth-*P p q d))
  (trans (cong (λ z → nth z d) (*P-comm p q))
  (trans (nth-subst (+-comm m n) (q *P p) d) (nth-*P q p d)))

-- right-monomial coefficient law (k goes into the shift via comm).
convCoeff-basis-right : ∀ {n m} (p : Polynomial n) (k : Fin m) (d : ℕ)
                      → convCoeff p (basis k) d ≡ nth (x-power (toℕ k) p) d
convCoeff-basis-right p k d =
  trans (convCoeff-comm p (basis k) d) (convCoeff-basis-xpower k p d)

-- 7h-xx: x-power vanishes at d whenever its argument vanishes at the de-shifted index
-- (covers BOTH d < a, vacuously, and d = a+b with q b = 𝟘). Induction on the shift a.
nth-xpower-off : ∀ a {m} (q : Polynomial m) (d : ℕ)
               → (∀ b → d ≡ a ℕ+ b → nth q b ≡ 𝟘) → nth (x-power a q) d ≡ 𝟘
nth-xpower-off zero    q d       h = h d refl
nth-xpower-off (suc a) q zero    _ = refl
nth-xpower-off (suc a) q (suc d) h = nth-xpower-off a q d (λ b e → h b (cong suc e))

-- (basis i · basis j) · basis k  and  basis i · (basis j · basis k) are the SAME
-- delta (at toℕi+toℕj+toℕk), reconciled at length by ℕ +-assoc. Peak/off case split;
-- exponent re-association is the only ℕ-arithmetic (rk), via convCoeff-basis-right (k last).
mono-assoc : ∀ {n m l} (i : Fin n) (j : Fin m) (k : Fin l)
           → subst Polynomial (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k)
             ≡ basis i *P (basis j *P basis k)
mono-assoc {n} {m} {l} i j k = nth-ext _ _ (λ d →
  trans (nth-subst (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k) d) (coeff d))
  where
    P : ℕ
    P = toℕ i ℕ+ (toℕ j ℕ+ toℕ k)
    rk : toℕ k ℕ+ (toℕ i ℕ+ toℕ j) ≡ P
    rk = trans (+-comm (toℕ k) (toℕ i ℕ+ toℕ j)) (+ℕ-assoc (toℕ i) (toℕ j) (toℕ k))
    lhsV : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                   ≡ nth (x-power (toℕ k) (basis i *P basis j)) d
    lhsV d = trans (nth-*P (basis i *P basis j) (basis k) d)
                   (convCoeff-basis-right (basis i *P basis j) k d)
    rhsV : (d : ℕ) → nth (basis i *P (basis j *P basis k)) d
                   ≡ nth (x-power (toℕ i) (basis j *P basis k)) d
    rhsV d = trans (nth-*P (basis i) (basis j *P basis k) d)
                   (convCoeff-basis-xpower i (basis j *P basis k) d)
    ijV : (b : ℕ) → nth (basis i *P basis j) b ≡ nth (x-power (toℕ i) (basis j)) b
    ijV b = trans (nth-*P (basis i) (basis j) b) (convCoeff-basis-xpower i (basis j) b)
    jkV : (b : ℕ) → nth (basis j *P basis k) b ≡ nth (x-power (toℕ j) (basis k)) b
    jkV b = trans (nth-*P (basis j) (basis k) b) (convCoeff-basis-xpower j (basis k) b)
    coeff : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                    ≡ nth (basis i *P (basis j *P basis k)) d
    coeff d with d ≟ P
    ... | yes eq = trans lhs𝟙 (sym rhs𝟙)
      where
        rhs𝟙 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟙
        rhs𝟙 = subst (λ z → nth (basis i *P (basis j *P basis k)) z ≡ 𝟙) (sym eq)
                 (trans (rhsV P)
                  (trans (nth-xpower-add (toℕ i) (basis j *P basis k) (toℕ j ℕ+ toℕ k))
                   (trans (jkV (toℕ j ℕ+ toℕ k)) (nth-xpower-basis-peak (toℕ j) k))))
        lhs𝟙 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟙
        lhs𝟙 = subst (λ z → nth ((basis i *P basis j) *P basis k) z ≡ 𝟙) (sym eq)
                 (trans (lhsV P)
                  (subst (λ z → nth (x-power (toℕ k) (basis i *P basis j)) z ≡ 𝟙) rk
                    (trans (nth-xpower-add (toℕ k) (basis i *P basis j) (toℕ i ℕ+ toℕ j))
                     (trans (ijV (toℕ i ℕ+ toℕ j)) (nth-xpower-basis-peak (toℕ i) j)))))
    ... | no neq = trans lhs𝟘 (sym rhs𝟘)
      where
        rhs𝟘 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟘
        rhs𝟘 = trans (rhsV d)
                 (nth-xpower-off (toℕ i) (basis j *P basis k) d
                   (λ b e → trans (jkV b)
                     (nth-xpower-basis-off (toℕ j) k b
                       (λ b-eq → neq (trans e (cong (toℕ i ℕ+_) b-eq))))))
        lhs𝟘 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟘
        lhs𝟘 = trans (lhsV d)
                 (nth-xpower-off (toℕ k) (basis i *P basis j) d
                   (λ b e → trans (ijV b)
                     (nth-xpower-basis-off (toℕ i) j b
                       (λ b-eq → neq (trans (trans e (cong (toℕ k ℕ+_) b-eq)) rk)))))

-- Same costructure as comm (7g), one nesting deeper. The six Linear records are the
-- two sides at each level; the 3-fold nest bottoms at mono-assoc (all-basis).
*P-assoc : ∀ {n m l} (p : Polynomial n) (q : Polynomial m) (r : Polynomial l)
         → subst Polynomial (+ℕ-assoc n m l) ((p *P q) *P r) ≡ p *P (q *P r)
*P-assoc {n} {m} {l} p q r = linear-extensionality (Lp q r) (Rp q r) (λ i → agp i q r) p
  where
    ae : (n ℕ+ m) ℕ+ l ≡ n ℕ+ (m ℕ+ l)
    ae = +ℕ-assoc n m l
    S : Polynomial ((n ℕ+ m) ℕ+ l) → Polynomial (n ℕ+ (m ℕ+ l))
    S = subst Polynomial ae
    Lp : (q : Polynomial m) (r : Polynomial l) → Linear n (n ℕ+ (m ℕ+ l))
    Lp q r = record
      { apply = λ p → S ((p *P q) *P r)
      ; preserves-+ = λ u v → trans (cong S (trans (cong (_*P r) (*P-distribʳ u v q))
                                                    (*P-distribʳ (u *P q) (v *P q) r)))
                                    (subst-+ⱽ ae ((u *P q) *P r) ((v *P q) *P r))
      ; preserves-*ₛ = λ c v → trans (cong S (trans (cong (_*P r) (*P-scalarˡ c v q))
                                                    (*P-scalarˡ c (v *P q) r)))
                                     (subst-*ₛ ae c ((v *P q) *P r)) }
    Rp : (q : Polynomial m) (r : Polynomial l) → Linear n (n ℕ+ (m ℕ+ l))
    Rp q r = record
      { apply = λ p → p *P (q *P r)
      ; preserves-+ = λ u v → *P-distribʳ u v (q *P r)
      ; preserves-*ₛ = λ c v → *P-scalarˡ c v (q *P r) }
    Lq' : (i : Fin n) (r : Polynomial l) → Linear m (n ℕ+ (m ℕ+ l))
    Lq' i r = record
      { apply = λ q → S ((basis i *P q) *P r)
      ; preserves-+ = λ u v → trans (cong S (trans (cong (_*P r) (*P-distribˡ (basis i) u v))
                                                   (*P-distribʳ (basis i *P u) (basis i *P v) r)))
                                    (subst-+ⱽ ae ((basis i *P u) *P r) ((basis i *P v) *P r))
      ; preserves-*ₛ = λ c v → trans (cong S (trans (cong (_*P r) (*P-scalarʳ c (basis i) v))
                                                    (*P-scalarˡ c (basis i *P v) r)))
                                     (subst-*ₛ ae c ((basis i *P v) *P r)) }
    Rq' : (i : Fin n) (r : Polynomial l) → Linear m (n ℕ+ (m ℕ+ l))
    Rq' i r = record
      { apply = λ q → basis i *P (q *P r)
      ; preserves-+ = λ u v → trans (cong (basis i *P_) (*P-distribʳ u v r))
                                    (*P-distribˡ (basis i) (u *P r) (v *P r))
      ; preserves-*ₛ = λ c v → trans (cong (basis i *P_) (*P-scalarˡ c v r))
                                     (*P-scalarʳ c (basis i) (v *P r)) }
    Lr'' : (i : Fin n) (j : Fin m) → Linear l (n ℕ+ (m ℕ+ l))
    Lr'' i j = record
      { apply = λ r → S ((basis i *P basis j) *P r)
      ; preserves-+ = λ u v → trans (cong S (*P-distribˡ (basis i *P basis j) u v))
                                    (subst-+ⱽ ae ((basis i *P basis j) *P u) ((basis i *P basis j) *P v))
      ; preserves-*ₛ = λ c v → trans (cong S (*P-scalarʳ c (basis i *P basis j) v))
                                     (subst-*ₛ ae c ((basis i *P basis j) *P v)) }
    Rr'' : (i : Fin n) (j : Fin m) → Linear l (n ℕ+ (m ℕ+ l))
    Rr'' i j = record
      { apply = λ r → basis i *P (basis j *P r)
      ; preserves-+ = λ u v → trans (cong (basis i *P_) (*P-distribˡ (basis j) u v))
                                    (*P-distribˡ (basis i) (basis j *P u) (basis j *P v))
      ; preserves-*ₛ = λ c v → trans (cong (basis i *P_) (*P-scalarʳ c (basis j) v))
                                     (*P-scalarʳ c (basis i) (basis j *P v)) }
    agq : (i : Fin n) (j : Fin m) (r : Polynomial l)
        → S ((basis i *P basis j) *P r) ≡ basis i *P (basis j *P r)
    agq i j r = linear-extensionality (Lr'' i j) (Rr'' i j) (λ k → mono-assoc i j k) r
    agp : (i : Fin n) (q : Polynomial m) (r : Polynomial l)
        → S ((basis i *P q) *P r) ≡ basis i *P (q *P r)
    agp i q r = linear-extensionality (Lq' i r) (Rq' i r) (λ j → agq i j r) q
