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
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.Wedge
  using (DivStr; Trace; done; more; collapse; collapse-fold; collapse-fold≡collapse; quot; rem)
  renaming (Wedge to Wedge⟦478f66a6⟧)   -- specialize the colliding name by shape
import Substrate.Algebra.Polynomial.Graded.FromCommRing as F
import Substrate.Algebra.Polynomial.Graded.Mod as M
import Substrate.Algebra.Polynomial.Graded.Quotient as Q
import Substrate.Algebra.Polynomial.Graded.Div as Div
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem; div-quot; PolyEEATrace; base; step)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEAFold
  using (gcd-fold-poly; gcd-fold-poly-correct)
import Substrate.Algebra.Polynomial.Graded.PolyDivWedge as PDW

-- the F₂ coefficient machinery — the SAME instantiation Graded.Div uses.
open F.Over F₂-CommRing using (Poly; nth; convCoeff; _+_)

------------------------------------------------------------------------
-- 1-3. SINGLE SOURCE (Ⓢ.single-source): F₂[x] division-as-wedge IS the F₂
--      instance of the CR-generic poly-wedge (Graded.PolyDivWedge). buildPoly /
--      recon-poly / Poly-div / step-wedge are DERIVED from it, not duplicated —
--      so they are ONE symbol and the F₂ ≡ generic identity is `refl` by
--      construction. This resolves the cross-module non-defeq + funext-block that
--      blocked Ⓐ.gfinv-generic (memory feedback_derive_dont_duplicate_single_source).
------------------------------------------------------------------------

open PDW.Over F₂-CommRing
  using (buildPoly; buildPoly-correct; recon-poly; Poly-div; step-wedge)

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

-- STRONGER: the poly gcd-fold is the generic TRACE-FOLD (not merely the trivial
-- index-projection `collapse`) — gcd-fold-poly factors through the carrier-uniform
-- recursor `trace-fold`. This collapse works because the gcd TARGET (the index g)
-- is INDEPENDENT of the divmod step structure; the Bézout target is NOT (see §6).
gcd-fold-poly-is-trace-fold : {a b g : QPoly} (t : PolyEEATrace a b g) →
                              gcd-fold-poly t ≡ collapse-fold (fromPolyEEATrace t)
gcd-fold-poly-is-trace-fold t =
  trans (gcd-fold-poly-correct t) (sym (collapse-fold≡collapse (fromPolyEEATrace t)))

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
  open F.Over F₂-CommRing using (𝟙)
  open M.Over F₂-CommRing d f-lo using (vinit)
  open Q.Over F₂-CommRing d f-lo using (-P)
  open Div.Over F₂-CommRing d f-lo using (b-poly; snoc)

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

  -- …and the divisor RECONSTRUCTS from that recovered low part: the (d, f-lo)
  -- presentation a Bézout step needs is fully carried by the divisor QPoly.
  divisor-recovers : divisor-q d (vinit b-poly) ≡ divisor-q d f-lo
  divisor-recovers = cong (divisor-q d) recover-flo

------------------------------------------------------------------------
-- 6. WHY BÉZOUT DOES NOT COLLAPSE TO A BARE-TRACE FOLD (the monic boundary).
--
-- gcd-fold collapses (above) because its target — the index g — is INDEPENDENT
-- of the divmod step structure. Bézout's target (BezoutNthWitness: s·a + t·b ≡ g
-- coefficient-wise) is NOT: its correctness uses `recon-nth` ∀k, which needs the
-- divisor's monic (d, f-lo) data. A wedge's `wedge-eq` only pins coefficients for
-- k < |a| (a QPoly ≡ cannot constrain k beyond the length), so the bare wedge is
-- insufficient; the step must call the real `recon-nth`.
--
-- `recover-flo` / `divisor-recovers` show that (d, f-lo) IS recoverable from the
-- divisor polynomial (char-2). So nothing is lost in `fromPolyEEATrace`. But a
-- TOTAL `bezout : Trace Poly-div a b g → BezoutNthWitness a b g` still cannot
-- exist: the bare `Trace Poly-div` admits NON-monic divisors (a `more` step with
-- an arbitrary wedge), where the recovery does not round-trip and Bézout is
-- undefined. Bézout folds the MONIC-divisor trace — which IS `PolyEEATrace` (every
-- `step`'s divisor is `divisor-q d f-lo`, monic by construction). So `bezout-poly`
-- (Wedge.BezoutFold, the residual fold over PolyEEATrace) is the right home, NOT a
-- specialization of the generic `trace-fold`. The collapse is exactly as far as
-- the target's divmod-independence allows: gcd yes, Bézout no. (Allegory ALG-6:
-- the residual fold lives over the monic refinement chain, not the bare trace.)
------------------------------------------------------------------------
