------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI
--
-- Stanza XVI: Aidenn; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XVI : Stanza
stanza-XVI = mk-stanza
  ( lbody la ∷ lbody pa ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ llock ñi ∷ [] )
