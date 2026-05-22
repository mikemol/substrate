------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé
--
-- prior-añelē? : Vec Stanza n → Fin n → Bool.
-- "Did any stanza strictly BEFORE index i have añelē as terminal?"
-- Recurse on the index: at zero, no prior; at (suc i) on (s ∷ rest),
-- check the head OR recurse on the tail with i.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.PriorAñelé where

open import Substrate.Foundation.Bool using (Bool; false; _∨_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar using (Stanza)
open import Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
  using (is-añelē-terminal)

prior-añelē? : ∀ {n} → Vec Stanza n → Fin n → Bool
prior-añelē? (s ∷ _)  zero    = false
prior-añelē? (s ∷ ss) (suc i) = is-añelē-terminal s ∨ prior-añelē? ss i
