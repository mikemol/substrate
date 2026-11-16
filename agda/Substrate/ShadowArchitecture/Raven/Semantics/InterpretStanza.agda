------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.InterpretStanza
--
-- interpret-stanza : Stanza → Cotype → Cotype.
-- The terminal-driven Cotype transition rule:
--   añelē      → populate L₇  (introduce the deletion-prohibition marker)
--   awen-taso  → identity      (open phase, no L₇ change)
--   other-attr → identity      (post-lock; L₇ already populated)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.InterpretStanza where

open import Substrate.ShadowArchitecture.FanoLabeling using (L₇)
open import Substrate.ShadowArchitecture.Persistence
  using (Cotype; populate-line)
-- ⚑ `Terminal` is genuinely ambiguous — ⟦ac030497⟧ data {awen-taso, añelē,
-- other-attr} here, vs ⟦59e216d4⟧ record {feeds-nothing} in Lifecycle.Terminal.
-- Specialized at the import so the reader sees which shape.
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (Stanza; añelē; awen-taso; other-attr; stanza-terminal)
  renaming (Terminal-Raven to Terminal-Raven)

interpret-stanza : Stanza → Cotype → Cotype
interpret-stanza s c = act (stanza-terminal s) c
  where
    act : Terminal-Raven → Cotype → Cotype
    act añelē      c = populate-line L₇ c
    act awen-taso  c = c
    act other-attr c = c
