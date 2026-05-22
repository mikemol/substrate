------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII
--
-- Stanza XVII: parting plea; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XVII : Stanza
stanza-XVII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody pa ∷ lbody ñi ∷ llock ñi ∷ [] )
