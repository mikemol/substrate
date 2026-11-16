------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal
--
-- is-añelē-terminal : Stanza → Bool.
-- True iff a stanza's terminal is `añelē`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.PhaseTransition.IsAñeléTerminal where

open import Substrate.Foundation.Bool.Bool
-- ⚑ `Terminal` is genuinely ambiguous — ⟦ac030497⟧ data {awen-taso, añelē,
-- other-attr} here, vs ⟦59e216d4⟧ record {feeds-nothing} in Lifecycle.Terminal.
-- Specialized at the import so the reader sees which shape.
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (Stanza; añelē; awen-taso; other-attr; stanza-terminal)
  renaming (Terminal-Raven to Terminal-Raven)

is-añelē-terminal : Stanza → Bool
is-añelē-terminal s = check (stanza-terminal s)
  where
    check : Terminal-Raven → Bool
    check añelē      = true
    check awen-taso  = false
    check other-attr = false
