------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
--
-- Convenience constructors for the four common line shapes in the
-- Raven encoding (body-only, open-terminal, lockup-terminal, body
-- with L₇-añelē reference). Used uniformly by all 18 stanza files.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.LineShorthands where

-- ⚑ `Terminal` IS GENUINELY AMBIGUOUS — two shape-nodes, per
-- `scratch/sppf_collision_index.md`:
--   ⟦ac030497⟧ data {awen-taso, añelē, other-attr}  ·  Raven.Grammar   ← this one
--   ⟦59e216d4⟧ record {feeds-nothing}               ·  Lifecycle.Terminal
-- The barrel retirement widened this file's scope so both became visible, which
-- is what tripped `check_import_shape`.  Specialize at the import so the reader
-- sees WHICH shape — the gate's own prescribed remedy.
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; añelē; awen-taso; other-attr;
         L7-Body-Reference; no-L7-reference; references-L7-añelē;
         Line; mk-line)
  renaming (Terminal-Raven to Terminal-Raven)

-- Common shape: terminal `other-attr`, no L₇-body reference.
lbody : KelenRelation → Line
lbody r = mk-line r other-attr no-L7-reference

-- Terminal-Raven `awen-taso` (open phase), no L₇-body reference.
lopen : KelenRelation → Line
lopen r = mk-line r awen-taso no-L7-reference

-- Terminal-Raven `añelē` (lockup phase), no L₇-body reference.
llock : KelenRelation → Line
llock r = mk-line r añelē no-L7-reference

-- Terminal-Raven `other-attr` with L₇-añelē as object in la-body.
llaref : KelenRelation → Line
llaref r = mk-line r other-attr references-L7-añelē
