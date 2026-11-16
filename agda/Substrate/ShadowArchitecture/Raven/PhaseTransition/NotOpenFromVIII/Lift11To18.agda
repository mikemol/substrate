------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.Lift11To18
--
-- Defines: lift-11-to-18
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.Lift11To18 where

open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Literals
open import Substrate.Foundation.Negation.Not
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.StanzaIndices
open import Substrate.Foundation.Eq
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.NotOpenFromVIII.Private


lift-11-to-18 : Fin 11 → Fin 18
lift-11-to-18 zero                                                                    = s8
lift-11-to-18 ₁                                                              = s9
lift-11-to-18 ₂                                                        = s10
lift-11-to-18 ₃                                                  = s11
lift-11-to-18 ₄                                            = s12
lift-11-to-18 ₅                                      = s13
lift-11-to-18 ₆                                = s14
lift-11-to-18 ₇                          = s15
lift-11-to-18 ₈                    = s16
lift-11-to-18 ₉              = s17
lift-11-to-18 ₁₀        = s18
