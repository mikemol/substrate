------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Step
--
-- THE STEP: char-2 Bézout back-substitution, new s = t', new t = s' + t'·q.
--
-- ⟡mod-content-squeeze (propagation): BezoutFold measured 151MB. A first split left the
-- step-bearing tip at 137, so the char-2 back-substitution step is separated from the
-- fold + fuel-EEA glue. Each part carries its own content over the shared ~90MB floor.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Step where

open import Substrate.Foundation.Nat using (ℕ; zero; suc) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-assoc to +ℕ-assoc; +-comm to +ℕ-comm)
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

open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold.Base
private variable n m l : ℕ

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

