------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
--
-- Convenience constructors for the four common line shapes in the
-- Raven encoding (body-only, open-terminal, lockup-terminal, body
-- with L₇-añelē reference). Used uniformly by all 18 stanza files.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.LineShorthands where

open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; Terminal; añelē; awen-taso; other-attr;
         L7-Body-Reference; no-L7-reference; references-L7-añelē;
         Line; mk-line)

-- Common shape: terminal `other-attr`, no L₇-body reference.
lbody : KelenRelation → Line
lbody r = mk-line r other-attr no-L7-reference

-- Terminal `awen-taso` (open phase), no L₇-body reference.
lopen : KelenRelation → Line
lopen r = mk-line r awen-taso no-L7-reference

-- Terminal `añelē` (lockup phase), no L₇-body reference.
llock : KelenRelation → Line
llock r = mk-line r añelē no-L7-reference

-- Terminal `other-attr` with L₇-añelē as object in la-body.
llaref : KelenRelation → Line
llaref r = mk-line r other-attr references-L7-añelē
