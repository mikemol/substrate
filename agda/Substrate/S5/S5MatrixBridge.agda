{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.S5.S5MatrixBridge — ⟡bridge-matrix: the WITNESSED transport
-- S5Matrix ≅ Algebra.R.Trace.CFMatrixBridge.
--
-- Both subsystems independently re-derive the 2×2 CF convergent matrix
-- (record Mat, identity I, CF step M(a)=[[a,1],[1,0]], product _·_, and the
-- convergent-state matrix) — jea_pysim flags them cross-module IDENTICAL. The
-- WRONG move is to collapse one into the other: that would delete the bridge
-- between the S5 fuel-metering subsystem and the R.Trace continued-fraction
-- subsystem. The RIGHT move (the KleinV4≅V₄ pattern) is to WITNESS it. This
-- module records:
--
--   1. the structural ISO  S5Matrix.Mat ≅ CFMatrixBridge.Mat (to/from + round-trips);
--   2. that `to` is an ALGEBRA MORPHISM — it preserves I, M(a), _·_, state (all
--      refl: the two definitions coincide), so the two subsystems' matrices are
--      the SAME monoid-with-generators, not merely isomorphic carriers;
--   3. the RELATIONSHIP-OF-RELATIONSHIPS: S5Matrix's matrices INHERIT, through the
--      transport, CFMatrixBridge.Properties's determinant theory — detM = det4, and
--      one CF step NEGATES it by the repo's own det-flip (◆T3's (−1)ⁿ cochain). That
--      is the connection S5Matrix only CITED in prose ("det-flip IS ◆T3's (−1)ⁿ"),
--      now machine-checked: the S5 fuel-runner's 2×2 state IS the CF convergent
--      matrix, AND its determinant IS the (−1)ⁿ cochain.
------------------------------------------------------------------------

module Substrate.S5.S5MatrixBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq  using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Z using (ℤ; -ℤ_)
open import Substrate.Algebra.R.Trace.Properties using (det4)

import Substrate.S5.S5Matrix                            as S5M
import Substrate.Algebra.R.Trace.CFMatrixBridge         as CF
import Substrate.Algebra.R.Trace.CFMatrixBridge.Properties as CFP

------------------------------------------------------------------------
-- 1. The structural ISO: the two Mat records are one 2×2 ℕ-matrix.
------------------------------------------------------------------------
to : S5M.Mat → CF.Mat
to (S5M.mat a b c d) = CF.mat a b c d

from : CF.Mat → S5M.Mat
from (CF.mat a b c d) = S5M.mat a b c d

from-to : (m : S5M.Mat) → from (to m) ≡ m
from-to (S5M.mat a b c d) = refl

to-from : (m : CF.Mat) → to (from m) ≡ m
to-from (CF.mat a b c d) = refl

------------------------------------------------------------------------
-- 2. `to` is an ALGEBRA MORPHISM: it preserves the whole matrix structure.
------------------------------------------------------------------------
to-I : to S5M.I ≡ CF.I
to-I = refl

to-M : (q : ℕ) → to (S5M.M q) ≡ CF.M q
to-M q = refl

to-· : (x y : S5M.Mat) → to (x S5M.· y) ≡ (to x) CF.· (to y)
to-· (S5M.mat _ _ _ _) (S5M.mat _ _ _ _) = refl

to-state : (p₁ q₁ p₀ q₀ : ℕ) → to (S5M.state p₁ q₁ p₀ q₀) ≡ CF.state p₁ q₁ p₀ q₀
to-state p₁ q₁ p₀ q₀ = refl

------------------------------------------------------------------------
-- 3. THEOREM TRANSPORT (relationship-of-relationships).
------------------------------------------------------------------------
-- (a) the two modules' conv-step-is-matmul are ONE theorem: apply `to` to
-- S5Matrix's, push it through the morphism (to-·, to-M), and land on
-- CFMatrixBridge's right-multiply-by-M(a) form.
conv-step-agree :
  (a p₁ q₁ p₀ q₀ : ℕ) →
  to (S5M.state (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁)
  ≡ (to (S5M.state p₁ q₁ p₀ q₀)) CF.· (CF.M a)
conv-step-agree a p₁ q₁ p₀ q₀ =
  trans (cong to (S5M.conv-step-is-matmul a p₁ q₁ p₀ q₀))
        (trans (to-· (S5M.state p₁ q₁ p₀ q₀) (S5M.M a))
               (cong ((to (S5M.state p₁ q₁ p₀ q₀)) CF.·_) (to-M a)))

-- (b) S5Matrix's matrices INHERIT CFMatrixBridge's determinant, via `to`.
detM : S5M.Mat → ℤ
detM m = CF.detM (to m)

-- its convergent state's determinant IS det4 (the neighbour determinant)…
det-is-det4 : (p₁ q₁ p₀ q₀ : ℕ)
            → detM (S5M.state p₁ q₁ p₀ q₀) ≡ det4 p₁ q₁ p₀ q₀
det-is-det4 = CFP.det-is-det4

-- …and one CF step NEGATES it, by the repo's own det-flip (◆T3's (−1)ⁿ). The
-- sign story S5Matrix only cited, now carried onto its matrices by the bridge.
matrix-det-flip :
  (a p₁ q₁ p₀ q₀ : ℕ) →
  detM (S5M.state (a * p₁ + p₀) (a * q₁ + q₀) p₁ q₁)
  ≡ -ℤ (detM (S5M.state p₁ q₁ p₀ q₀))
matrix-det-flip = CFP.matrix-det-flip
