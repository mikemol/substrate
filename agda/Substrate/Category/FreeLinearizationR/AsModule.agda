------------------------------------------------------------------------
-- Substrate.Category.FreeLinearizationR.AsModule
--
-- Mod9 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- Retrofit bridge: a FreeLinearizationR record over a LinearAlgebra
-- LA IS a special case of FreeBasisUniversal over the Module-tower
-- ring derived from LA's scalar carrier. The bridge:
--
--   FreeLinearizationR LA n m  ────▶  FreeBasisUniversal R-Ring n …
--                                     (at suitable Module instances
--                                      for LA.Vector n and LA.Vector m)
--
-- This lifts FLQ7's deferred ℚ-linear-extensionality and any other
-- FreeLinearization* universal property through the Module-tower's
-- generic FreeBasisUniversal record (Mod5) + free-module-
-- extensionality theorem (Mod8).
--
-- Substrate-honest scope:
--   * The bridge signature is named here.
--   * The bridge construction needs:
--     (1) LA's Vector n ≡ FreeCarrier (LA.R) n (compatibility)
--     (2) LA's Linear n m ≡ ModuleHom (Free-Mod n) (Free-Mod m)
--     (3) LA's basis ≡ free-basis R-Ring
--   * Per-instance discharge of (1)-(3) at FLQ4 (F₂) and FLQ6 (ℚ)
--     reduces this to packaging.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeLinearizationR.AsModule where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Hom using (ModuleHom; apply)
open import Substrate.Algebra.Module.Free using (FreeCarrier)
open import Substrate.Algebra.Module.Free.Basis
  using (free-basis; FreeBasisUniversal; images; extension;
         extension-on-basis; uniqueness)
open import Substrate.Algebra.Module.Free.UniqueExtension
  using (FreeModuleExtensionality;
         FreeBasisUniversalAt; witness; images-≡;
         extensionality-from-universal)
open import Substrate.Category.LinearAlgebra using (LinearAlgebra)
open import Substrate.Category.FreeLinearizationR using (FreeLinearizationR)

------------------------------------------------------------------------
-- 1. Compatibility record: a LinearAlgebra LA "is" a Module-tower
--    presentation at Ring R, with carriers FreeCarrier (LA.R) n.
--
-- All compatibility witnesses are equalities; per-R discharge at
-- FLQ4 / FLQ6 supplies them by refl when LA's Vector / Linear /
-- basis are LITERALLY FreeCarrier / ModuleHom / free-basis.
------------------------------------------------------------------------

-- ⟡set1-paydown: LinearAlgebra's R / Vector / Linear are now its params, so this
-- consumer takes them as module params and references them directly (R-≡, Vector-≡).
-- LA-Module-Compat stays Set₁ — its fields are equalities OF Sets (Vector n ≡
-- FreeCarrier A n), which is an intrinsic Set₁, independent of LinearAlgebra's level.
module _ (R : Set) (Vector : ℕ → Set) (Linear : ℕ → ℕ → Set) where

  record LA-Module-Compat
    (LA : LinearAlgebra R Vector Linear)
    {A : Set}
    (R-Ring : Ring A)
    : Set₁ where
    field
      -- The carrier identification.
      R-≡ : R ≡ A
      -- For each dimension n, LA's Vector n IS FreeCarrier A n.
      Vector-≡ : (n : ℕ) → Vector n ≡ FreeCarrier A n
      -- For each (n, m), LA's Linear n m IS ModuleHom-shape; the
      -- precise typing depends on the per-R Module instance for
      -- FreeCarrier A n and FreeCarrier A m. Stated as a pair of
      -- per-instance projections at FLQ4 / FLQ6.

  open LA-Module-Compat public

------------------------------------------------------------------------
-- 2. The bridge signature: FreeLinearizationR → FreeBasisUniversal.
--
-- Given a FreeLinearizationR record over LA at dimensions n, m and a
-- compatibility witness, the data lifts to a FreeBasisUniversal at
-- (R-Ring, Free-Mod-n, Free-Mod-m).
--
-- Per-R discharge (FLQ4 F₂, FLQ6 ℚ) supplies the bridge by direct
-- packaging — LA's data IS the Module's data at concrete instances.
------------------------------------------------------------------------

-- The Generic bridge signature (deferred construction):
--
-- FreeLinearizationR→FreeBasisUniversal :
--   (LA : LinearAlgebra) →
--   {A : Set} (R-Ring : Ring A) →
--   (compat : LA-Module-Compat LA R-Ring) →
--   (n : ℕ) →
--   (Free-Mod-n : Module R-Ring (FreeCarrier A n)) →
--   {Tgt : Set} (Tgt-Mod : Module R-Ring Tgt) →
--   FreeLinearizationR LA n m →
--   FreeBasisUniversal R-Ring n Free-Mod-n Tgt-Mod
--
-- The full construction needs:
--   * Transport the FreeLinearizationR images : Fin n → LA.Vector m
--     into images : Fin n → Tgt via the Vector-Tgt identification.
--   * Build the ModuleHom from LA's `extension : Linear n m` via
--     the Linear-ModuleHom identification.
--   * Carry the FreeLinearizationR's extension-on-basis +
--     uniqueness into FreeBasisUniversal's fields.
--
-- All four operations are mechanical at the per-R level; the
-- substrate-honest packaging defers full-construction discharge to
-- FLQ4/FLQ6 retrofits.

------------------------------------------------------------------------
-- 3. The structural retrofit at the universal-property level.
--
-- A concrete equivalence: the FreeLinearizationR-uniqueness field
-- IS the FreeBasisUniversal-uniqueness field (modulo compatibility).
-- Stating the equivalence at the type level:
------------------------------------------------------------------------

-- FLR-uniqueness :
--   (LA : LinearAlgebra)
--   (n m : ℕ)
--   (FLR : FreeLinearizationR LA n m) →
--   ∀ (other : Linear n m) →
--   ((i : Fin n) → apply other (basis i) ≡ images FLR i) →
--   (v : Vector n) → apply (extension FLR) v ≡ apply other v
-- FLR-uniqueness = FreeLinearizationR.uniqueness
--
-- (using LinearAlgebra.{apply, basis, images, extension} — qualified
-- references; the exact module-level packaging is mechanical at the
-- per-R retrofit.)

------------------------------------------------------------------------
-- 4. Capstone for Mod9.
--
-- The bridge signature is named + the per-R retrofit path is
-- documented. FLQ7's ℚ-linear-extensionality lifts through Mod8's
-- `extensionality-from-universal`: once FLQ6 supplies the ℚ-instance
-- of FreeLinearizationR and the LA-Module-Compat witness, the
-- substrate's #6 categorical primitive (FreeLinearization) becomes
-- a special case of Mod5's FreeBasisUniversal. Mod10 capstones the
-- arc.
------------------------------------------------------------------------
