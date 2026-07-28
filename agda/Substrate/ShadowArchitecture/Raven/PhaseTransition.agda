------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition
--
-- The genuinely history-aware phase classification of the Raven's
-- stanzas. Decomposed file-per-section:
--
--   PhaseTransition.HistoryPhase       — open/locked-now/post-lock
--   PhaseTransition.IsAñeléTerminal    — terminal-añelē test
--   PhaseTransition.PriorAñelé         — prior-añelē? predicate
--   PhaseTransition.HistoryPhaseAt     — phase function
--   PhaseTransition.StanzaIndices      — s1..s18 Fin 18 indices
--   PhaseTransition.PerStanzaPhase     — 18 per-stanza phase facts
--   PhaseTransition.OpenOnPreVIII      — meta (a): I..VII are open
--   PhaseTransition.NotOpenFromVIII    — meta (b): VIII..XVIII are not open
--   PhaseTransition.FirstLockupAtVIII  — meta (c): VIII is the first lockup
--   PhaseTransition.Monotone           — historical-truth monotonicity
--
-- The phase-transition theorem: the first locked-now stanza is at
-- index 7 (= stanza VIII). The open phase is exactly stanzas I-VII;
-- from VIII onward, no stanza is in the open phase.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition where

open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.FirstLockupAtVIII
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.Monotone