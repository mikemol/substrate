------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII
--
-- Meta-theorem (a): every stanza in I..VII is in the open phase.
-- Uses an inject Fin 7 → Fin 18 to address the pre-VIII slice.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.ShadowArchitecture.Raven.Poem using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (open-phase)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
  using (history-phase-at)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase

private
  inject-7-to-18 : Fin 7 → Fin 18
  inject-7-to-18 zero                                       = s1
  inject-7-to-18 (suc zero)                                 = s2
  inject-7-to-18 (suc (suc zero))                           = s3
  inject-7-to-18 (suc (suc (suc zero)))                     = s4
  inject-7-to-18 (suc (suc (suc (suc zero))))               = s5
  inject-7-to-18 (suc (suc (suc (suc (suc zero)))))         = s6
  inject-7-to-18 (suc (suc (suc (suc (suc (suc zero))))))   = s7

open-on-pre-VIII : ∀ (i : Fin 7) → history-phase-at raven (inject-7-to-18 i) ≡ open-phase
open-on-pre-VIII zero                                       = stanza-I-phase
open-on-pre-VIII (suc zero)                                 = stanza-II-phase
open-on-pre-VIII (suc (suc zero))                           = stanza-III-phase
open-on-pre-VIII (suc (suc (suc zero)))                     = stanza-IV-phase
open-on-pre-VIII (suc (suc (suc (suc zero))))               = stanza-V-phase
open-on-pre-VIII (suc (suc (suc (suc (suc zero)))))         = stanza-VI-phase
open-on-pre-VIII (suc (suc (suc (suc (suc (suc zero))))))   = stanza-VII-phase
