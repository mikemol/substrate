------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem.Raven
--
-- The whole Raven as a Vec Stanza 18. 0-based indexing:
-- `lookup raven (# 0)` = stanza-I, …, `lookup raven (# 17)` = stanza-XVIII.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem.Raven where

open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.ShadowArchitecture.Raven.Grammar using (Stanza)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaI     using (stanza-I)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaII    using (stanza-II)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIII   using (stanza-III)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIV    using (stanza-IV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaV     using (stanza-V)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVI    using (stanza-VI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVII   using (stanza-VII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVIII  using (stanza-VIII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIX    using (stanza-IX)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaX     using (stanza-X)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXI    using (stanza-XI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXII   using (stanza-XII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII  using (stanza-XIII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV   using (stanza-XIV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXV    using (stanza-XV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI   using (stanza-XVI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII  using (stanza-XVII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII using (stanza-XVIII)

raven : Vec Stanza 18
raven =
    stanza-I    ∷ stanza-II   ∷ stanza-III  ∷ stanza-IV   ∷ stanza-V
  ∷ stanza-VI   ∷ stanza-VII  ∷ stanza-VIII ∷ stanza-IX   ∷ stanza-X
  ∷ stanza-XI   ∷ stanza-XII  ∷ stanza-XIII ∷ stanza-XIV  ∷ stanza-XV
  ∷ stanza-XVI  ∷ stanza-XVII ∷ stanza-XVIII ∷ []
