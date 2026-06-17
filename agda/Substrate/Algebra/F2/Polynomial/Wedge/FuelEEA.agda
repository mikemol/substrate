------------------------------------------------------------------------
-- Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA  (the fuel-EEA, B-COMPUTE)
--
-- The extended-Euclidean construction that PRODUCES the Bézout witness for
-- inverting a polynomial `a` modulo the monic divisor `divisor-q d f-lo`.
-- This is the self-contained, buildable path to the GF(2⁸) inverse: it does
-- NOT use the (structurally uninhabited) `PolyEEATrace`, and needs no
-- cross-session machinery.  It glues the landed pieces:
--
--   trim            — present each remainder as monic exact-degree (or zero)
--   step-bezout-poly — the back-substitution s·a + t·m = r at each step
--   base/unit-bezout — the gcd-is-divisor / gcd-is-unit terminals
--   bezout-cong-b    — transport a witness across a value-equal divisor
--   monic-pres       — a monic full-length poly IS the divisor b-poly
--
-- The one subtlety is INSTANCE TRANSPORT: `vinit`/`vlast` are pure Vec
-- recursions (Mod.agda:59-64) that don't use (d, f-lo), so they agree across
-- `Div.Over` instances — but the projections only reduce WITHIN an instance,
-- not across.  `vlast-cross`/`vinit-cross` bridge the gap by induction; this
-- is the "common structure" (the instance-free recursion) under the two
-- instance-tagged ops, and is what lets a varying-degree recursion typecheck.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Polynomial.Wedge.FuelEEA where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.EEATrace
  using (QPoly; zero-q; divisor-q; div-rem)
open import Substrate.Algebra.F2.Polynomial.Wedge.BezoutFold
  using (BezoutNthWitness; base-bezout-poly; step-bezout-poly; bezout-cong-b;
         unit-bezout; convCoeff-one)
open import Substrate.Algebra.F2.Polynomial.Wedge.Trim
  using (trim; Trim; is-zero; is-monic)
import Substrate.Algebra.F2.Polynomial.Wedge.ComputeTrace as CT
import Substrate.Algebra.Polynomial.Graded.Div as D
open D.Over F₂-CommRing 0 (F2.𝟘 ∷ []) using (Poly; nth; convCoeff; vinit; vlast; +-identityʳ)

-- cross-instance transport: vlast/vinit agree across Div.Over instances
-- (provable by induction; the projections reduce within each instance).
vlast-cross : {d₀ d₁ : ℕ} (f₀ : Vec F2.F₂ (suc d₀)) (f₁ : Vec F2.F₂ (suc d₁))
              {n : ℕ} (v : Vec F2.F₂ (suc n))
            → D.Over.vlast F₂-CommRing d₀ f₀ v ≡ D.Over.vlast F₂-CommRing d₁ f₁ v
vlast-cross f₀ f₁ {zero}  (x ∷ []) = refl
vlast-cross f₀ f₁ {suc n} (x ∷ v)  = vlast-cross f₀ f₁ v

vinit-cross : {d₀ d₁ : ℕ} (f₀ : Vec F2.F₂ (suc d₀)) (f₁ : Vec F2.F₂ (suc d₁))
              {n : ℕ} (v : Vec F2.F₂ (suc n))
            → D.Over.vinit F₂-CommRing d₀ f₀ v ≡ D.Over.vinit F₂-CommRing d₁ f₁ v
vinit-cross f₀ f₁ {zero}  (x ∷ []) = refl
vinit-cross f₀ f₁ {suc n} (x ∷ v)  = cong (x ∷_) (vinit-cross f₀ f₁ v)

-- THE FUEL-EEA: build the Bézout witness for inverting `a` modulo the divisor
-- `divisor-q d f-lo`, by the extended Euclidean recursion.  Fuel bounds the
-- degree-descent (a divisor of degree suc d needs ≤ suc d steps).
fuel-bezout : ℕ → (a : QPoly) (d : ℕ) (f-lo : Vec F2.F₂ (suc d))
            → Σ QPoly (BezoutNthWitness a (divisor-q d f-lo))
-- out of fuel (unreachable when fuel ≥ degree): the self-witness 𝟙·a + 0·b = a.
fuel-bezout zero a d f-lo =
  a , ((suc zero , (F2.𝟙 ∷ [])) , zero-q ,
       (λ k → trans (+-identityʳ (convCoeff (F2.𝟙 ∷ []) (proj₂ a) k))
                    (convCoeff-one (proj₂ a) k)))
fuel-bezout (suc fuel) a d f-lo with trim (suc d) (proj₂ (div-rem d f-lo a))
... | is-zero h =
  divisor-q d f-lo ,
  step-bezout-poly {g = divisor-q d f-lo} d f-lo
    (bezout-cong-b {b′ = div-rem d f-lo a} {g = divisor-q d f-lo} (λ j → sym (h j)) (base-bezout-poly (divisor-q d f-lo)))
... | is-monic zero rr hm hc =
  (suc zero , rr) ,
  step-bezout-poly {g = suc zero , rr} d f-lo
    (bezout-cong-b {b′ = div-rem d f-lo a} {g = suc zero , rr} hc (unit-bezout (divisor-q d f-lo) (suc zero , rr)))
... | is-monic (suc e′) rr hm hc =
  let g,sub = fuel-bezout fuel (divisor-q d f-lo) e′ (vinit rr)
      hm′ = trans (vlast-cross (vinit rr) (F2.𝟘 ∷ []) rr) hm
      hf′ = vinit-cross (vinit rr) (F2.𝟘 ∷ []) rr
  in proj₁ g,sub ,
     step-bezout-poly {g = proj₁ g,sub} d f-lo
       (bezout-cong-b {b′ = div-rem d f-lo a} {g = proj₁ g,sub}
         (λ j → trans (cong (λ z → nth z j) (sym (CT.Pres.monic-pres e′ (vinit rr) rr hm′ hf′))) (hc j))
         (proj₂ g,sub))
