------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII.OpenOnPreVIII
--
-- Defines: open-on-pre-VIII
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII.OpenOnPreVIII where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.ShadowArchitecture.Raven.Poem.Raven
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII.Inject7To18



open-on-pre-VIII : ∀ (i : Fin 7) → history-phase-at raven (inject-7-to-18 i) ≡ open-phase
open-on-pre-VIII zero                                       = stanza-I-phase
open-on-pre-VIII ₁                                 = stanza-II-phase
open-on-pre-VIII ₂                           = stanza-III-phase
open-on-pre-VIII ₃                     = stanza-IV-phase
open-on-pre-VIII ₄               = stanza-V-phase
open-on-pre-VIII ₅         = stanza-VI-phase
open-on-pre-VIII ₆   = stanza-VII-phase
