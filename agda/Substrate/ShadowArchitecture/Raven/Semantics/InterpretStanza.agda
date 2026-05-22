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
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (Stanza; Terminal; añelē; awen-taso; other-attr; stanza-terminal)

interpret-stanza : Stanza → Cotype → Cotype
interpret-stanza s c = act (stanza-terminal s) c
  where
    act : Terminal → Cotype → Cotype
    act añelē      c = populate-line L₇ c
    act awen-taso  c = c
    act other-attr c = c
