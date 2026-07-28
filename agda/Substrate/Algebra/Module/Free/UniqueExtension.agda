------------------------------------------------------------------------
-- Substrate.Algebra.Module.Free.UniqueExtension
--
-- Mod8 of the Module-over-Ring tower per [scratch/m_mod_arc_plan.md].
--
-- The generic linear-extensionality theorem at the
-- Module-over-Ring level:
--
--   ∀ R-Mod (Free-Mod : Module R (FreeCarrier A n))
--     (Target-Mod : Module R N)
--     (f g : ModuleHom Free-Mod Target-Mod) →
--   (∀ i → apply f (free-basis R i) ≡ apply g (free-basis R i)) →
--   ∀ v → apply f v ≡ apply g v
--
-- ─────────────────────────────────────────────────────────────────
--
-- This IS the lemma deferred at FLQ7 / TPQ7 (ℚ-linear-extensionality)
-- and at every per-R linear-map call site. The substrate-honest
-- packaging:
--
--   1. The theorem statement is named here.
--   2. A `BasisDecomposition` record names the structural witness
--      (every vector decomposes as a sum of scaled basis vectors).
--   3. The generic theorem is THEN extensible to any Module that
--      supplies a BasisDecomposition (per-R discharge: F₂'s
--      basis-decomp is in F2.Vector.Universal; ℚ's discharge is
--      future arc work).
--
-- The substrate's #6 categorical primitive (FreeLinearization) at
-- the Module-tower level: FreeBasisUniversal's `uniqueness` field IS
-- this extensionality, named.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Module.Free.UniqueExtension where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans)

open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.Module using (Module)
open import Substrate.Algebra.Module.Hom using (ModuleHom; apply)
open import Substrate.Algebra.Module.Free using (FreeCarrier)
open import Substrate.Algebra.Module.Free.Basis
  using (free-basis; FreeBasisUniversal; extension; uniqueness;
         extension-on-basis; images)

------------------------------------------------------------------------
-- 1. The generic free-module-extensionality theorem statement.
------------------------------------------------------------------------

FreeModuleExtensionality :
  {A : Set} (R : Ring A) (n : ℕ)
  (Free-Mod : Module R (FreeCarrier A n))
  {N : Set} (Target-Mod : Module R N)
  → Set
FreeModuleExtensionality R n Free-Mod Target-Mod =
  (f g : ModuleHom Free-Mod Target-Mod) →
  ((i : Fin n) → apply f (free-basis R i) ≡ apply g (free-basis R i)) →
  (v : FreeCarrier _ n) → apply f v ≡ apply g v

------------------------------------------------------------------------
-- 2. Discharge from a parametric FreeBasisUniversal builder.
--
-- A builder that, given any image map `imgs : Fin n → N`, produces
-- a FreeBasisUniversal witness whose `images` field IS `imgs`.
-- The two-sided uniqueness on f and g then gives extensionality.
------------------------------------------------------------------------

record FreeBasisUniversalAt
  {A : Set} (R : Ring A) (n : ℕ)
  (Free-Mod : Module R (FreeCarrier A n))
  {N : Set} (Target-Mod : Module R N)
  (imgs : Fin n → N)
  : Set where
  field
    witness : FreeBasisUniversal R n Free-Mod {N} Target-Mod
    images-≡ : (i : Fin n) → images witness i ≡ imgs i

open FreeBasisUniversalAt public

extensionality-from-universal :
  {A : Set} (R : Ring A) (n : ℕ)
  (Free-Mod : Module R (FreeCarrier A n))
  {N : Set} (Target-Mod : Module R N) →
  ((imgs : Fin n → N) →
   FreeBasisUniversalAt R n Free-Mod {N} Target-Mod imgs) →
  FreeModuleExtensionality R n Free-Mod Target-Mod
extensionality-from-universal R n Free-Mod {N} Target-Mod build f g f≈g v =
  let imgs   : Fin n → N
      imgs i = apply g (free-basis R i)
      U      = build imgs
      U-W    = witness U
      U-eq   = images-≡ U
      -- apply g (free-basis R i) ≡ images U-W i
      g-on-basis : (i : Fin n) → apply g (free-basis R i) ≡ images U-W i
      g-on-basis i = sym (U-eq i)
      f-on-basis : (i : Fin n) → apply f (free-basis R i) ≡ images U-W i
      f-on-basis i = trans (f≈g i) (sym (U-eq i))
      uniq-f = uniqueness U-W f f-on-basis v
      uniq-g = uniqueness U-W g g-on-basis v
  in trans (sym uniq-f) uniq-g

------------------------------------------------------------------------
-- 3. Capstone for Mod8.
--
-- The free-module-extensionality theorem named generically + the
-- universal-property discharge path. Per-R bridges (F₂ via
-- F2.Vector.Universal supplying the FreeBasisUniversalAt builder;
-- ℚ via future per-arithmetic work) feed
-- `extensionality-from-universal`. Mod9 retrofits FreeLinearizationR
-- through this entry point.
------------------------------------------------------------------------
