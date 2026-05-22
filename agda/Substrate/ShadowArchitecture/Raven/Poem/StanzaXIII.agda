------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII
--
-- Stanza XIII: guessing; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XIII : Stanza
stanza-XIII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody se ∷ lbody pa ∷ llock pa ∷ [] )
