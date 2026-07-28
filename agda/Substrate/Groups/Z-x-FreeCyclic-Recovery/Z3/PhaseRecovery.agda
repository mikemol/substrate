------------------------------------------------------------------------
-- …Recovery.Z3.PhaseRecovery — phase-project ∘ embed ≡ id (the section).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.PhaseRecovery where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjW
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃B
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z3.Embed using (embed-Z₃)
projcap-Z₃ = PhaseProjW.cap 2



import Substrate.Groups.Coxeter.PhaseProjectionFromCapability projcap-Z₃ as Z₃-Proj
Z₃-phase-recovery :
  (w : Word Z₃B.Gen) → Z₃-Proj.phase-project (embed-Z₃ w) ≡ w
Z₃-phase-recovery w = refl
