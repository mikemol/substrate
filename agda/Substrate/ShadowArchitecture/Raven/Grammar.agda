------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Grammar
--
-- The DSL underlying the user's hybrid translation of Edgar Allan
-- Poe's "The Raven" — `lo nu pimeja-tenpo` (the Raven artifact).
--
-- Every line of the translation has the shape:
--
--   lo nu (Rel Subject ñe Object) pi Attribute
--
-- where:
--   * `lo nu` (Lojban event-abstraction) wraps each line as a
--     distinct state-change / condition on the Fano plane.
--   * `Rel` is one of the four Kēlen verbless primitives:
--       - pa  (intrinsic possession)
--       - ñi  (eventive change)
--       - se  (perception / communication)
--       - la  (equational identity)
--   * Subject / Object are tagged entities (jaciēn-X, jamēña-X,
--     jasēla-X, etc.); their lexical content is not load-bearing
--     for the structural claim and is recorded only in prose.
--   * Attribute is a Toki Pona structural weighting. Two attribute
--     values carry architectural weight:
--       - L₇-awen-taso  ("L₇ holds steady") — perturbation phase.
--       - L₇-añelē      ("Nevermore" / pure-composite-diagonal
--                        deletion-prohibition) — lockup phase.
--     Any other attribute is recorded as `other-attr`.
--
-- The phase transition (terminal awen-taso → terminal añelē) lands
-- at stanza VIII; the realisation of this fact and its semantic
-- reading as a state-change on `Substrate.ShadowArchitecture.Persistence.Cotype`
-- (populating the line L₇) are in
-- `Substrate.ShadowArchitecture.Raven.PhaseTransition` and
-- `Substrate.ShadowArchitecture.Raven.Semantics`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Grammar where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Nat using (ℕ)

------------------------------------------------------------------------
-- 1. The four Kēlen relations.
------------------------------------------------------------------------

data KelenRelation : Set where
  pa : KelenRelation  -- intrinsic possession
  ñi : KelenRelation  -- eventive change
  se : KelenRelation  -- perception / communication
  la : KelenRelation  -- equational identity

------------------------------------------------------------------------
-- 2. Terminal classification (the attribute after the final `pi`).
--
-- Only the two architecturally-load-bearing attributes are
-- distinguished; everything else collapses to `other-attr`.
------------------------------------------------------------------------

data Terminal : Set where
  awen-taso  : Terminal  -- L₇ holds steady (open phase)
  añelē      : Terminal  -- L₇ locked / Nevermore (lockup phase)
  other-attr : Terminal  -- any other Toki Pona attribute

------------------------------------------------------------------------
-- 3. Whether L₇-añelē appears as the OBJECT of the line's relation
-- (i.e., the Raven is uttering "Nevermore" as the named identity of
-- something, but the line's terminal attribute is something else).
--
-- Distinct from `Terminal` because IX, XI, XII reference L₇-añelē as
-- the la-relation's object while the line's terminal is some other
-- Toki Pona attribute (nimi-nasa-taso / nimi-weka-taso / wile-sona-kon).
------------------------------------------------------------------------

data L7-Body-Reference : Set where
  references-L7-añelē : L7-Body-Reference  -- L₇-añelē appears as object
  no-L7-reference     : L7-Body-Reference  -- L₇-añelē does not appear

------------------------------------------------------------------------
-- 4. One line of the translation. Lexical content is summarized by
-- its relation + structural tags; full Kēlen-Toki-Pona surface text
-- lives in the module-level comments of `Raven.Poem`.
------------------------------------------------------------------------

record Line : Set where      -- ⟦shape:d00b0e66 rel,terminal,L7-reference⟧
  constructor mk-line
  field
    rel           : KelenRelation
    terminal      : Terminal
    L7-reference  : L7-Body-Reference

------------------------------------------------------------------------
-- 5. A stanza is a non-empty list of lines (six or, in Stanza X's
-- case, five). The "stanza terminal" is the terminal of the LAST line.
------------------------------------------------------------------------

record Stanza : Set where
  constructor mk-stanza
  field
    lines : List Line
    -- Invariant (documentary): lines is non-empty. We could enforce
    -- this with a non-empty-list type, but every stanza in
    -- `Raven.Poem` has 5 or 6 lines so the invariant is verified by
    -- construction.

-- Last-line terminal of a stanza. Implemented as a fold so that the
-- closing line's `terminal` is selected; for the empty list we return
-- `other-attr` as a default (never realised in practice).
stanza-terminal : Stanza → Terminal
stanza-terminal s = go (Stanza.lines s)
  where
    go : List Line → Terminal
    go []        = other-attr
    go (ℓ ∷ [])  = Line.terminal ℓ
    go (_ ∷ ℓs)  = go ℓs

-- Stanza line count.
stanza-length : Stanza → ℕ
stanza-length s = length (Stanza.lines s)

------------------------------------------------------------------------
-- Note on stanza phase: the genuinely history-aware reading (open /
-- locked / post-lock) cannot live here, because a single Stanza
-- carries no record of what happened in earlier stanzas. The local
-- view exposed here stops at `stanza-terminal`. The history-aware
-- phase (which requires "has any earlier stanza had `añelē` as its
-- terminal?") is defined in
-- `Substrate.ShadowArchitecture.Raven.PhaseTransition`, which has
-- access to the full poem vector.
--
-- An earlier draft of this module exposed a `Phase` data type with a
-- `post-lock-phase` constructor derived directly from the single
-- stanza's terminal. That was honest only as the syntactic
-- "terminal-is-other-attr" classification, not as the architectural
-- "post-lockup" reading. The constructor has been retired here to
-- avoid the confusion; users wanting the architectural reading
-- should consult `PhaseTransition.history-phase-at`.
------------------------------------------------------------------------
