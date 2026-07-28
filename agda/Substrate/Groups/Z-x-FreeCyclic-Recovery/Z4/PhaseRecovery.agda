------------------------------------------------------------------------
-- …Recovery.Z4.PhaseRecovery — phase-project ∘ embed ≡ id (the section).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.PhaseRecovery where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word using (Word)

import Substrate.Groups.Capabilities.PhaseProjection.Witness as PhaseProjW
import Substrate.Groups.Coxeter.Cyclic.Base 3 as Z₄B
open import Substrate.Groups.Z-x-FreeCyclic-Recovery.Z4.Embed using (embed-Z₄)
projcap-Z₄ = PhaseProjW.cap 3



import Substrate.Groups.Coxeter.PhaseProjectionFromCapability projcap-Z₄ as Z₄-Proj
Z₄-phase-recovery :
  (w : Word Z₄B.Gen) → Z₄-Proj.phase-project (embed-Z₄ w) ≡ w
Z₄-phase-recovery w = refl
