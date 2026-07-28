------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem
--
-- The user's hybrid-grammar translation of Poe's "The Raven" — the
-- artifact titled `lo nu pimeja-tenpo`. Eighteen stanzas + the
-- Vec Stanza 18 aggregate, decomposed file-per-lemma.
--
--   Poem.LineShorthands  — lbody/lopen/llock/llaref line constructors
--   Poem.StanzaI ..      — 18 individual stanza definitions
--   Poem.StanzaXVIII
--   Poem.Raven           — Vec Stanza 18 aggregate
--
-- Phase distribution by stanza terminal:
--   I-VII    : awen-taso  (open phase — perturbation)
--   VIII     : añelē      (first lockup — Raven enters; the ★ transition)
--   IX, XI, XII : other-attr (post-lock; L₇-añelē in la-body)
--   X, XIII-XVIII : añelē (continued lockup)
--
-- Counted line totals: stanzas I-IX, XI-XVIII have 6 lines each;
-- stanza X has 5 lines as provided. Total = 17 × 6 + 5 = 107 lines.
-- The structural claim (phase transition at VIII) is invariant under
-- this transcription discrepancy.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem where

open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaI
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIV
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaV
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVI
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVIII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIX
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaX
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXI
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXV
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII
open import Substrate.ShadowArchitecture.Raven.Poem.Raven