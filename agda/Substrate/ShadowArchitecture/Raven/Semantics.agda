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

open import Substrate.ShadowArchitecture.Raven.Semantics.InterpretStanza public
open import Substrate.ShadowArchitecture.Raven.Semantics.Cotypes          public
open import Substrate.ShadowArchitecture.Raven.Semantics.L7Population     public
open import Substrate.ShadowArchitecture.Raven.Semantics.Steps            public
open import Substrate.ShadowArchitecture.Raven.Semantics.FullChain        public
open import Substrate.ShadowArchitecture.Raven.Semantics.L7Summary        public
