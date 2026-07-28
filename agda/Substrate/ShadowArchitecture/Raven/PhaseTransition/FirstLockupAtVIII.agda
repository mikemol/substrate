------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.FirstLockupAtVIII
--
-- Meta-theorem (c): stanza VIII is the FIRST lockup —
--   history-phase-at raven s8 ≡ locked-now
--   prior-añelē? raven s8     ≡ false
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.FirstLockupAtVIII where

open import Substrate.Foundation.Bool using (false)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.ShadowArchitecture.Raven.Poem.Raven using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (locked-now)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
  using (history-phase-at)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
  using (prior-añelē?)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase
  using (stanza-VIII-phase)

first-lockup-at-VIII :
    history-phase-at raven s8 ≡ locked-now
  × prior-añelē? raven s8 ≡ false
first-lockup-at-VIII = stanza-VIII-phase , refl
