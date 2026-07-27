------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base
--
-- The convCoeff infrastructure for the polynomial Bézout fold: `convCoeff-one`, the
-- coefficient-wise invariant `BezoutNthWitness`, the base case, the congruence/subst/
-- zero/pad/assoc/split lemmas, and the char-2 rearrangement.
--
-- ⟡mod-content-squeeze (propagation): BezoutFold measured 151MB against the 128 cap.
-- Split at the convCoeff-infrastructure / step-and-fold boundary; `BezoutFold` stays the
-- tip so consumers are unchanged. (The ~90MB Graded LOAD FLOOR is shared by both parts;
-- only the content divides.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using ()
  renaming (+-assoc to +ℕ-assoc; +-comm to +ℕ-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
open F.Over F₂-CommRing
import Substrate.Algebra.Polynomial.Graded.Div as D
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; PolyEEATrace)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEAFold using (eea-fold-poly)

private variable n m l : ℕ


-- convCoeff by the unit polynomial [𝟙] is nth (the *P-identityˡ, convCoeff form).
convCoeff-one : (v : Poly n) (k : ℕ) → convCoeff (𝟙 ∷ []) v k ≡ nth v k
convCoeff-one v zero    = *-identityˡ (nth v zero)
convCoeff-one v (suc k) = trans (+-identityʳ _) (*-identityˡ (nth v (suc k)))

-- the Bézout invariant, coefficient-wise (convCoeff form, avoiding the *P
-- length-mismatch — the recon-nth method): convCoeff s a + convCoeff t b = g, ∀k.
BezoutNthWitness : QPoly → QPoly → QPoly → Set
BezoutNthWitness a b g =
  Σ QPoly λ s → Σ QPoly λ t →
    (k : ℕ) → (convCoeff (proj₂ s) (proj₂ a) k + convCoeff (proj₂ t) (proj₂ b) k)
              ≡ nth (proj₂ g) k

-- base: gcd(a, 0) = a; bridge 1·a + 0·0 = a.
base-bezout-poly : (a : QPoly) → BezoutNthWitness a zero-q a
base-bezout-poly a =
  (suc zero , (𝟙 ∷ [])) , zero-q ,
  (λ k → trans (+-identityʳ _) (convCoeff-one (proj₂ a) k))

------------------------------------------------------------------------
-- the step's reusable convCoeff infrastructure.
------------------------------------------------------------------------

-- char-2 self-cancellation — the proof lives ONCE in Algebra.F2 (⟡A3: single source); this is a
-- thin re-export alias so the local call sites are unchanged.
+-self : (x : F2.F₂) → x + x ≡ 𝟘
+-self = F2.+-self-inverse

-- convCoeff is congruent in its 2nd argument under pointwise nth-equality.
convCoeff-cong-r : (p : Poly n) {q : Poly m} {q' : Poly l}
                 → ((j : ℕ) → nth q j ≡ nth q' j)
                 → (k : ℕ) → convCoeff p q k ≡ convCoeff p q' k
convCoeff-cong-r []      h k       = refl
convCoeff-cong-r (a ∷ p) h zero    = cong (a *_) (h zero)
convCoeff-cong-r (a ∷ p) h (suc k) = cong₂ _+_ (cong (a *_) (h (suc k))) (convCoeff-cong-r p h k)

-- subst on the 1st argument is invisible to convCoeff.
convCoeff-subst-l : {n n' : ℕ} (eq : n ≡ n') (v : Poly n) (X : Poly m) (k : ℕ)
                  → convCoeff (subst Poly eq v) X k ≡ convCoeff v X k
convCoeff-subst-l refl v X k = refl

-- convCoeff by an all-zero first argument is 𝟘.
convCoeff-replicate-zero : (j : ℕ) (X : Poly m) (k : ℕ) → convCoeff (replicate j 𝟘) X k ≡ 𝟘
convCoeff-replicate-zero zero    X k       = refl
convCoeff-replicate-zero (suc j) X zero    = *-absorbˡ (nth X zero)
convCoeff-replicate-zero (suc j) X (suc k) =
  trans (cong₂ _+_ (*-absorbˡ (nth X (suc k))) (convCoeff-replicate-zero j X k)) (+-identityˡ 𝟘)

-- pad-end (high-zero padding) is invisible to convCoeff in the 1st argument.
convCoeff-pad-endˡ : (j : ℕ) (v : Poly n) (X : Poly m) (k : ℕ)
                   → convCoeff (pad-end j v) X k ≡ convCoeff v X k
convCoeff-pad-endˡ j []      X k       = convCoeff-replicate-zero j X k
convCoeff-pad-endˡ j (a ∷ v) X zero    = refl
convCoeff-pad-endˡ j (a ∷ v) X (suc k) = cong ((a * nth X (suc k)) +_) (convCoeff-pad-endˡ j v X k)

-- convCoeff associativity: t·(q·B) coefficients = (t·q)·B coefficients.
convCoeff-assoc : (t : Poly n) (q : Poly m) (B : Poly l) (k : ℕ)
                → convCoeff t (q *P B) k ≡ convCoeff (t *P q) B k
convCoeff-assoc {n} {m} {l} t q B k =
  trans (sym (nth-*P t (q *P B) k))
  (trans (cong (λ z → nth z k) (sym (*P-assoc t q B)))
  (trans (nth-subst (+ℕ-assoc n m l) ((t *P q) *P B) k)
         (nth-*P (t *P q) B k)))

-- split convCoeff over a pointwise sum in argument 2 (no padded poly needed).
convCoeff-split-r : {p : ℕ} (t : Poly n) {Y : Poly m} {Z : Poly l} {X : Poly p}
                  → ((j : ℕ) → nth X j ≡ nth Y j + nth Z j)
                  → (k : ℕ) → convCoeff t X k ≡ convCoeff t Y k + convCoeff t Z k
convCoeff-split-r []      h k       = sym (+-identityˡ 𝟘)
convCoeff-split-r (a ∷ t) h zero    = trans (cong (a *_) (h zero)) (*-distribˡ a _ _)
convCoeff-split-r (a ∷ t) {Y} {Z} h (suc k) =
  trans (cong₂ _+_ (trans (cong (a *_) (h (suc k))) (*-distribˡ a _ _))
                   (convCoeff-split-r t h k))
        (rearrange (a * nth Y (suc k)) (a * nth Z (suc k)) (convCoeff t Y k) (convCoeff t Z k))

-- char-2 cancellation rearrangement.
char2-rearr : (X Y Z : F2.F₂) → (X + Y) + (Z + X) ≡ Z + Y
char2-rearr X Y Z =
  trans (+-assoc X Y (Z + X))
  (trans (cong (X +_) (sym (+-assoc Y Z X)))
  (trans (cong (X +_) (+-comm (Y + Z) X))
  (trans (sym (+-assoc X X (Y + Z)))
  (trans (cong (_+ (Y + Z)) (+-self X))
  (trans (+-identityˡ (Y + Z)) (+-comm Y Z))))))

------------------------------------------------------------------------
