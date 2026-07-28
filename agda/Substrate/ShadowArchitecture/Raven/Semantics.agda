------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics
--
-- The semantic interpretation of the Raven artifact as a sequence of
-- monotonic state-changes on Persistence.Cotype.
--
-- Decomposed: each "indexed sequence" (cotypes / L₇-populations /
-- adjacent steps) gets its own submodule, plus standalone modules for
-- the interpretation function, the full chain closure, and the phase-
-- transition summary.
--
--   Semantics.InterpretStanza  — Stanza → Cotype → Cotype rule
--   Semantics.Cotypes          — c0..c18 snapshot sequence
--   Semantics.L7Population     — L₇ population status at each cₙ
--   Semantics.Steps            — adjacent ⊑-monotonicity steps
--   Semantics.FullChain        — c0 ⊑ c18 chain closure
--   Semantics.L7Summary        — pre/post-lockup conjunction theorem
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics where

open import Substrate.ShadowArchitecture.Raven.Semantics.InterpretStanza
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes
open import Substrate.ShadowArchitecture.Raven.Semantics.L7Population
open import Substrate.ShadowArchitecture.Raven.Semantics.Steps
open import Substrate.ShadowArchitecture.Raven.Semantics.FullChain
open import Substrate.ShadowArchitecture.Raven.Semantics.L7Summary