{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderNfCrossDlogCospan — ⟡nf-cross-dlog-cospan:
-- package the exp/dlog Nf cross (ExtruderNfCrossDlog, ADD 134) as a genuine
-- Wedge.CrossMul.CrossMix — the cospan A → R ← B form.
--
-- The dlog cross already IS a product in the Poly ring: cross-dlog i j =
-- gpow i *Q gpow j. CrossMix's cross cm p q = mul R (translate (embA cm) p)
-- (translate (embB cm) q). Taking R = the Poly ring as a MulDivStr (mul = *Q),
-- A = B = base R, and both embeddings = id-bridge, gives cross cm p q = p *Q q —
-- so feeding gpow i, gpow j reproduces cross-dlog EXACTLY. Coherence (the cross
-- is a nilpotent residue) is the ADD-134 nilpotency: gpow i *Q gpow j = gpow(i+j)
-- collapses in the zero-modulus regime.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderNfCrossDlogCospan where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Vec using (Vec; replicate)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom using (module Over)
import Substrate.Algebra.Polynomial.Graded.Div as Div
open import Substrate.Algebra.Wedge using (DivStr; z; recon)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; base; mul; Nilpotent; pow)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; translate; id-bridge)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; embA; embB; cross; Coherent)

------------------------------------------------------------------------
-- The nilpotent regime (matching ExtruderNfCrossDlog): d = 3, zero modulus.
------------------------------------------------------------------------
d : ℕ
d = 3

f-lo₀ : Vec F2.F₂ (suc d)
f-lo₀ = replicate (suc d) F2.𝟘

open Div.Over F₂-CommRing d f-lo₀ using (Poly; _*Q_; _+P_; oneC; 𝟎C)
open Over d f-lo₀ using (gpow; gpow-hom)

------------------------------------------------------------------------
-- ① The Poly ring as a MulDivStr. DivStr needs (C, z, recon); recon is only used
-- by the wedge machinery, and id-bridge's `respects` is refl, so any recon that
-- typechecks serves — take the honest recon q b r = q *Q b +P r (q·b then +r).
------------------------------------------------------------------------
Poly-DivStr : DivStr (Poly (suc d))
Poly-DivStr = record
  { z = 𝟎C
  ; recon = λ q b r → (q *Q b) +P r
  }

Poly-Mul : MulDivStr (Poly (suc d))
Poly-Mul = record { base = Poly-DivStr ; mul = _*Q_ }

------------------------------------------------------------------------
-- ② THE COSPAN: CrossMix (base Poly-Mul) (base Poly-Mul) Poly-Mul, both strands
-- embedded by id-bridge. cross this-cm p q = mul Poly-Mul p q = p *Q q.
------------------------------------------------------------------------
dlog-mix : CrossMix Poly-DivStr Poly-DivStr Poly-Mul
dlog-mix = record { embA = id-bridge Poly-DivStr ; embB = id-bridge Poly-DivStr }

-- cross dlog-mix reproduces the ExtruderNfCrossDlog cross on gpow inputs:
-- cross dlog-mix (gpow i) (gpow j) = gpow i *Q gpow j = cross-dlog i j.
cross-is-dlog : (i j : ℕ) → cross dlog-mix (gpow i) (gpow j) ≡ (gpow i *Q gpow j)
cross-is-dlog i j = refl

-- and it is gpow (i+j) — the codec, now AS the cospan's cross term (symmetric).
cross-cospan-sum : (i j : ℕ) → cross dlog-mix (gpow i) (gpow j) ≡ gpow (i + j)
cross-cospan-sum i j = sym (gpow-hom i j)

------------------------------------------------------------------------
-- ③ COHERENCE: the cross term is a nilpotent residue. In the zero-modulus regime
-- gpow (suc d) ≡ 𝟎C, so cross dlog-mix (gpow i)(gpow j) = gpow (i+j) is nilpotent
-- whenever i+j hits the bound. The clean case (i = j = 0): cross = oneC, and at the
-- max obstruction (i+j = suc d) the cross is already 𝟎C. Witness Coherent at a pair
-- whose logs sum past the bound — the cross is z after one more gpow step.
------------------------------------------------------------------------
-- cross dlog-mix (gpow (suc d)) (gpow 0) = gpow (suc d) *Q gpow 0 = gpow (suc d) = 𝟎C.
-- The cross term is ALREADY z (n = 0): gpow (suc d) ≡ 𝟎C in the zero-modulus regime.
coherent-at-bound : Coherent dlog-mix (gpow (suc d)) (gpow 0)
coherent-at-bound = 0 , refl   -- pow⁰ (cross) = cross = gpow (suc d) *Q gpow 0 = 𝟎C

------------------------------------------------------------------------
-- THE COSPAN READING (the packaging's value): the exp/dlog cross is NOT a bespoke
-- construction — it is Wedge.CrossMul's cospan A → R ← B instantiated at R = the
-- Poly ring, both strands id-embedded, cross = *Q. The symmetric codec cross i j =
-- gpow (i+j) is the CrossMix cross term; its nilpotency (zero-modulus regime) is
-- CrossMul's Coherent. ExtruderNfCrossDlog's cross-dlog was the special case; this
-- is it read as the general wedge cospan.
------------------------------------------------------------------------
