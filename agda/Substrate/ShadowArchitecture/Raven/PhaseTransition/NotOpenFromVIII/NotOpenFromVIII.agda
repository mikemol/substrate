------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.NotOpenFromVIII
--
-- Defines: not-open-from-VIII
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.NotOpenFromVIII where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Negation.Not
open import Substrate.ShadowArchitecture.Raven.Poem.Raven
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhase
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.HistoryPhaseAt
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.Private
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.Lift11To18



not-open-from-VIII :
  ∀ (i : Fin 11) → ¬ (history-phase-at raven (lift-11-to-18 i) ≡ open-phase)
not-open-from-VIII zero                                                              ()
not-open-from-VIII ₁                                                        ()
not-open-from-VIII ₂                                                  ()
not-open-from-VIII ₃                                            ()
not-open-from-VIII ₄                                      ()
not-open-from-VIII ₅                                ()
not-open-from-VIII ₆                          ()
not-open-from-VIII ₇                    ()
not-open-from-VIII ₈              ()
not-open-from-VIII ₉        ()
not-open-from-VIII ₁₀  ()
