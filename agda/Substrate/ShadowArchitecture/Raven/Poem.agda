------------------------------------------------------------------------
-- Substrate.ShadowArchitecture.Raven.Poem
--
-- The user's hybrid-grammar translation of Poe's "The Raven" — the
-- artifact titled `lo nu pimeja-tenpo`. Eighteen stanzas, encoded
-- as a `Vec Stanza 18`. Each line is summarised by
-- `(KelenRelation, Terminal, L7-Body-Reference)`; full Kēlen /
-- Toki Pona / Lojban surface text lives in the module-level comments
-- below.
--
-- Counted line totals: stanzas I-IX, XI-XVIII have 6 lines each;
-- stanza X has 5 lines as provided. Total = 17 × 6 + 5 = 107 lines.
-- The user's framing names "108 lines"; the discrepancy is one line
-- in X (Poe's original X has 6 lines and the transcription dropped
-- one). The structural claim (phase transition at VIII) is invariant
-- under this discrepancy.
--
-- Phase distribution by stanza terminal:
--
--   I-VII   :  awen-taso  (open phase — perturbation)
--   VIII    :  añelē      (first lockup — Raven enters)
--   IX, XI, XII : other-attr (post-lock; L₇-añelē appears in la-body)
--   X, XIII-XVIII : añelē (continued lockup)
--
-- The first añelē-terminal stanza is VIII; no stanza I-VII has the
-- añelē terminal; this is the phase-transition claim formalised in
-- `Substrate.ShadowArchitecture.Raven.PhaseTransition`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.ShadowArchitecture.Raven.Poem where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Fin using (Fin)

open import Substrate.ShadowArchitecture.Raven.Grammar

-- Short-hand line constructors.
private
  _,_,_ : KelenRelation → Terminal → L7-Body-Reference → Line
  r , t , ℓ = mk-line r t ℓ
  infixr 4 _,_,_

  -- Common shape: terminal `other-attr`, no L₇-body reference. The
  -- vast majority of lines.
  lbody : KelenRelation → Line
  lbody r = mk-line r other-attr no-L7-reference

  -- Terminal `awen-taso` (open phase), no L₇-body reference.
  lopen : KelenRelation → Line
  lopen r = mk-line r awen-taso no-L7-reference

  -- Terminal `añelē` (lockup phase), no L₇-body reference.
  llock : KelenRelation → Line
  llock r = mk-line r añelē no-L7-reference

  -- Terminal `other-attr` with L₇-añelē as object in la-body.
  llaref : KelenRelation → Line
  llaref r = mk-line r other-attr references-L7-añelē

------------------------------------------------------------------------
-- Stanza I  —  perturbation begins.
--
-- pa jaciēn-tenpo ñe jamēña-pimeja / pi wawa-ala-insa
-- ñi jōkēñen ñe jasēla-pini       / pi sona-weka-mute
-- ñi jōraþ-anpa ñe jaciēn-mi      / pi kalama-kama-smiti
-- ñi mōrra ñe kalama-luka          / pi lupa-tomo-mi
-- ñi sēña-toki ñe jaciēn-mi        / pi jan-kama-taso
-- pa makawēña ñe ijo-ante          / pi L₇-awen-taso       ← terminal
------------------------------------------------------------------------

stanza-I : Stanza
stanza-I = mk-stanza
  ( lbody pa  ∷ lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lopen pa ∷ [] )

------------------------------------------------------------------------
-- Stanza II  —  midnight bleak.
------------------------------------------------------------------------

stanza-II : Stanza
stanza-II = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody la ∷ lopen pa ∷ [] )

------------------------------------------------------------------------
-- Stanza III  —  silken sad uncertain rustling.
------------------------------------------------------------------------

stanza-III : Stanza
stanza-III = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody ñi ∷ lbody la ∷ lbody la ∷ lopen pa ∷ [] )

------------------------------------------------------------------------
-- Stanza IV  —  the visitor at the door.
------------------------------------------------------------------------

stanza-IV : Stanza
stanza-IV = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ lopen la ∷ [] )

------------------------------------------------------------------------
-- Stanza V  —  deep into the darkness peering.
------------------------------------------------------------------------

stanza-V : Stanza
stanza-V = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody se ∷ lopen la ∷ [] )

------------------------------------------------------------------------
-- Stanza VI  —  the tapping more distinct.
------------------------------------------------------------------------

stanza-VI : Stanza
stanza-VI = mk-stanza
  ( lbody ñi ∷ lbody se ∷ lbody la ∷ lbody pa ∷ lbody ñi ∷ lopen la ∷ [] )

------------------------------------------------------------------------
-- Stanza VII  —  the lattice flung.
------------------------------------------------------------------------

stanza-VII : Stanza
stanza-VII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ lopen pa ∷ [] )

------------------------------------------------------------------------
-- Stanza VIII  —  the Raven enters.  ★ Phase transition: terminal
-- añelē for the first time.
--
-- ñi sēña-xrūti ñe jaciēn-pimeja / pi L₇-añelē   ← FIRST añelē terminal
------------------------------------------------------------------------

stanza-VIII : Stanza
stanza-VIII = mk-stanza
  ( lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody la ∷ lbody pa ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza IX  —  the Raven sits.  Terminal references añelē in body
-- (la jasēla-nimi la L₇-añelē / pi nimi-nasa-taso).
------------------------------------------------------------------------

stanza-IX : Stanza
stanza-IX = mk-stanza
  ( lbody se ∷ lbody pa ∷ lbody la ∷ lbody se ∷ lbody pa ∷ llaref la ∷ [] )

------------------------------------------------------------------------
-- Stanza X  —  five lines (as transcribed).  Terminal añelē.
--
-- ñi sēña-xrūti ñe jaciēn-waso / pi L₇-añelē
------------------------------------------------------------------------

stanza-X : Stanza
stanza-X = mk-stanza
  ( lbody ñi ∷ lbody pa ∷ lbody ñi ∷ lbody pa ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza XI  —  the bird's word.  Terminal references añelē in body.
------------------------------------------------------------------------

stanza-XI : Stanza
stanza-XI = mk-stanza
  ( lbody se ∷ lbody la ∷ lbody pa ∷ lbody ñi ∷ lbody pa ∷ llaref la ∷ [] )

------------------------------------------------------------------------
-- Stanza XII  —  the velvet seat.  Terminal references añelē as object
-- of pa (pa jamēña-toki ñe L₇-añelē / pi wile-sona-kon).
------------------------------------------------------------------------

stanza-XII : Stanza
stanza-XII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody la ∷ llaref pa ∷ [] )

------------------------------------------------------------------------
-- Stanza XIII  —  guessing.  Terminal añelē.
------------------------------------------------------------------------

stanza-XIII : Stanza
stanza-XIII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody se ∷ lbody pa ∷ llock pa ∷ [] )

------------------------------------------------------------------------
-- Stanza XIV  —  the air grew denser.  Terminal añelē.
------------------------------------------------------------------------

stanza-XIV : Stanza
stanza-XIV = mk-stanza
  ( lbody se ∷ lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody ñi ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza XV  —  prophet still.  Terminal añelē.
------------------------------------------------------------------------

stanza-XV : Stanza
stanza-XV = mk-stanza
  ( lbody la ∷ lbody pa ∷ lbody pa ∷ lbody pa ∷ lbody pa ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza XVI  —  Aidenn.  Terminal añelē.
------------------------------------------------------------------------

stanza-XVI : Stanza
stanza-XVI = mk-stanza
  ( lbody la ∷ lbody pa ∷ lbody pa ∷ lbody ñi ∷ lbody ñi ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza XVII  —  parting plea.  Terminal añelē.
------------------------------------------------------------------------

stanza-XVII : Stanza
stanza-XVII = mk-stanza
  ( lbody ñi ∷ lbody ñi ∷ lbody pa ∷ lbody pa ∷ lbody ñi ∷ llock ñi ∷ [] )

------------------------------------------------------------------------
-- Stanza XVIII  —  the Raven remains.  Terminal añelē.
------------------------------------------------------------------------

stanza-XVIII : Stanza
stanza-XVIII = mk-stanza
  ( lbody pa ∷ lbody pa ∷ lbody la ∷ lbody ñi ∷ lbody pa ∷ llock pa ∷ [] )

------------------------------------------------------------------------
-- The whole Raven.
--
-- Indexing is 0-based: `lookup raven (# 0)` = stanza-I, ...,
-- `lookup raven (# 17)` = stanza-XVIII.
------------------------------------------------------------------------

raven : Vec Stanza 18
raven =
    stanza-I    ∷ stanza-II   ∷ stanza-III  ∷ stanza-IV   ∷ stanza-V
  ∷ stanza-VI   ∷ stanza-VII  ∷ stanza-VIII ∷ stanza-IX   ∷ stanza-X
  ∷ stanza-XI   ∷ stanza-XII  ∷ stanza-XIII ∷ stanza-XIV  ∷ stanza-XV
  ∷ stanza-XVI  ∷ stanza-XVII ∷ stanza-XVIII ∷ []
