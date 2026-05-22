------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.StanzaVII
--
-- Stanza VII: the lattice flung.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.StanzaVII where

open import Substrate.Foundation.List using ([]; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar
  using (KelenRelation; pa; ñi; se; la; Stanza; mk-stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.LineShorthands
  using (lbody; lopen; llock; llaref)

stanza-VII : Stanza
stanza-VII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ lopen pa ∷ [] )
