------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII
--
-- Meta-theorem (a): every stanza in I..VII is in the open phase.
-- Uses an inject Fin 7 → Fin 18 to address the pre-VIII slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅; ₆)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.ShadowArchitecture.Raven.Poem.Raven using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (open-phase)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
  using (history-phase-at)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase

private
  inject-7-to-18 : Fin 7 → Fin 18
  inject-7-to-18 zero                                       = s1
  inject-7-to-18 ₁                                 = s2
  inject-7-to-18 ₂                           = s3
  inject-7-to-18 ₃                     = s4
  inject-7-to-18 ₄               = s5
  inject-7-to-18 ₅         = s6
  inject-7-to-18 ₆   = s7

open-on-pre-VIII : ∀ (i : Fin 7) → history-phase-at raven (inject-7-to-18 i) ≡ open-phase
open-on-pre-VIII zero                                       = stanza-I-phase
open-on-pre-VIII ₁                                 = stanza-II-phase
open-on-pre-VIII ₂                           = stanza-III-phase
open-on-pre-VIII ₃                     = stanza-IV-phase
open-on-pre-VIII ₄               = stanza-V-phase
open-on-pre-VIII ₅         = stanza-VI-phase
open-on-pre-VIII ₆   = stanza-VII-phase
