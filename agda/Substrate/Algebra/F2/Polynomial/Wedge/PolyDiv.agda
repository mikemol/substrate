------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.PolyDiv
--
-- THE POLY COLLAPSE — F₂[x] division IS a generic wedge. The parallel
-- `PolyEEATrace` construction existed because the old `recon : ℕ → C → C → C`
-- baked a ℕ COUNT as the quotient, but polynomial division's quotient is a
-- POLYNOMIAL. Now that `recon : C → C → C → C` takes a CARRIER REPRESENTATIVE,
-- F₂[x] is a genuine `DivStr` instance (`Poly-div`), and the polynomial
-- Euclidean trace embeds into the generic `Trace` (`fromPolyEEATrace`) — so the
-- generic `collapse` / `trace-fold` apply, no faithful copy needed.
--
-- The crux is the LENGTH mismatch: `q *P b` is length-additive, so `a ≡ q *P b
-- +P r` is not a strict `Poly` equation (it is the coefficient-wise `recon-nth`,
-- Graded.Div). But `div-quot` keeps the dividend's length n, so `recon` builds a
-- length-n poly with the right coefficients (`buildPoly`) and the wedge-eq closes
-- by `buildPoly-correct` ∘ `recon-nth` — pointwise coefficients, lifted to ≡.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.PolyDiv where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.Wedge
  using (DivStr; Trace; done; more; collapse; quot; rem)
  renaming (Wedge to Wedge⟦478f66a6⟧)   -- specialize the colliding name by shape
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Div as Div
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; div-quot; PolyEEATrace; base; step)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEAFold
  using (gcd-fold-poly; gcd-fold-poly-correct)

-- the F₂ coefficient machinery — the SAME instantiation Graded.Div uses.
open F.Over F₂-CommRing using (Poly; nth; convCoeff; _+_)

------------------------------------------------------------------------
-- 1. A length-n poly with prescribed coefficients (the inverse of nth).
------------------------------------------------------------------------

buildPoly : (n : ℕ) → (ℕ → F₂) → Poly n
buildPoly zero    g = []
buildPoly (suc n) g = g zero ∷ buildPoly n (λ k → g (suc k))

-- if v's coefficients are g everywhere, v IS buildPoly n g (the gap-closer).
buildPoly-correct : {n : ℕ} (v : Poly n) (g : ℕ → F₂) →
                    ((k : ℕ) → nth v k ≡ g k) → v ≡ buildPoly n g
buildPoly-correct []      g hyp = refl
buildPoly-correct (x ∷ v) g hyp =
  cong₂ _∷_ (hyp zero) (buildPoly-correct v (λ k → g (suc k)) (λ k → hyp (suc k)))

------------------------------------------------------------------------
-- 2. F₂[x] as a DivStr: recon q b r = "q·b + r", coefficient-wise at length |q|.
--    The quotient q is a carrier element (a polynomial), not a count.
------------------------------------------------------------------------

recon-poly : QPoly → QPoly → QPoly → QPoly
recon-poly (n , qv) (_ , bv) (_ , rv) =
  n , buildPoly n (λ k → convCoeff qv bv k + nth rv k)

Poly-div : DivStr
Poly-div = record { C = QPoly ; z = zero-q ; recon = recon-poly }

------------------------------------------------------------------------
-- 3. Each division step is a generic wedge; the witness is recon-nth.
------------------------------------------------------------------------

step-wedge : (d : ℕ) (f-lo : Vec F₂ (suc d)) (n : ℕ) (av : Vec F₂ n) →
             Wedge⟦478f66a6⟧ Poly-div (n , av) (divisor-q d f-lo)
step-wedge d f-lo n av = record
  { quot     = div-quot d f-lo (n , av)
  ; rem      = div-rem d f-lo (n , av)
  ; wedge-eq = cong (n ,_)
      (buildPoly-correct av _ (λ k → Div.Over.recon-nth F₂-CommRing d f-lo av k))
  }

------------------------------------------------------------------------
-- 4. THE COLLAPSE: the polynomial Euclidean trace IS a generic trace.
------------------------------------------------------------------------

fromPolyEEATrace : {a b g : QPoly} → PolyEEATrace a b g → Trace Poly-div a b g
fromPolyEEATrace (base a)              = done a
fromPolyEEATrace {n , av} (step d f-lo rec) =
  more (divisor-q d f-lo) (step-wedge d f-lo n av) (fromPolyEEATrace rec)

-- the poly gcd-fold IS the generic forgetful read (collapse) of that trace:
-- the parallel `gcd-fold-poly` is no longer a separate fact, just the generic one.
gcd-fold-poly-is-collapse : {a b g : QPoly} (t : PolyEEATrace a b g) →
                            gcd-fold-poly t ≡ collapse (fromPolyEEATrace t)
gcd-fold-poly-is-collapse t = gcd-fold-poly-correct t

------------------------------------------------------------------------
-- 5. RECOVER f-lo FROM THE DIVISOR (the bezout-collapse enabler).
--
-- gcd-fold collapses cleanly because it reads only the trace indices. The
-- Bézout fold (BezoutFold) is harder: its STEP RECURRENCE needs only the
-- quotient (`quot w`, already carried by the generic wedge), but its CORRECTNESS
-- needs `recon-nth` (the reconstruction ∀k) — and `wedge-eq` only pins the
-- coefficients for k < |a| (a QPoly ≡ cannot constrain k beyond the length).
-- So a generic-wedge bezout step must call the REAL `recon-nth`, which needs the
-- divisor's monic data (d, f-lo). In char-2 that data is RECOVERABLE from the
-- divisor polynomial itself: b-poly = snoc (-P f-lo) 𝟙 and -P = id, so
-- f-lo = vinit b-poly. This is the concrete enabler the user named.
------------------------------------------------------------------------

module _ (d : ℕ) (f-lo : Vec F₂ (suc d)) where
  open Div.Over F₂-CommRing d f-lo using (b-poly; snoc; vinit; -P; 𝟙)

  -- char-2: polynomial negation is the identity (componentwise -_ = id).
  -P-id : {n : ℕ} (v : Vec F₂ n) → -P v ≡ v
  -P-id []      = refl
  -P-id (x ∷ v) = cong₂ _∷_ refl (-P-id v)

  vinit-snoc : {n : ℕ} (w : Vec F₂ n) (x : F₂) → vinit (snoc w x) ≡ w
  vinit-snoc []      x = refl
  vinit-snoc (a ∷ w) x = cong (a ∷_) (vinit-snoc w x)

  -- f-lo is the low part of the divisor: drop its (monic) top coefficient.
  recover-flo : vinit b-poly ≡ f-lo
  recover-flo = trans (vinit-snoc (-P f-lo) 𝟙) (-P-id f-lo)
