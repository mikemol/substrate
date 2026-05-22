------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXV
--
-- Stanza XV: prophet still; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXV where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XV : Stanza
stanza-XV = mk-stanza
  ( lbody la ∷ lbody pa ∷ lbody pa ∷ lbody pa ∷ lbody pa ∷ llock ñi ∷ [] )
