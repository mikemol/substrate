------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaIV
--
-- Stanza IV: the visitor at the door.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaIV where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-IV : Stanza
stanza-IV = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ lopen la ∷ [] )
