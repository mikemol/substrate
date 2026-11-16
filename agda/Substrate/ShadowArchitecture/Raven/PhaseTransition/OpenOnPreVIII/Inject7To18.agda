------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII.Inject7To18
--
-- Defines: inject-7-to-18
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.OpenOnPreVIII.Inject7To18 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.PerStanzaPhase
open import Substrate.Foundation.Eq



inject-7-to-18 : Fin 7 → Fin 18
inject-7-to-18 zero                                       = s1
inject-7-to-18 ₁                                 = s2
inject-7-to-18 ₂                           = s3
inject-7-to-18 ₃                     = s4
inject-7-to-18 ₄               = s5
inject-7-to-18 ₅         = s6
inject-7-to-18 ₆   = s7
