------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXII
--
-- Stanza XII: the velvet seat; pa jamēña-toki ñe L₇-añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XII : Stanza
stanza-XII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody la ∷ llaref pa ∷ [] )
