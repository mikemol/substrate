------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaI
--
-- Stanza I: perturbation begins.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaI where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-I : Stanza
stanza-I = mk-stanza
  ( lbody pa ∷ lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lopen pa ∷ [] )
