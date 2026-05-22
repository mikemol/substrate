------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXI
--
-- Stanza XI: the bird's word; body references añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXI where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XI : Stanza
stanza-XI = mk-stanza
  ( lbody se ∷ lbody la ∷ lbody pa ∷ lbody ñi ∷ lbody pa ∷ llaref la ∷ [] )
