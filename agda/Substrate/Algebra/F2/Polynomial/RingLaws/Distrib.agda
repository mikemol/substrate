------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Distrib  (was RingLaws §AI-7 cont'd)
--
-- Bilinear distributivity of `_*P_`: right (`*P-distribʳ`, linearity in arg 1)
-- and left (`*P-distribˡ`, linearity in arg 2). Each is the per-coordinate
-- convolution-distributivity pushed through `nth-ext` + `nth-*P` — no subst.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Distrib where

open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_; _·_; +-identityˡ; +-assoc;
  ·-comm; ·-distribˡ-+) renaming (+-comm to +F-comm)
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth; nth-+ⱽ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff; nth-*P; nth-ext)
open import Substrate.Algebra.Medial using (medial)

·-distribʳ : (x y z : F₂) → (x + y) · z ≡ x · z + y · z
·-distribʳ x y z = trans (·-comm (x + y) z)
                   (trans (·-distribˡ-+ z x y) (cong₂ _+_ (·-comm z x) (·-comm z y)))

-- Ⓜ: 4-term abelian rearrange = the commutative-monoid medial law (Algebra.Medial)
-- at F₂'s `+` (assoc + comm). The local re-proof became this one-line instance.
rearrange : (w x y z : F₂) → (w + x) + (y + z) ≡ (w + y) + (x + z)
rearrange = medial _+_ +-assoc +F-comm

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
