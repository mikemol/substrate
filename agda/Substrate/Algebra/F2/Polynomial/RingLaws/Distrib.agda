------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.RingLaws.Distrib  (was RingLaws §AI-7 cont'd)
--
-- Bilinear distributivity of `_*P_`: right (`*P-distribʳ`, linearity in arg 1)
-- and left (`*P-distribˡ`, linearity in arg 2). Each is the per-coordinate
-- convolution-distributivity pushed through `nth-ext` +F `nth-*P` — no subst.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.RingLaws.Distrib where

open import Substrate.Algebra.F2.Comm
open import Substrate.Algebra.F2.DistribLPlus
open import Substrate.Algebra.F2.DistribRPlus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.Op
open import Substrate.Algebra.F2.PlusAssoc
open import Substrate.Algebra.F2.PlusComm
  renaming (+-comm to +F-comm)
open import Substrate.Algebra.F2.PlusF
open import Substrate.Algebra.F2.PlusIdentityL
open import Substrate.Algebra.F2.Vector using (_+ⱽ_)
open import Substrate.Algebra.F2.Polynomial using (Polynomial; _*P_)
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Nth using (nth; nth-+ⱽ)
open import Substrate.Algebra.F2.Polynomial.RingLaws.Conv using (convCoeff; nth-*P; nth-ext)
open import Substrate.Algebra.Medial using (medial)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2

-- Ⓓ·: ·-distribʳ is Algebra.F2's ·-distribʳ-+ (reordered args); it was
-- re-derived here with the identical trans/·-comm/·-distribˡ-+ chain.
·-distribʳ : (x y z : F₂) → (x +F y) · z ≡ x · z +F y · z
·-distribʳ x y z = ·-distribʳ-+ z x y

-- Ⓜ: 4-term abelian rearrange = the commutative-monoid medial law (Algebra.Medial)
-- at F₂'s `+` (assoc +F comm). The local re-proof became this one-line instance.
rearrange : (w x y z : F₂) → (w +F x) +F (y +F z) ≡ (w +F y) +F (x +F z)
rearrange = medial _+F_ +-assoc +F-comm

-- per-coordinate distributivity of the convolution coefficient (linearity in arg 1).
convCoeff-distrib : ∀ {n m} (p q : Polynomial n) (r : Polynomial m) (k : ℕ)
                  → convCoeff (p +ⱽ q) r k ≡ convCoeff p r k +F convCoeff q r k
convCoeff-distrib []      []      r k       = sym (+-identityˡ 𝟘)
convCoeff-distrib (a ∷ p) (b ∷ q) r zero    = ·-distribʳ a b (nth r zero)
convCoeff-distrib (a ∷ p) (b ∷ q) r (suc k) =
  trans (cong₂ _+F_ (·-distribʳ a b (nth r (suc k))) (convCoeff-distrib p q r k))
        (rearrange (a · nth r (suc k)) (b · nth r (suc k)) (convCoeff p r k) (convCoeff q r k))

-- *P right-distributivity, via the method (nth-ext +F nth-*P +F the per-coord identity). No subst.
*P-distribʳ : ∀ {n m} (p q : Polynomial n) (r : Polynomial m)
            → (p +ⱽ q) *P r ≡ (p *P r) +ⱽ (q *P r)
*P-distribʳ p q r = nth-ext _ _ (λ k →
  trans (nth-*P (p +ⱽ q) r k)
  (trans (convCoeff-distrib p q r k)
  (trans (cong₂ _+F_ (sym (nth-*P p r k)) (sym (nth-*P q r k)))
         (sym (nth-+ⱽ (p *P r) (q *P r) k)))))

-- *P left-distributivity (linearity in arg 2) → with distribʳ gives BILINEARITY.
-- convCoeff recurses on arg 1, so arg 2 enters only via nth — clean, no reindex.
convCoeff-distribˡ : ∀ {n m} (r : Polynomial n) (p q : Polynomial m) (k : ℕ)
                   → convCoeff r (p +ⱽ q) k ≡ convCoeff r p k +F convCoeff r q k
convCoeff-distribˡ []      p q k       = sym (+-identityˡ 𝟘)
convCoeff-distribˡ (a ∷ r) p q zero    =
  trans (cong (a ·_) (nth-+ⱽ p q zero)) (·-distribˡ-+ a (nth p zero) (nth q zero))
convCoeff-distribˡ (a ∷ r) p q (suc k) =
  trans (cong₂ _+F_ (trans (cong (a ·_) (nth-+ⱽ p q (suc k)))
                          (·-distribˡ-+ a (nth p (suc k)) (nth q (suc k))))
                   (convCoeff-distribˡ r p q k))
        (rearrange (a · nth p (suc k)) (a · nth q (suc k)) (convCoeff r p k) (convCoeff r q k))

*P-distribˡ : ∀ {n m} (r : Polynomial n) (p q : Polynomial m)
            → r *P (p +ⱽ q) ≡ (r *P p) +ⱽ (r *P q)
*P-distribˡ r p q = nth-ext _ _ (λ k →
  trans (nth-*P r (p +ⱽ q) k)
  (trans (convCoeff-distribˡ r p q k)
  (trans (cong₂ _+F_ (sym (nth-*P r p k)) (sym (nth-*P r q k)))
         (sym (nth-+ⱽ (r *P p) (r *P q) k)))))
