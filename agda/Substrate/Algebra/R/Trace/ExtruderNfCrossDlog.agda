{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderNfCrossDlog — ⟡nf-cross-dlog: the degree-k
-- Nf cross-witness on the GROUNDED exp/dlog footing (ADD 133), dissolving the
-- asymmetric addCap hack. The additive→multiplicative codec is DLogHom.gpow-hom:
--   gpow (a + b) ≡ gpow a *Q gpow b            (exp of a sum IS a product)
-- so the Nf cross of two strands carrying exponents (shed-step logs) i, j is
--   cross i j = gpow i *Q gpow j = gpow (i + j)
-- SYMMETRIC in i, j (because + is), with NO strand forced to zero. The degree-k
-- obstruction lives in the NILPOTENT regime: instantiate with the ZERO modulus
-- f-lo = 0, so y^(suc d) ≡ 0 (nilpotent), NOT a GF irreducible (cyclic). Then
-- gpow n = yⁿ collapses at the degree bound — the residual redex's cost.
--
-- Grounded (ADD 133 reads): Graded.Div.Over CR d f-lo has divisor b = y^(suc d) −
-- f-lo; f-lo = 0 ⟹ b = y^(suc d) ⟹ y^(suc d) ≡ 0. gpow/gpow-hom are DLogHom.Over's.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderNfCrossDlog where

open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties using (+-comm)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
import Substrate.Algebra.F2 as F2
open import Substrate.Algebra.F2.CommRing using (F₂-CommRing)
open import Substrate.Algebra.F2.Polynomial.Wedge.DLogHom using (module Over)
import Substrate.Algebra.Polynomial.Graded.Div as Div

------------------------------------------------------------------------
-- THE NILPOTENT REGIME: degree bound (suc d), ZERO modulus (y^(suc d) ≡ 0). We
-- work at d = 3 (bound 4): y is a degree-4 nilpotent — the SAME degree-4
-- obstruction as NilpotentDegreeK's Rk 3, now MULTIPLICATIVELY via exp/dlog.
------------------------------------------------------------------------
d : ℕ
d = 3

f-lo₀ : Vec F2.F₂ (suc d)              -- ZERO modulus ⟹ y^(suc d) ≡ 0 (nilpotent)
f-lo₀ = replicate (suc d) F2.𝟘

open Div.Over F₂-CommRing d f-lo₀ using (Poly; _*Q_; oneC; 𝟎C)
open Over d f-lo₀ using (gpow; gpow-hom)

------------------------------------------------------------------------
-- ① THE CROSS, exp/dlog form. Two Nf strands carry exponents (shed-step logs)
-- i, j; the cross is their product in the ring, gpow i *Q gpow j.
------------------------------------------------------------------------
cross-dlog : ℕ → ℕ → Poly (suc d)
cross-dlog i j = gpow i *Q gpow j

-- the codec: the cross IS gpow of the summed logs (exp of a sum is a product).
cross-is-gpow-sum : (i j : ℕ) → cross-dlog i j ≡ gpow (i + j)
cross-is-gpow-sum i j = sym (gpow-hom i j)

------------------------------------------------------------------------
-- ② SYMMETRY FOR FREE — the asymmetric hack dissolved. cross i j ≡ cross j i,
-- because both are gpow (i+j) = gpow (j+i). No strand carries the residue while
-- the other is zero; both contribute their log, added symmetrically, then exp'd.
------------------------------------------------------------------------
cross-symmetric : (i j : ℕ) → cross-dlog i j ≡ cross-dlog j i
cross-symmetric i j =
  trans (cross-is-gpow-sum i j)
        (trans (cong gpow (+-comm i j)) (sym (cross-is-gpow-sum j i)))

------------------------------------------------------------------------
-- ③ THE DEGREE-k NILPOTENT, multiplicatively. gpow (suc d) = y^(suc d) ≡ 0 in
-- the zero-modulus regime — the residual redex collapses at the degree bound.
-- (gpow (suc d) computes to 𝟎C by refl: xpow (suc d) oneC shifts the 1 off the
-- length-(suc d) vector, and the reduction adds f-lo·(...) = 0·(...) = 0.)
------------------------------------------------------------------------
nilpotent-at-bound : gpow (suc d) ≡ 𝟎C           -- y^(suc d) ≡ 0: genuine nilpotency
nilpotent-at-bound = refl

-- the cross of two strands whose logs SUM to the bound collapses — the maximal
-- obstruction is when i + j = suc d (the residual redex is exactly the bound).
cross-collapses-at-bound : (i j : ℕ) → i + j ≡ suc d → cross-dlog i j ≡ gpow (suc d)
cross-collapses-at-bound i j p = trans (cross-is-gpow-sum i j) (cong gpow p)

------------------------------------------------------------------------
-- THE DISSOLUTION (grounded): the additive addCap of the earlier Rₖ (ADD 131) was
-- the LOG side; here the exponents i, j ARE the logs, and gpow is exp. The cross
-- is gpow (i + j) — the additive sum of logs, symmetric, lifted to the product by
-- the codec. No strand is forced to zero: both logs add. The degree-k obstruction
-- is the sum reaching the bound (suc d), where gpow collapses (nilpotent regime).
------------------------------------------------------------------------
