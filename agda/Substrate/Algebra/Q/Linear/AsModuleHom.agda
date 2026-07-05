------------------------------------------------------------------------
-- Substrate.Algebra.Q.Linear.AsModuleHom
--
-- ⟡Ⓒ.linear (2026-07-05): the ℚ half of the Module.Hom retrofit its header
-- promised ("F₂.Linear and ℚ.Linear both retrofit as ModuleHom instances at
-- Mod6 / Mod7"). ℚ.Linear stood alone; this bridge WITNESSES that it IS a
-- ModuleHom over the ℚ-vector free module (Q.AsModule.Lifters.ℚ-FreeModule),
-- parametric in a ℚ-Field-Obligation `o` (the Q-arc's deferred per-arithmetic
-- obligation — the transport needs the PARAMETER, not a discharged instance).
--
-- As on the F₂ side, the transport is DEFINITIONAL (·ₛ reduces to *ℚₛ, the
-- AbelianGroup + to +ℚⱽ), so the three fields carry across both ways.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.Linear.AsModuleHom where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Q.Linear using (Linearℚ)
open import Substrate.Algebra.Q.AsField using (ℚ-Field-Obligation)
open import Substrate.Algebra.Q.AsModule using (module Lifters)
open import Substrate.Algebra.Module.Hom using (ModuleHom)

module L = Linearℚ
module H = ModuleHom

module _ (o : ℚ-Field-Obligation) where
  open Lifters o using (ℚ-FreeModule)

  -- Forward: every ℚ-linear map is a ModuleHom over the ℚ-vector free module.
  Linearℚ→ModuleHom : ∀ {n m} → Linearℚ n m → ModuleHom (ℚ-FreeModule n) (ℚ-FreeModule m)
  Linearℚ→ModuleHom f = record
    { apply            = L.apply f
    ; preserves-+      = L.preserves-+ f
    ; preserves-scalar = L.preserves-*ₛ f
    }

  -- Reverse: and every such ModuleHom is a ℚ-linear map (the retrofit is faithful).
  ModuleHom→Linearℚ : ∀ {n m} → ModuleHom (ℚ-FreeModule n) (ℚ-FreeModule m) → Linearℚ n m
  ModuleHom→Linearℚ h = record
    { apply        = H.apply h
    ; preserves-+  = H.preserves-+ h
    ; preserves-*ₛ = H.preserves-scalar h
    }
