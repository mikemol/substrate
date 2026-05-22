------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaII
--
-- Stanza II: midnight bleak.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-II : Stanza
stanza-II = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody la ∷ lopen pa ∷ [] )
