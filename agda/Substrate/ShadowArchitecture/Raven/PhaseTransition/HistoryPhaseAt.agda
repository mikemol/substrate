------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
--
-- history-phase-at : Vec Stanza n → Fin n → HistoryPhase.
-- The phase function. Three-way case-split on (this stanza's terminal,
-- prior añelē occurrence?).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt where

open import Substrate.Foundation.Bool using (true; false)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (Vec; lookup)
open import Substrate.ShadowArchitecture.Raven.Grammar using (Stanza)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (HistoryPhase; open-phase; locked-now; post-lock)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
  using (is-añelē-terminal)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
  using (prior-añelē?)

history-phase-at : ∀ {n} → Vec Stanza n → Fin n → HistoryPhase
history-phase-at v i with is-añelē-terminal (lookup v i) | prior-añelē? v i
... | true  | _     = locked-now
... | false | true  = post-lock
... | false | false = open-phase
