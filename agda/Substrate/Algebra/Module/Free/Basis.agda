------------------------------------------------------------------------
-- Substrate.Algebra.Module.Free.Basis
--
-- Mod5 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- The basis embedding for FreeCarrier A n:
--
--   free-basis : (R : Ring A) → Fin n → FreeCarrier A n
--   free-basis R i = e_i = (0,…,1,…,0) with 1 at position i
--
-- + the universal-property record:
--
--   given a Module R N and an image map Fin n → N, the unique
--   ModuleHom FreeModule(R, n) → N extends along the basis.
--
-- This is the abstract source of the substrate's
-- `linear-from-images` discipline at every R: FreeLinearization (F₂)
-- and FreeLinearizationR (parametric) are special cases.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Free.Basis where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.Monoid using (Monoid; ε)
open import Substrate.Algebra.Semiring using (+-monoid; *-monoid)
open import Substrate.Algebra.Ring using (Ring; semiring)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Hom using (ModuleHom; apply)
open import Substrate.Algebra.Module.Free using (FreeCarrier)

------------------------------------------------------------------------
-- 1. The basis-vector constructor.
--
-- basis-vec zeroA oneA i = the i-th canonical basis vector over the
-- carrier A: 1 at slot i, 0 elsewhere. Substrate-native; mirrors
-- Substrate.Algebra.F2.Vector's `basis` shape but parametric in
-- (zeroA, oneA).
------------------------------------------------------------------------

basis-vec :
  {A : Set} (zeroA oneA : A) {n : ℕ} →
  Fin n → FreeCarrier A n
basis-vec zeroA oneA {ℕ.suc m} zero    = oneA  ∷ replicate m zeroA
basis-vec zeroA oneA {ℕ.suc m} (suc i) = zeroA ∷ basis-vec zeroA oneA i

------------------------------------------------------------------------
-- 2. The ring-parametric basis.
--
-- free-basis R i = basis-vec (0_R) (1_R) i. The canonical basis of
-- FreeCarrier A n viewed as an R-module: extracts 0 and 1 from R
-- via field-accessor projection.
------------------------------------------------------------------------

free-basis :
  {A : Set} (R : Ring A) {n : ℕ} →
  Fin n → FreeCarrier A n
free-basis R = basis-vec (ε (+-monoid (semiring R)))
                         (ε (*-monoid (semiring R)))

------------------------------------------------------------------------
-- 3. The universal property of the free module.
--
-- Parametric in:
--   * a Ring R,
--   * dimension n,
--   * a Module-instance for FreeCarrier A n (deferred to Mod6 / Mod7
--     for F₂ / ℚ),
--   * a target Module R N.
--
-- A FreeBasisUniversal record bundles:
--   * images : Fin n → N (where each basis vector maps)
--   * extension : ModuleHom Free → Target
--   * extension-on-basis : extension agrees with images on free-basis
--   * uniqueness : any other extension agreeing on the basis is
--     pointwise equal on all vectors.
--
-- This IS the FreeLinearization universal property at the
-- Module-tower level — Mod9 retrofits FreeLinearizationR through
-- this record.
------------------------------------------------------------------------

record FreeBasisUniversal
  {A : Set} (R : Ring A) (n : ℕ)
  (Free-Mod : Module R (FreeCarrier A n))
  {N : Set} (Target-Mod : Module R N)
  : Set where
  field
    images :
      Fin n → N
    extension :
      ModuleHom Free-Mod Target-Mod
    extension-on-basis :
      (i : Fin n) → apply extension (free-basis R i) ≡ images i
    uniqueness :
      (other : ModuleHom Free-Mod Target-Mod) →
      ((i : Fin n) → apply other (free-basis R i) ≡ images i) →
      (v : FreeCarrier A n) →
      apply extension v ≡ apply other v

open FreeBasisUniversal public

------------------------------------------------------------------------
-- 4. Capstone for Mod5.
--
-- Basis embedding (basis-vec, free-basis) + FreeBasisUniversal
-- record landed. Mod6/Mod7 supply the per-R Module instance +
-- discharge the universal-property record. Mod8 supplies the
-- generic linear-extensionality theorem; Mod9 retrofits
-- FreeLinearizationR through this record.
------------------------------------------------------------------------
