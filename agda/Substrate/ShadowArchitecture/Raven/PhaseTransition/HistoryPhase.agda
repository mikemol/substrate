------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
--
-- HistoryPhase: the genuinely history-aware phase classification.
--   open-phase  — no añelē seen yet AND this stanza isn't añelē.
--   locked-now  — this stanza's terminal IS añelē (lockup happens here).
--   post-lock   — at least one earlier añelē AND this stanza isn't añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase where

data HistoryPhase : Set where
  open-phase  : HistoryPhase
  locked-now  : HistoryPhase
  post-lock   : HistoryPhase
