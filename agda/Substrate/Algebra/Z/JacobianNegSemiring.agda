{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.JacobianNegSemiring — ⟡jac-neg-route-C.
--
-- ROUTE C of ⟡jac-neg-three-routes: the SEMIRING GAUGE, in which negation is
-- neither fielded (Route A) nor transported (Route B) but ELIMINATED BY
-- TRANSPOSITION. A signed value becomes a pair of ℕ rails ⟨positive, negative⟩,
-- and every claim about it is re-stated as a ℕ equation with no subtraction:
--
--     a − b ≡ c − d      becomes      a + d ≡ c + b          (`_≈D_`)
--     det   ≡ −2         becomes      det⁺ + 2 ≡ det⁻ + 0    (§4)
--
-- That rewriting IS the gauge. Nothing below mentions `-ℤ_`.
--
-- ⚑ THE CARRIER IS NOT NEW — IT IS `GradedProductOver` (USER CORRECTION).
-- This module was planned around "a ℕ×ℕ difference-pair carrier, ~15 lines,
-- NEW — no Grothendieck pair exists in-tree." **That absence claim was wrong**,
-- and it was wrong the usual way: the saturation searched by NAME
-- (`Grothendieck|difference pair|_⊖_|posPart|negPart`, which finds only
-- `Category/GrothendieckConstruction.agda`'s fibrations) instead of by SHAPE.
-- The structure is `GradedProductOver _+_ 0 C` (`OrientationBimonoidal.agda:33`)
-- at the constant family `C = λ _ → ℕ`: the GRADE is one rail, the CARRIER is
-- the other, and `_∧_` together with the grading op `_+_` IS pairwise addition.
-- The fit is exact, not analogical — `_×_ A B = Σ A (λ _ → B)`
-- (`Foundation/Product.agda:46`), so the graded product's total space
-- `Σ ℕ (λ _ → ℕ)` IS `ℕ × ℕ` definitionally. RIGHT NEIGHBOUR:
-- `Logic/Evidence/DualRail.agda:58-59`, `EvCarrier C = C × C ⟨positive rail,
-- negative rail⟩` — this is that carrier at `C = ℕ`.
--
-- WHAT IS GENUINELY NEW: `split` (ℤ → the two rails) and `split-hom`. Verified
-- absent by a SHAPE search (`ℤ → ℕ × ℕ` / `ℤ → Σ ℕ` / posPart / negPart), not a
-- name search — the only `sign-magnitude` hits are prose about `_*ℤ_`'s
-- algorithm (`Z/Mul.agda:4,21`), not a splitting function.
--
-- No `data`/`record` is declared (the carrier is `_×_`), so the sum-type
-- ratchet is untouched. Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.JacobianNegSemiring where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; subst; subst-const)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc; +-identityʳ; +-assoc)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.WitnessTower.Wedge.OrientationBimonoidal
  using (GradedProductOver; GradedAssocOver)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Z.Add using (_⊖_; _+ℤ_)
open import Substrate.Algebra.Z.JacobianResidue
  using (mono; detJac; coeff; constant-part)

------------------------------------------------------------------------
-- 1. THE CARRIER — an instance of the existing graded product.
--
-- ⚑ `subst-const` (constant-family `subst` is the identity) was homed LOCALLY
-- here, flagged ⟡subst-const-home. DISCHARGED: it now lives in
-- `Foundation.Eq`, level-polymorphic — and the move was a DEDUP, not merely a
-- relocation: the same lemma had also been proved at
-- `WitnessTower/Wedge/OrientationRigCatSym.agda`. Both route through the
-- Foundation copy.
------------------------------------------------------------------------

Diff : GradedProductOver _+_ zero (λ _ → ℕ)
Diff = record { u = zero ; _∧_ = _+_ }

-- and it is a genuine graded monoid: associativity is `+-assoc`, generically.
Diff-assoc : GradedAssocOver +-assoc Diff
Diff-assoc {i} {j} {k} a b c =
  trans (subst-const (+-assoc i j k) ((a + b) + c)) (+-assoc a b c)

------------------------------------------------------------------------
-- 2. THE TWO RAILS, AND THE SUBTRACTION-FREE EQUALITY.
------------------------------------------------------------------------

-- the pairwise operation the graded product's grade-op + `_∧_` induce.
_⊞_ : (ℕ × ℕ) → (ℕ × ℕ) → (ℕ × ℕ)
(a , b) ⊞ (c , d) = (a + c , b + d)

-- ⚑ THE GAUGE, IN ONE LINE: "a − b ≡ c − d" written WITHOUT subtraction.
-- This is the Grothendieck equivalence; it is why the semiring suffices.
_≈D_ : (ℕ × ℕ) → (ℕ × ℕ) → Set
(a , b) ≈D (c , d) = a + d ≡ c + b

split : ℤ → ℕ × ℕ
split (+ n)    = (n , zero)
split (-suc n) = (zero , suc n)

------------------------------------------------------------------------
-- 3. THE GAUGE IS A HOMOMORPHISM.
--
-- `split` carries ℤ-addition to pairwise ⊞ — up to `≈D`, NOT on the nose
-- (`split (+2 +ℤ -1) = (1,0)` while `split (+2) ⊞ split (-1) = (2,1)`; equal as
-- differences, distinct as pairs). That is exactly the Grothendieck quotient,
-- and stating it at `≈D` is what keeps every step inside ℕ.
------------------------------------------------------------------------

-- `_⊖_` IS the difference pair (the one place ℤ's sign is introduced).
split-⊖ : (m n : ℕ) → split (m ⊖ n) ≈D (m , n)
split-⊖ m       zero    = refl
split-⊖ zero    (suc n) = refl
split-⊖ (suc m) (suc n) = trans (+-suc _ n) (cong suc (split-⊖ m n))

split-hom : (x y : ℤ) → split (x +ℤ y) ≈D (split x ⊞ split y)
split-hom (+ m)    (+ n)    = refl
split-hom (+ m)    (-suc n) =
  subst (λ z → split (m ⊖ suc n) ≈D (z , suc n))
        (sym (+-identityʳ m)) (split-⊖ m (suc n))
split-hom (-suc m) (+ n)    =
  subst (λ z → split (n ⊖ suc m) ≈D (n , z))
        (sym (+-identityʳ (suc m))) (split-⊖ n (suc m))
split-hom (-suc m) (-suc n) = cong suc (+-suc m n)

------------------------------------------------------------------------
-- 4. THE DETERMINANT, READ IN THIS GAUGE.
--
-- `Algebra.Z.JacobianResidue.constant-part` proves `coeff (mono 0 0 0) detJac
-- ≡ -suc 1` (= −2) over ℤ. Transposed onto the rails, the SAME fact carries no
-- negation: it is a ℕ equation.
------------------------------------------------------------------------

det⁺ det⁻ : ℕ
det⁺ = proj₁ (split (coeff (mono 0 0 0) detJac))
det⁻ = proj₂ (split (coeff (mono 0 0 0) detJac))

-- the rails are (0 , 2): the determinant's −2 sits entirely on the NEGATIVE rail.
det-rails : split (coeff (mono 0 0 0) detJac) ≡ (zero , 2)
det-rails = cong split constant-part

-- ⚑ THE FLAGSHIP. "det Jac F ≡ −2" in the semiring gauge. No `-ℤ_`, no ring,
-- no codec — the negation has been transposed across the equality and what
-- remains is arithmetic in ℕ.
route-C : det⁺ + 2 ≡ det⁻ + 0
route-C = refl

------------------------------------------------------------------------
-- 5. NON-VACUITY.
--
-- `_≈D_` is only a gauge if it DISCRIMINATES; a relation identifying every pair
-- would make §4 vacuous.
------------------------------------------------------------------------

-- the rails are not collapsed: ⟨0,2⟩ and ⟨0,0⟩ are distinguished (0 + 0 ≢ 0 + 2).
D-discriminates : (zero , 2) ≈D (zero , zero) → ⊥
D-discriminates ()

-- and `split` genuinely routes sign to different rails — it is not constant.
split-pos : split (+ 2) ≡ (2 , zero)
split-pos = refl

split-neg : split (-suc 1) ≡ (zero , 2)
split-neg = refl

------------------------------------------------------------------------
-- 6. HONEST SCOPE.
--
-- This is ONE gauge of three (A: negation in the carrier, `Algebra.Z.CommRing`;
-- B: negation transported, `Algebra.Z.JacobianNegCodec`). It does NOT establish
-- their equivalence — that is ⟡jac-neg-cover, whose apex is an `ExpLogCodec ℤ`
-- with each route DERIVED through it, plus the mandatory `trivial-codec`
-- vacuity pole.
--
-- Scope of §4: the CONSTANT coefficient only. `JacobianResidue.residue-vanishes`
-- carries the all-520-monomial statement over ℤ; re-running that whole
-- computation on the rails would need a ℕ-side trivariate polynomial layer,
-- which is NOT built here and is not needed for the gauge.
------------------------------------------------------------------------
