{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.PermMatrixDet — ⟡leibniz-det-of-perm-matrix.
--
-- THE PERMUTATION MATRIX, and det (P σ) = sign σ.
--
-- With the Leibniz determinant now a genuine term (`LeibnizDet.det`,
-- ⟡leibniz-det-sum), this module defines the permutation matrix `Pmat σ` and
-- exhibits the classical identity
--
--     det (P σ)  =  sign σ        (as ±1, i.e. `signVal (signF σ) 1A`)
--
-- CONCRETELY, by `refl`, at the smallest nontrivial cases (n = 2, 3).
--
-- ⚑ THIS RETIRES A STANDING BOUNDARY. `OrientationRigCatPermSignChirality:8-13`
-- states that `det(P_σ) = sign(σ)` is "a NAME-COINCIDENCE here: the substrate
-- has NO permutation matrix and NO Leibniz determinant… We do NOT build a fake
-- permutation determinant." Both halves of the premise are now false: the
-- determinant IS built (LeibnizDet, the genuine Leibniz sum — not a fake), and
-- `Pmat` IS a permutation matrix. The identity is verified here at n = 2, 3;
-- the GENERAL ∀-n theorem is now also BUILT, so it is no longer a "coincidence"
-- — it is a checked identity at every arity.
--
-- ⚑ THE GENERAL THEOREM ⟡leibniz-det-perm-general — det (P σ) ≡ signVal (signF σ)
-- 1A for ALL σ — is BUILT in `WitnessTower.LeibnizDetPerm` (`DetPerm.det-P`), via
--   (1) `LeibnizMonomialDirect.mono≡dprod` — the cofactor fold equals the direct
--       indexed product (`remQuot-combine`, no perm-matrix-specific lemma);
--   (2) `indicator-0`/`indicator-1` — `Πⱼ (P σ)[j, τ j]` is 1A iff τ = σ (else a
--       0A factor annihilates via the semiring's zero-absorb);
--   (3) `sumF-onehot` — the one-hot `sumF` collapse over the Sₙ enumeration
--       (`enumerate-surjective`/`-injective`).
-- Plus the tower ◂-step `DetPerm.det-P-◂` (via `insertion-parity-B`): det∘P∘decode
-- is a parity character over the ordering tower. `Pmat` here is the concrete
-- nested-`with` refl witness at n = 2, 3; `LeibnizDetPerm.Pmat` is the δ-based
-- ∀-n form — the same permutation matrix, two presentations.
--
-- Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.WitnessTower.PermMatrixDet where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
import Substrate.WitnessTower.LeibnizDet as LD

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring; mul-sign-computes)

------------------------------------------------------------------------
-- 1. THE PERMUTATION MATRIX, FLAT: (P σ)[i, j] = 1 iff j ≡ σ i, else 0.
--
-- Row i has its single 1 in column σ i, so `Πⱼ (P σ)[j, τ j]` is 1 exactly
-- when τ = σ — which is what makes the determinant sum collapse to sign σ.
------------------------------------------------------------------------

open LD.Det ℤ ℤ-semiring using (Mat)
open LD.Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det; signVal)

Pmat : {n : ℕ} → Perm n → Mat n
Pmat {n} σ k with proj₁ (remQuot {n} n k) | proj₂ (remQuot {n} n k)
... | i | j with j ≟ lookup σ i
...   | yes _ = + 1
...   | no  _ = + 0

------------------------------------------------------------------------
-- 2. THE IDENTITY det (P σ) ≡ sign σ (as ±1), verified at n = 2, 3 by refl.
------------------------------------------------------------------------

id2 swap2 : Perm 2
id2   = zero ∷ suc zero ∷ []
swap2 = suc zero ∷ zero ∷ []

det-P-id2   : det {2} (Pmat id2)   ≡ signVal (signF id2)   (+ 1)
det-P-id2   = refl
det-P-swap2 : det {2} (Pmat swap2) ≡ signVal (signF swap2) (+ 1)
det-P-swap2 = refl

-- and the right-hand sides genuinely are ±1: identity even (+1), swap odd (−1).
sign-id2-+1   : signVal (signF id2)   (+ 1) ≡ + 1
sign-id2-+1   = refl
sign-swap2-−1 : signVal (signF swap2) (+ 1) ≡ -suc 0
sign-swap2-−1 = refl

id3 tp3 cyc3 : Perm 3
id3  = zero ∷ suc zero ∷ suc (suc zero) ∷ []
tp3  = suc zero ∷ zero ∷ suc (suc zero) ∷ []       -- a transposition (odd)
cyc3 = suc zero ∷ suc (suc zero) ∷ zero ∷ []       -- a 3-cycle (even)

det-P-id3  : det {3} (Pmat id3)  ≡ signVal (signF id3)  (+ 1)
det-P-id3  = refl
det-P-tp3  : det {3} (Pmat tp3)  ≡ signVal (signF tp3)  (+ 1)
det-P-tp3  = refl
det-P-cyc3 : det {3} (Pmat cyc3) ≡ signVal (signF cyc3) (+ 1)
det-P-cyc3 = refl
