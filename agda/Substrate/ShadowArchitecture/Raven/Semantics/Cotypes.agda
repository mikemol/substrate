------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Semantics.Cotypes
--
-- The 19 snapshot Cotypes c0..c18. cₙ is the state after the first
-- n stanzas have been interpreted; c0 is empty (before any stanza).
-- An indexed structural sequence: each cN depends on c{N-1}.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Semantics.Cotypes where
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVIII using (stanza-XVIII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVII using (stanza-XVII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXVI using (stanza-XVI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXV using (stanza-XV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIV using (stanza-XIV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXIII using (stanza-XIII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXII using (stanza-XII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaXI using (stanza-XI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaX using (stanza-X)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIX using (stanza-IX)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVIII using (stanza-VIII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVII using (stanza-VII)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaVI using (stanza-VI)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaV using (stanza-V)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIV using (stanza-IV)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaIII using (stanza-III)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaII using (stanza-II)
open import Substrate.ShadowArchitecture.Raven.Poem.StanzaI using (stanza-I)

open import Substrate.ShadowArchitecture.Persistence using (Cotype; empty-cotype)
open import Substrate.ShadowArchitecture.Raven.Poem
open import Substrate.ShadowArchitecture.Raven.Semantics.InterpretStanza
  using (interpret-stanza)

c0  : Cotype
c0  = empty-cotype
c1  : Cotype
c1  = interpret-stanza stanza-I     c0
c2  : Cotype
c2  = interpret-stanza stanza-II    c1
c3  : Cotype
c3  = interpret-stanza stanza-III   c2
c4  : Cotype
c4  = interpret-stanza stanza-IV    c3
c5  : Cotype
c5  = interpret-stanza stanza-V     c4
c6  : Cotype
c6  = interpret-stanza stanza-VI    c5
c7  : Cotype
c7  = interpret-stanza stanza-VII   c6
c8  : Cotype
c8  = interpret-stanza stanza-VIII  c7
c9  : Cotype
c9  = interpret-stanza stanza-IX    c8
c10 : Cotype
c10 = interpret-stanza stanza-X     c9
c11 : Cotype
c11 = interpret-stanza stanza-XI    c10
c12 : Cotype
c12 = interpret-stanza stanza-XII   c11
c13 : Cotype
c13 = interpret-stanza stanza-XIII  c12
c14 : Cotype
c14 = interpret-stanza stanza-XIV   c13
c15 : Cotype
c15 = interpret-stanza stanza-XV    c14
c16 : Cotype
c16 = interpret-stanza stanza-XVI   c15
c17 : Cotype
c17 = interpret-stanza stanza-XVII  c16
c18 : Cotype
c18 = interpret-stanza stanza-XVIII c17
