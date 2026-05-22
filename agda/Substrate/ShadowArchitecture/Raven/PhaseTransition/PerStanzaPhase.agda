------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase
--
-- The 18 per-stanza phase facts. Each `history-phase-at raven sₖ`
-- reduces by computation, so each closes by `refl`.
--
-- Pattern:
--   I-VII   →  open-phase
--   VIII    →  locked-now  (first lockup — the ★ phase transition)
--   IX      →  post-lock   (Raven sitting; añelē in body)
--   X       →  locked-now  (añelē terminal repeated)
--   XI, XII →  post-lock   (body references añelē)
--   XIII-XVIII → locked-now (terminal añelē repeated)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.ShadowArchitecture.Raven.Poem using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (HistoryPhase; open-phase; locked-now; post-lock)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
  using (history-phase-at)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices

stanza-I-phase    : history-phase-at raven s1  ≡ open-phase
stanza-I-phase    = refl
stanza-II-phase   : history-phase-at raven s2  ≡ open-phase
stanza-II-phase   = refl
stanza-III-phase  : history-phase-at raven s3  ≡ open-phase
stanza-III-phase  = refl
stanza-IV-phase   : history-phase-at raven s4  ≡ open-phase
stanza-IV-phase   = refl
stanza-V-phase    : history-phase-at raven s5  ≡ open-phase
stanza-V-phase    = refl
stanza-VI-phase   : history-phase-at raven s6  ≡ open-phase
stanza-VI-phase   = refl
stanza-VII-phase  : history-phase-at raven s7  ≡ open-phase
stanza-VII-phase  = refl

stanza-VIII-phase : history-phase-at raven s8  ≡ locked-now
stanza-VIII-phase = refl

stanza-IX-phase   : history-phase-at raven s9  ≡ post-lock
stanza-IX-phase   = refl

stanza-X-phase    : history-phase-at raven s10 ≡ locked-now
stanza-X-phase    = refl

stanza-XI-phase   : history-phase-at raven s11 ≡ post-lock
stanza-XI-phase   = refl
stanza-XII-phase  : history-phase-at raven s12 ≡ post-lock
stanza-XII-phase  = refl

stanza-XIII-phase  : history-phase-at raven s13 ≡ locked-now
stanza-XIII-phase  = refl
stanza-XIV-phase   : history-phase-at raven s14 ≡ locked-now
stanza-XIV-phase   = refl
stanza-XV-phase    : history-phase-at raven s15 ≡ locked-now
stanza-XV-phase    = refl
stanza-XVI-phase   : history-phase-at raven s16 ≡ locked-now
stanza-XVI-phase   = refl
stanza-XVII-phase  : history-phase-at raven s17 ≡ locked-now
stanza-XVII-phase  = refl
stanza-XVIII-phase : history-phase-at raven s18 ≡ locked-now
stanza-XVIII-phase = refl
