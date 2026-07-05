------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.AsModuleHom
--
-- ⟡Ⓒ.linear (2026-07-05): realizes the retrofit Substrate.Algebra.Module.Hom
-- PROMISED but never delivered — its header says "ModuleHom is the universal
-- 'Linear map' — F₂.Linear and ℚ.Linear both retrofit as ModuleHom instances
-- at Mod6 / Mod7", yet F₂.Linear stood alone (a deliberately vector-scoped API,
-- "to keep the API small"), never connected to the center.
--
-- This bridge WITNESSES the connection without collapsing either side:
-- F₂.Linear IS a ModuleHom over the F₂-vector free module (F2.AsModule's
-- F₂-FreeModule). The transport is DEFINITIONAL — the module's scalar mult ·ₛ
-- reduces to F₂.Vector's *ₛ, and its AbelianGroup + reduces to +ⱽ — so the
-- three fields carry across by projection, both ways (the retrofit is faithful).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.AsModuleHom where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.F2.Linear using (Linear)
open import Substrate.Algebra.F2.AsModule using (F₂-FreeModule)
open import Substrate.Algebra.Module.Hom using (ModuleHom)

module L = Linear
module H = ModuleHom

-- Forward: every F₂-linear map is a ModuleHom over the F₂-vector free module.
Linear→ModuleHom : ∀ {n m} → Linear n m → ModuleHom (F₂-FreeModule n) (F₂-FreeModule m)
Linear→ModuleHom f = record
  { apply            = L.apply f
  ; preserves-+      = L.preserves-+ f
  ; preserves-scalar = L.preserves-*ₛ f
  }

-- Reverse: and every such ModuleHom is an F₂-linear map (the retrofit is faithful).
ModuleHom→Linear : ∀ {n m} → ModuleHom (F₂-FreeModule n) (F₂-FreeModule m) → Linear n m
ModuleHom→Linear h = record
  { apply        = H.apply h
  ; preserves-+  = H.preserves-+ h
  ; preserves-*ₛ = H.preserves-scalar h
  }
