------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaVI
--
-- Stanza VI: the tapping more distinct.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaVI where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-VI : Stanza
stanza-VI = mk-stanza
  ( lbody ñi ∷ lbody se ∷ lbody la ∷ lbody pa ∷ lbody ñi ∷ lopen la ∷ [] )
