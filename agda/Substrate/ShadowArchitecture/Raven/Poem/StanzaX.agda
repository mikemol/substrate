------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaX
--
-- Stanza X: five lines as transcribed; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaX where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-X : Stanza
stanza-X = mk-stanza
  ( lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody pa ∷ llock ñi ∷ [] )
