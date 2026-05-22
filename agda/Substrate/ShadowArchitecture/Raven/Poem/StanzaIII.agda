------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaIII
--
-- Stanza III: silken sad uncertain rustling.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaIII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-III : Stanza
stanza-III = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody ñi ∷ lbody la ∷ lbody la ∷ lopen pa ∷ [] )
