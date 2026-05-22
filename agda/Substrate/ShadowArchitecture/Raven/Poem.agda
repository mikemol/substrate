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

open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaI        public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaII       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIII      public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIV       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaV        public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVI       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVII      public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVIII     public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIX       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaX        public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXI       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXII      public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII     public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV      public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXV       public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI      public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII     public
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII    public
open import Substrate.ShadowArchitecture.Raven.Poem.Raven          public
