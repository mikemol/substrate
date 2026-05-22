------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
--
-- is-añelē-terminal : Stanza → Bool.
-- True iff a stanza's terminal is `añelē`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal where

open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (Stanza; Terminal; añelē; awen-taso; other-attr; stanza-terminal)

is-añelē-terminal : Stanza → Bool
is-añelē-terminal s = check (stanza-terminal s)
  where
    check : Terminal → Bool
    check añelē      = true
    check awen-taso  = false
    check other-attr = false
