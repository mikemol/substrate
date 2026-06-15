------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws
--
-- The commutative-ring laws of F₂[x] multiplication (`_*P_`), proven via
-- the coefficient calculus: ℕ-indexed coefficient extraction `nth`
-- (𝟘 out of range), its convolution characterization `convCoeff`
-- (`nth-*P`), and observation-equality `nth-ext`. From these:
--   * bilinear distributivity   (`*P-distribʳ` / `*P-distribˡ`),
--   * commutativity             (`*P-comm`, via nested `linear-extensionality`),
--   * associativity             (`*P-assoc`, via 3× nested `linear-extensionality`),
--   * graded identity           (`*P-identityˡ-nth`).
--
-- Method: polynomial equalities reduce to per-coordinate F₂ facts
-- (`nth-ext`) and to basis-vector checks (`linear-extensionality`), so
-- the Fubini reindex lives inside `preserves-sum` — never written by hand.
-- `_*P_` is length-additive, so the FIXED-carrier ring is GF(2⁸) =
-- F₂[x]/(m) via reduce-mod-m; these are its graded laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws where

open import Substrate.Algebra.F2
  using (F₂; 𝟘; 𝟙; _+_; _·_; +-identityˡ; +-identityʳ; ·-absorbʳ)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; _*ₛ_)
open import Substrate.Algebra.F2.Polynomial
  using (Polynomial; _*P_; x-shift; pad-end; shift-to-suc-on-left; _·c_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using (+-comm) renaming (+-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)

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

-- The convolution coefficient, defined to MATCH the *P recursion (so it IS the
-- real Σ_{i+j=k} pᵢ·qⱼ: (a∷p)₀=a, and the rest is p convolved, shifted by one).
convCoeff : ∀ {n m} → Polynomial n → Polynomial m → ℕ → F₂
convCoeff []      q k       = 𝟘
convCoeff (a ∷ p) q zero    = a · nth q zero
convCoeff (a ∷ p) q (suc k) = a · nth q (suc k) + convCoeff p q k

-- GENERAL lookup-*P (nth form): the k-th coefficient of p *P q is the convolution.
nth-*P : ∀ {n m} (p : Polynomial n) (q : Polynomial m) (k : ℕ)
       → nth (p *P q) k ≡ convCoeff p q k
nth-*P {zero}  {m} []      q k       = nth-replicate m k
nth-*P {suc n} {m} (a ∷ p) q zero    =
  trans (nth-+ⱽ lo hi zero)
        (trans (cong₂ _+_
                  (trans (nth-subst (+-comm m (suc n)) (pad-end (suc n) (a ·c q)) zero)
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
        (cong₂ _+_
           (trans (nth-subst (+-comm m (suc n)) (pad-end (suc n) (a ·c q)) (suc k))
                  (trans (nth-pad-end (suc n) (a ·c q) (suc k)) (nth-*ₛ a q (suc k))))
           (trans (nth-x-shift-suc (p *P q) k) (nth-*P p q k)))
  where
    lo : Polynomial (suc n ℕ+ m)
    lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
    hi : Polynomial (suc n ℕ+ m)
    hi = x-shift (p *P q)

-- ===== AI-7 cont'd: the ≡-from-lookup method (observation-equality), via nth =====

open import Substrate.Algebra.F2 using (+-assoc; ·-comm; ·-distribˡ-+) renaming (+-comm to +F-comm)

-- nth analog of ≡-from-lookup (observation-equality = the substrate's universal law method).
nth-ext : ∀ {n} (u v : Polynomial n) → (∀ k → nth u k ≡ nth v k) → u ≡ v
nth-ext []      []      _  = refl
nth-ext (x ∷ u) (y ∷ v) eq = cong₂ _∷_ (eq zero) (nth-ext u v (λ k → eq (suc k)))

·-distribʳ : (x y z : F₂) → (x + y) · z ≡ x · z + y · z
·-distribʳ x y z = trans (·-comm (x + y) z)
                   (trans (·-distribˡ-+ z x y) (cong₂ _+_ (·-comm z x) (·-comm z y)))

-- 4-term abelian rearrange (F₂ + is comm-assoc): (w+x)+(y+z) ≡ (w+y)+(x+z).
rearrange : (w x y z : F₂) → (w + x) + (y + z) ≡ (w + y) + (x + z)
rearrange w x y z =
  trans (+-assoc w x (y + z))
  (trans (cong (w +_) (sym (+-assoc x y z)))
  (trans (cong (λ t → w + (t + z)) (+F-comm x y))
  (trans (cong (w +_) (+-assoc y x z)) (sym (+-assoc w y (x + z))))))

-- per-coordinate distributivity of the convolution coefficient (linearity in arg 1).
convCoeff-distrib : ∀ {n m} (p q : Polynomial n) (r : Polynomial m) (k : ℕ)
                  → convCoeff (p +ⱽ q) r k ≡ convCoeff p r k + convCoeff q r k
convCoeff-distrib []      []      r k       = sym (+-identityˡ 𝟘)
convCoeff-distrib (a ∷ p) (b ∷ q) r zero    = ·-distribʳ a b (nth r zero)
convCoeff-distrib (a ∷ p) (b ∷ q) r (suc k) =
  trans (cong₂ _+_ (·-distribʳ a b (nth r (suc k))) (convCoeff-distrib p q r k))
        (rearrange (a · nth r (suc k)) (b · nth r (suc k)) (convCoeff p r k) (convCoeff q r k))

-- *P right-distributivity, via the method (nth-ext + nth-*P + the per-coord identity). No subst.
*P-distribʳ : ∀ {n m} (p q : Polynomial n) (r : Polynomial m)
            → (p +ⱽ q) *P r ≡ (p *P r) +ⱽ (q *P r)
*P-distribʳ p q r = nth-ext _ _ (λ k →
  trans (nth-*P (p +ⱽ q) r k)
  (trans (convCoeff-distrib p q r k)
  (trans (cong₂ _+_ (sym (nth-*P p r k)) (sym (nth-*P q r k)))
         (sym (nth-+ⱽ (p *P r) (q *P r) k)))))

-- *P left-distributivity (linearity in arg 2) → with distribʳ gives BILINEARITY.
-- convCoeff recurses on arg 1, so arg 2 enters only via nth — clean, no reindex.
convCoeff-distribˡ : ∀ {n m} (r : Polynomial n) (p q : Polynomial m) (k : ℕ)
                   → convCoeff r (p +ⱽ q) k ≡ convCoeff r p k + convCoeff r q k
convCoeff-distribˡ []      p q k       = sym (+-identityˡ 𝟘)
convCoeff-distribˡ (a ∷ r) p q zero    =
  trans (cong (a ·_) (nth-+ⱽ p q zero)) (·-distribˡ-+ a (nth p zero) (nth q zero))
convCoeff-distribˡ (a ∷ r) p q (suc k) =
  trans (cong₂ _+_ (trans (cong (a ·_) (nth-+ⱽ p q (suc k)))
                          (·-distribˡ-+ a (nth p (suc k)) (nth q (suc k))))
                   (convCoeff-distribˡ r p q k))
        (rearrange (a · nth p (suc k)) (a · nth q (suc k)) (convCoeff r p k) (convCoeff r q k))

*P-distribˡ : ∀ {n m} (r : Polynomial n) (p q : Polynomial m)
            → r *P (p +ⱽ q) ≡ (r *P p) +ⱽ (r *P q)
*P-distribˡ r p q = nth-ext _ _ (λ k →
  trans (nth-*P r (p +ⱽ q) k)
  (trans (convCoeff-distribˡ r p q k)
  (trans (cong₂ _+_ (sym (nth-*P r p k)) (sym (nth-*P r q k)))
         (sym (nth-+ⱽ (r *P p) (r *P q) k)))))

-- ===== AI-7e: nth↔basis bridge (substrate basis is a delta under nth) =====
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Algebra.F2.Vector using (basis; 𝟎ⱽ)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥-elim)

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

-- ===== AI-7d (identity) + 7e-core foundation: convCoeff of 𝟎ⱽ and of basis fz =====
open import Substrate.Algebra.F2 using (·-absorbˡ; ·-identityˡ)

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

-- ===== AI-7e core: mult by basis i (= xⁱ) is a shift =====
open import Substrate.Algebra.F2.Polynomial.Wedge.XPower using (x-power)

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

-- ===== AI-7e: monomials are deltas at d + toℕ j; hence basis-level commutativity =====
open import Substrate.Foundation.Nat using (_≟_)
open import Substrate.Foundation.Negation using (yes; no)

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

-- ===== AI-7f: the preserves-*ₛ pieces (for packaging *P as Linear) + subst-linearity =====
open import Substrate.Algebra.F2 using (·-assoc)

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

-- ===== AI-7f/7g: *P-comm via nested linear-extensionality (the V4⋊S3 route) =====
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)

-- _*P q as a Linear map (outer, varying the left arg).
Lq : ∀ {n m} (q : Polynomial m) → Linear n (n ℕ+ m)
Lq q = record { apply = _*P q ; preserves-+ = λ u v → *P-distribʳ u v q
              ; preserves-*ₛ = λ c v → *P-scalarˡ c v q }
-- subst ∘ (q *P_) as a Linear map (same codomain n+m, via +-comm m n).
Mq : ∀ {n m} (q : Polynomial m) → Linear n (n ℕ+ m)
Mq {n} {m} q = record
  { apply = λ p → subst Polynomial (+-comm m n) (q *P p)
  ; preserves-+ = λ u v → trans (cong (subst Polynomial (+-comm m n)) (*P-distribˡ q u v))
                                (subst-+ⱽ (+-comm m n) (q *P u) (q *P v))
  ; preserves-*ₛ = λ c v → trans (cong (subst Polynomial (+-comm m n)) (*P-scalarʳ c q v))
                                 (subst-*ₛ (+-comm m n) c (q *P v)) }
-- (basis i) *P_  and  subst ∘ (_*P basis i)  as Linear maps (inner, varying the right arg).
Li : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
Li i = record { apply = λ q → basis i *P q ; preserves-+ = λ u v → *P-distribˡ (basis i) u v
              ; preserves-*ₛ = λ c v → *P-scalarʳ c (basis i) v }
Mi : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
Mi {n} {m} i = record
  { apply = λ q → subst Polynomial (+-comm m n) (q *P basis i)
  ; preserves-+ = λ u v → trans (cong (subst Polynomial (+-comm m n)) (*P-distribʳ u v (basis i)))
                                (subst-+ⱽ (+-comm m n) (u *P basis i) (v *P basis i))
  ; preserves-*ₛ = λ c v → trans (cong (subst Polynomial (+-comm m n)) (*P-scalarˡ c v (basis i)))
                                 (subst-*ₛ (+-comm m n) c (v *P basis i)) }

-- inner extensionality: bottoms at the basis-pair fact (AI-7e convCoeff-basis-comm).
agree-i : ∀ {n m} (i : Fin n) (q : Polynomial m)
        → basis i *P q ≡ subst Polynomial (+-comm m n) (q *P basis i)
agree-i {n} {m} i q = linear-extensionality (Li i) (Mi i) basis-pair q
  where
    basis-pair : (j : Fin m) → basis i *P basis j ≡ subst Polynomial (+-comm m n) (basis j *P basis i)
    basis-pair j = nth-ext _ _ (λ k →
      trans (nth-*P (basis i) (basis j) k)
      (trans (convCoeff-basis-comm i j k)
      (trans (sym (nth-*P (basis j) (basis i) k))
             (sym (nth-subst (+-comm m n) (basis j *P basis i) k)))))

-- AI-7g: *P COMMUTATIVITY (full).
*P-comm : ∀ {n m} (p : Polynomial n) (q : Polynomial m)
        → p *P q ≡ subst Polynomial (+-comm m n) (q *P p)
*P-comm p q = linear-extensionality (Lq q) (Mq q) (λ i → agree-i i q) p

-- ===== AI-7h foundations: convCoeff-comm (from *P-comm) + general x-power vanishing =====
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

-- ===== AI-7h-bot: all-basis associativity (the monomial-assoc bottom) =====
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

-- ===== AI-7h: *P ASSOCIATIVITY (full) via 3× nested linear-extensionality =====
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

-- ===== AI-7d: multiplicative identity (graded / length-agnostic form) =====
-- The "one" of F₂[x] is the leading-𝟙 basis vector. Multiplying by it preserves every
-- coefficient: nth (𝟙·xⁿ-style basis *P q) ≡ nth q. (A length-1 `[𝟙]` is the n=0 case.)
-- This is the coefficient-level identity that reduce-mod-m (AI-6) carries down to GF(2⁸);
-- a fixed-carrier `[𝟙] *P q ≡ q` is NOT well-typed here (*P is length-additive: 1+m ≠ m).
*P-identityˡ-nth : ∀ {n m} (q : Polynomial m) (k : ℕ)
                 → nth (basis {suc n} fz *P q) k ≡ nth q k
*P-identityˡ-nth q k = trans (nth-*P (basis fz) q k) (convCoeff-basis-fz q k)
