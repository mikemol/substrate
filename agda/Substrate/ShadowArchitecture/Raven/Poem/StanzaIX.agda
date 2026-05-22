------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaIX
--
-- Stanza IX: the Raven sits — la jasēla-nimi la L₇-añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaIX where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-IX : Stanza
stanza-IX = mk-stanza
  ( lbody se ∷ lbody pa ∷ lbody la ∷ lbody se ∷ lbody pa ∷ llaref la ∷ [] )
