------------------------------------------------------------------------
-- Substrate.Algebra.Polynomial.Graded.PolyDivWedge
--
-- The CR-GENERIC polynomial wedge: polynomial division IS a generic `Wedge`,
-- over ANY CommutativeRing. The single source `Algebra.F2.Polynomial.Wedge.PolyDiv`
-- derives from (is the F₂ instance of). Every underpinning is already
-- CommRing-parametric (`convCoeff`/`nth`/`+` from `FromCommRing.Over CR`;
-- `b-poly`/`q-div`/`r-div`/`recon-nth` from `Div.Over CR`), so this is a
-- mechanical generalization, not new machinery.
--
--   `Poly-div`   : the polynomial wedge carrier — C = QPolyR (Σ ℕ (Vec A)),
--                  recon q b r = (q · b) + r (the quotient is a POLYNOMIAL = a
--                  carrier representative; the current `Wedge.recon : C→C→C→C` fits).
--   `step-wedge` : each Euclidean step IS a `Wedge Poly-div a (divisor-q d f-lo)`,
--                  `wedge-eq` from `Div.Over.recon-nth` — over any CommRing.
--
-- The FreeUP-aligned spine (the FreeUP/`trace-fold`/`package-comm` are all
-- carrier-generic; this matches that shape, with PolyDiv the F₂ vertex). Zero
-- postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Polynomial.Graded.PolyDivWedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)
open import Substrate.Algebra.Wedge
  using (DivStr) renaming (Wedge to Wedge⟦478f66a6⟧)   -- shape-specialized (ratchet)
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Div as Div

module Over {A : Set} (CR : CommutativeRing A) where
  open F.Over CR using (Poly; nth; convCoeff; _+_)

  QPolyR : Set
  QPolyR = Σ ℕ (Vec A)

  zero-qR : QPolyR
  zero-qR = 0 , []

  buildPoly : (n : ℕ) → (ℕ → A) → Poly n
  buildPoly zero    g = []
  buildPoly (suc n) g = g zero ∷ buildPoly n (λ k → g (suc k))

  buildPoly-correct : {n : ℕ} (v : Poly n) (g : ℕ → A) →
                      ((k : ℕ) → nth v k ≡ g k) → v ≡ buildPoly n g
  buildPoly-correct []      g hyp = refl
  buildPoly-correct (x ∷ v) g hyp =
    cong₂ _∷_ (hyp zero) (buildPoly-correct v (λ k → g (suc k)) (λ k → hyp (suc k)))

  -- recon q b r = (q · b) + r  (the quotient q is a polynomial — a carrier rep).
  recon-poly : QPolyR → QPolyR → QPolyR → QPolyR
  recon-poly (n , qv) (_ , bv) (_ , rv) =
    n , buildPoly n (λ k → convCoeff qv bv k + nth rv k)

  Poly-div : DivStr QPolyR
  Poly-div = record { z = zero-qR ; recon = recon-poly }

  divisor-q : (d : ℕ) (f-lo : Vec A (suc d)) → QPolyR
  divisor-q d f-lo = suc (suc d) , Div.Over.b-poly CR d f-lo

  div-rem : (d : ℕ) (f-lo : Vec A (suc d)) → QPolyR → QPolyR
  div-rem d f-lo (n , a) = suc d , Div.Over.r-div CR d f-lo a

  div-quot : (d : ℕ) (f-lo : Vec A (suc d)) → QPolyR → QPolyR
  div-quot d f-lo (n , a) = n , Div.Over.q-div CR d f-lo a

  -- THE WEDGE: each Euclidean division step is a generic `Wedge`, over any CommRing.
  step-wedge : (d : ℕ) (f-lo : Vec A (suc d)) (n : ℕ) (av : Vec A n) →
               Wedge⟦478f66a6⟧ Poly-div (n , av) (divisor-q d f-lo)
  step-wedge d f-lo n av = record
    { quot     = div-quot d f-lo (n , av)
    ; rem      = div-rem d f-lo (n , av)
    ; wedge-eq = cong (n ,_)
        (buildPoly-correct av _ (λ k → Div.Over.recon-nth CR d f-lo av k))
    }
