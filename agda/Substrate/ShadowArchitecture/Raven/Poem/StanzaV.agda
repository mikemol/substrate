------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaV
--
-- Stanza V: deep into the darkness peering.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaV where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-V : Stanza
stanza-V = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody se ∷ lopen la ∷ [] )
