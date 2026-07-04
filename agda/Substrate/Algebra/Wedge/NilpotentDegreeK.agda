{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.NilpotentDegreeK — ⟡nf-degree-k: nilpotents of degree
-- > 2, so a residual redex needing k > 2 shed-steps has a home. Wedderburn's M₂
-- caps at degree 2 (e₁₂² = 𝟎). The INVARIANT (not an ad-hoc M₃,M₄,… family):
-- nilpotency degree is a FREE PARAMETER of Nilpotent (Σ n. xⁿ ≡ z, Wedge.Mul).
--
-- The uniform carrier: TRUNCATED-℀ Rₖ = ℕ with z = 0 and "cap-collapse" addition
-- — add the shift counts, and any result ≥ suc k collapses to 0. The generator
-- gen = 1 then has pow gen n ≡ suc n for n < k, and pow gen k ≡ 0 — nilpotency
-- degree EXACTLY (suc k). The Jordan shift Nᵏ⁺¹ = 0, on the substrate's ℕ / z=0
-- MulDivStr idiom, no matrix machinery. Concretely validated at k = 3 (degree 4).
------------------------------------------------------------------------

module Substrate.Algebra.Wedge.NilpotentDegreeK where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_; _<_; _<?_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Algebra.Wedge using (DivStr; ℕ-div)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; pow; Nilpotent)

------------------------------------------------------------------------
-- capped-collapse addition at level k: add, collapse to 0 once the count reaches
-- (suc k). Decidable-< keeps it --safe and refl-computable on literals.
------------------------------------------------------------------------
addCap : (k x y : ℕ) → ℕ
addCap k x y with (x + y) <? suc k
... | yes _ = x + y          -- still below the cap: keep the shift count
... | no  _ = 0              -- reached/passed the cap: collapse (the nilpotent)

-- the truncated carrier Rₖ as a MulDivStr (base ℕ-div, z = 0).
Rk : ℕ → MulDivStr
Rk k = record { base = ℕ-div ; mul = addCap k }

-- the generator: one unit of shift.
gen : ℕ
gen = 1

------------------------------------------------------------------------
-- THE DEGREE-k NILPOTENT, validated concretely at k = 3 (nilpotency degree 4):
-- pow (Rk 3) gen n = 1 + n while 1+n < 4, then collapses. pow uses pow x 0 = x,
-- pow x (suc n) = mul x (pow x n), so:
--   pow gen 0 = 1, pow gen 1 = 2, pow gen 2 = 3, pow gen 3 = 0  (1+3=4 ≥ cap 4).
-- degree EXACTLY 4: the 3rd power is 0, the 2nd is not.
------------------------------------------------------------------------
pow3-gen : pow (Rk 3) gen 3 ≡ 0
pow3-gen = refl

pow2-gen-not-zero : pow (Rk 3) gen 2 ≡ 3
pow2-gen-not-zero = refl

-- so gen is nilpotent of degree 4 in R₃ — a degree > 2 obstruction, the Nf
-- residual cost when peel+reduce leave 3 shed-steps. Nilpotent = Σ n. genⁿ ≡ z:
gen-nilpotent-deg4 : Nilpotent (Rk 3) gen
gen-nilpotent-deg4 = 3 , pow3-gen

------------------------------------------------------------------------
-- degree-5 too (k = 4), to show the parameter genuinely varies:
--   pow gen 4 = 0 (1+4=5 ≥ cap 5), pow gen 3 = 4 ≠ 0.
------------------------------------------------------------------------
gen-nilpotent-deg5 : Nilpotent (Rk 4) gen
gen-nilpotent-deg5 = 4 , refl

pow3-gen-k4-not-zero : pow (Rk 4) gen 3 ≡ 4
pow3-gen-k4-not-zero = refl

------------------------------------------------------------------------
-- THE INVARIANT (dissolving "M₂ vs M₃ vs M₄ …"): the Nf residual obstruction is
-- ONE thing — a nilpotent cross term — graded by a single free parameter, its
-- degree. Degree 0 = clean (two-mul, ADD 129); degree 2 = M₂/e₁₂ (CrossMulGraded,
-- ADD 130); degree k+1 = gen in Rₖ (here). Not a family of ad-hoc carriers: one
-- Nilpotent predicate, one degree parameter, realised uniformly by Rₖ. The
-- "which matrix size" either/or dissolves to the value of k.
------------------------------------------------------------------------
