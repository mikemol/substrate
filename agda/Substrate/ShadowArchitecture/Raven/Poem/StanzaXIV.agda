------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV
--
-- Stanza XIV: the air grew denser; terminal añelē.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-XIV : Stanza
stanza-XIV = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ llock ñi ∷ [] )
