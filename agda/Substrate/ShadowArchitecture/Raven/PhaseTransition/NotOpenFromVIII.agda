------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII
--
-- Meta-theorem (b): no stanza from VIII onward is in the open phase.
-- Each case discharges by () because `history-phase-at raven sₖ`
-- reduces to either locked-now or post-lock (both ≢ open-phase).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Literals using (₁₀; ₂; ₃; ₄; ₅; ₆; ₇; ₈; ₉)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.ShadowArchitecture.Raven.Poem using (raven)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
  using (open-phase)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
  using (history-phase-at)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices

private
  -- Indices 0..10 correspond to stanzas VIII..XVIII.
  lift-11-to-18 : Fin 11 → Fin 18
  lift-11-to-18 zero                                                                    = s8
  lift-11-to-18 (suc zero)                                                              = s9
  lift-11-to-18 ₂                                                        = s10
  lift-11-to-18 ₃                                                  = s11
  lift-11-to-18 ₄                                            = s12
  lift-11-to-18 ₅                                      = s13
  lift-11-to-18 ₆                                = s14
  lift-11-to-18 ₇                          = s15
  lift-11-to-18 ₈                    = s16
  lift-11-to-18 ₉              = s17
  lift-11-to-18 ₁₀        = s18

not-open-from-VIII :
  ∀ (i : Fin 11) → ¬ (history-phase-at raven (lift-11-to-18 i) ≡ open-phase)
not-open-from-VIII zero                                                              ()
not-open-from-VIII (suc zero)                                                        ()
not-open-from-VIII ₂                                                  ()
not-open-from-VIII ₃                                            ()
not-open-from-VIII ₄                                      ()
not-open-from-VIII ₅                                ()
not-open-from-VIII ₆                          ()
not-open-from-VIII ₇                    ()
not-open-from-VIII ₈              ()
not-open-from-VIII ₉        ()
not-open-from-VIII ₁₀  ()
