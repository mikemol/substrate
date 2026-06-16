------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold  (B-EEA-FOLD-bez ✓)
--
-- The polynomial Bézout fold over F₂[x] — the residual-fold (allegory ALG-6)
-- over `PolyEEATrace`, producing (s, t) with s·a + t·b = g.  The g=𝟙 case is
-- the GF(2⁸) inverse (B-EEA-INV → AI-8).  A faithful char-2 port of `Z/Bezout`
-- (base-bezout / step-bezout / eea-fold), retyped for F₂[x].
--
-- FORMULATION (either/or resolved by the build): convCoeff/nth form, NOT a
-- truncation-ring + pad.  The naive `s *P a +P t *P b ≡ g` is ill-typed (`*P`
-- length-additive ⇒ the `+P` operands differ in length).  Stated COEFFICIENT-
-- WISE via `convCoeff` (no length match needed) — the `recon-nth` method.
--
--   `bezout-poly : PolyEEATrace a b g → BezoutNthWitness a b g`
--     = eea-fold-poly base-bezout-poly step-bezout-poly.
--
-- The step recurrence is the char-2 form of Z/Bezout's (s',t')↦(t', s'−t'·q):
-- new s = t', new t = s' +P (t' *P q).  Its correctness expands `convCoeff t' a`
-- via `recon-nth` (a = q·b + r coefficient-wise) and cancels the two
-- `convCoeff (t'·q) b` terms by char-2 self-inverse (`+-self`), leaving the
-- sub-invariant `convCoeff s' b + convCoeff t' r ≡ nth g`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold where

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

-- char-2 self-cancellation.
+-self : (x : F2.F₂) → x + x ≡ 𝟘
+-self F2.𝟘 = refl
+-self F2.𝟙 = refl

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
-- the step and the fold.
------------------------------------------------------------------------

-- THE STEP: char-2 Bézout back-substitution.  new s = t', new t = s' + t'·q.
step-bezout-poly : {a g : QPoly} (d : ℕ) (f-lo : Vec F2.F₂ (suc d)) →
                   BezoutNthWitness (divisor-q d f-lo) (div-rem d f-lo a) g →
                   BezoutNthWitness a (divisor-q d f-lo) g
step-bezout-poly {a} {g} d f-lo (s' , t' , eq') = t' , new-t , eq
  where
    open D.Over F₂-CommRing d f-lo using (b-poly; q-div; r-div; recon-nth)
    S = proj₁ s'
    T = proj₁ t'
    A = proj₁ a
    vs' = proj₂ s'
    vt' = proj₂ t'
    qd  = q-div (proj₂ a)
    rd  = r-div (proj₂ a)
    tq  = vt' *P qd

    new-t : QPoly
    new-t = (S ℕ+ (T ℕ+ A))
          , (pad-end (T ℕ+ A) vs' +P subst Poly (+ℕ-comm (T ℕ+ A) S) (pad-end S tq))

    vnt = proj₂ new-t

    stepA : (k : ℕ) → convCoeff vnt b-poly k ≡ convCoeff vs' b-poly k + convCoeff tq b-poly k
    stepA k =
      trans (convCoeff-distrib (pad-end (T ℕ+ A) vs')
                               (subst Poly (+ℕ-comm (T ℕ+ A) S) (pad-end S tq)) b-poly k)
            (cong₂ _+_ (convCoeff-pad-endˡ (T ℕ+ A) vs' b-poly k)
                       (trans (convCoeff-subst-l (+ℕ-comm (T ℕ+ A) S) (pad-end S tq) b-poly k)
                              (convCoeff-pad-endˡ S tq b-poly k)))

    hyp : (j : ℕ) → nth (proj₂ a) j ≡ nth (qd *P b-poly) j + nth rd j
    hyp j = trans (recon-nth (proj₂ a) j) (cong (_+ nth rd j) (sym (nth-*P qd b-poly j)))

    stepB : (k : ℕ) → convCoeff vt' (proj₂ a) k ≡ convCoeff tq b-poly k + convCoeff vt' rd k
    stepB k = trans (convCoeff-split-r vt' hyp k)
                    (cong (_+ convCoeff vt' rd k) (convCoeff-assoc vt' qd b-poly k))

    eq : (k : ℕ) → convCoeff vt' (proj₂ a) k + convCoeff vnt b-poly k ≡ nth (proj₂ g) k
    eq k = trans (cong₂ _+_ (stepB k) (stepA k))
           (trans (char2-rearr (convCoeff tq b-poly k) (convCoeff vt' rd k) (convCoeff vs' b-poly k))
                  (eq' k))

-- THE FOLD: the Bézout bridge over the polynomial EEA trace.
bezout-poly : {a b g : QPoly} → PolyEEATrace a b g → BezoutNthWitness a b g
bezout-poly t = eea-fold-poly {T = BezoutNthWitness} base-bezout-poly
                  (λ {a} {g} d f-lo rec → step-bezout-poly {a} {g} d f-lo rec) t
