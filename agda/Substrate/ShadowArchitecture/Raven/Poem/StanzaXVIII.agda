------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII
--
-- Stanza XVIII: the Raven remains; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XVIII : Stanza
stanza-XVIII = mk-stanza
  ( lbody pa ∷ lbody pa ∷ lbody la ∷ lbody ñi ∷ lbody pa ∷ llock pa ∷ [] )
