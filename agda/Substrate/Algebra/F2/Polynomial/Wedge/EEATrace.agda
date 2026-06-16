------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.EEATrace  (AI-17 B-EEA-TRACE)
--
-- The polynomial Euclidean trace over F₂[x] — a faithful mirror of the ℕ
-- `Nat/GCD/EEATrace` (base/step), the trace-as-data architecture that keeps
-- the EEA termination structural (Acc/fuel quarantined in the builder).
--
-- REUSE, not re-implementation: the per-step division is `Graded.Div.divmod`
-- (instantiated at each divisor's (d, f-lo)); the varying remainder dimension
-- `Poly (suc d)` rides as the trace INDEX (a `QPoly = Σ ℕ (Vec F₂)`), exactly
-- as ℕ `EEATrace.step` carries `suc b`/`rem w`. No new long division. The
-- reconstruction equation (`Div.recon-nth`) and degree bound (`lp-bound`) stay
-- available as theorems for the Bézout fold (B-EEA-FOLD) — no need to carry
-- them in the datatype, since `divmod` is deterministic.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.EEATrace where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; [])
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Algebra.F2 using (F₂)
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
import Substrate.Algebra.Polynomial.Graded.Div as Div

-- a polynomial packed with its length — the trace's uniform carrier.
QPoly : Set
QPoly = Σ ℕ (Vec F₂)

zero-q : QPoly
zero-q = 0 , []

-- the monic divisor y^(suc d) − f-lo, and the per-step division — all REUSING divmod.
divisor-q : (d : ℕ) (f-lo : Vec F₂ (suc d)) → QPoly
divisor-q d f-lo = suc (suc d) , Div.Over.b-poly F₂-CommRing d f-lo

div-rem : (d : ℕ) (f-lo : Vec F₂ (suc d)) → QPoly → QPoly
div-rem d f-lo (n , a) = suc d , Div.Over.r-div F₂-CommRing d f-lo a

div-quot : (d : ℕ) (f-lo : Vec F₂ (suc d)) → QPoly → QPoly
div-quot d f-lo (n , a) = n , Div.Over.q-div F₂-CommRing d f-lo a

-- gcd(a, b): base = gcd(a, 𝟘) = a; step divides a by the monic divisor (d, f-lo)
-- and recurses on (divisor, remainder) — the ℕ EEATrace shape, polynomials.
data PolyEEATrace : QPoly → QPoly → QPoly → Set where
  base : (a : QPoly) → PolyEEATrace a zero-q a
  step : ∀ {a g} (d : ℕ) (f-lo : Vec F₂ (suc d)) →
         PolyEEATrace (divisor-q d f-lo) (div-rem d f-lo a) g →
         PolyEEATrace a (divisor-q d f-lo) g
