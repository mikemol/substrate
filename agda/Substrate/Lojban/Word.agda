------------------------------------------------------------------------
-- Substrate.Lojban.Word
--
-- L2 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Costructure shadow #2: `LojbanWord` as a Coxeter Word adapter over
-- a gismu generator alphabet. Free monoid structure now; rafsi-merge
-- relations layer on top at L4 (Lujvo).
--
-- Per [[feedback-prefer-coxeter-backed]] /
-- [[feedback-roll-our-own-via-word-algebra]]: word-algebra
-- constructions are favoured over set / matrix / permutation
-- carriers. This module routes Lojban morphology through
-- Substrate.Groups.Coxeter.Word — the same Word type V₄, Z₂, and
-- the larger Coxeter zoo already share — so that L4 can swap in
-- rafsi-merge relations via Substrate.Groups.Coxeter.ListPresentation
-- without re-deriving framework machinery.
--
-- Per [[feedback-grothendieck-coherence-rule]]: the free-merge
-- operation is associative with two-sided identity (a strict
-- monoid), discharged here at L2. L8 (WordAlgebra) consumes this
-- monoid structure to prove the homomorphism into semantic
-- interpretation.
--
-- Parametric in (Gismu : Set) so that L3 supplies the concrete
-- vocabulary table. Toki Pona's discrete syntactic skeleton can
-- also instantiate this with its own generator alphabet.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Word (Gismu : Set) where

open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-assoc; ++-identity-left; ++-identity-right)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid using (MonoidOn)

------------------------------------------------------------------------
-- 1. LojbanWord : a word over the gismu generator alphabet.
--
-- The carrier is exactly Substrate.Groups.Coxeter.Word.Word Gismu.
-- The substrate-canonical name is "Word Gismu"; the linguistic name
-- is "LojbanWord". Both refer to the same data — the contrastive-
-- pedagogy point is that the Lojban arc can be read without
-- bouncing into the Coxeter generics.
------------------------------------------------------------------------

LojbanWord : Set
LojbanWord = Word Gismu

------------------------------------------------------------------------
-- 2. Empty word (identity for free-merge).
------------------------------------------------------------------------

ε : LojbanWord
ε = []

------------------------------------------------------------------------
-- 3. Single-gismu lift.
--
-- The free generator embedding: each gismu becomes a one-symbol
-- word. This is the inclusion of generators into the word algebra.
------------------------------------------------------------------------

single : Gismu → LojbanWord
single g = g ∷ []

------------------------------------------------------------------------
-- 4. Free merge (free concatenation).
--
-- Pure concatenation, no relations applied. L4 layers rafsi-merge
-- on top via Substrate.Groups.Coxeter.ListPresentation, turning
-- this free merge into a quotient by the rafsi-merge equations.
------------------------------------------------------------------------

free-merge : LojbanWord → LojbanWord → LojbanWord
free-merge = _++_

------------------------------------------------------------------------
-- 5. Monoid laws on free-merge.
--
-- These are the [[feedback-grothendieck-coherence-rule]] obligations
-- discharged at L2. L8 lifts them to the homomorphism statement.
------------------------------------------------------------------------

free-merge-assoc :
  (a b c : LojbanWord) →
  free-merge (free-merge a b) c ≡ free-merge a (free-merge b c)
free-merge-assoc = ++-assoc

free-merge-identity-left :
  (w : LojbanWord) → free-merge ε w ≡ w
free-merge-identity-left = ++-identity-left

free-merge-identity-right :
  (w : LojbanWord) → free-merge w ε ≡ w
free-merge-identity-right = ++-identity-right

------------------------------------------------------------------------
-- 6. GROUNDED: (LojbanWord, free-merge, ε) IS a substrate-named `MonoidOn`
-- (Category.FreeUniversalProperty.FreeMonoid) — the morphology free monoid,
-- an instance of the word-algebra center's free-monoid (cf. `word-monoid`
-- for any `Word Gen`). The bare laws above witness the named primitive.
--
-- Lojban-note: this is the MORPHOLOGY layer only — words as free gismu
-- sequences. Lojban's LOGIC (the 16 Boolean connectives of the A/JA/GIhA/GUhA
-- selma'o, the bridi predication, the Cartesian-closed structure) lives in
-- Bridi / AsCCC / Cmavo, not here; rafsi-merge quotients this free monoid at
-- L4 (Lujvo). Free monoid is the correct primitive for L2.
------------------------------------------------------------------------

free-merge-MonoidOn : MonoidOn LojbanWord
free-merge-MonoidOn = record
  { ε       = ε
  ; _∙_     = free-merge
  ; ∙-assoc = free-merge-assoc
  ; ε-left  = free-merge-identity-left
  ; ε-right = free-merge-identity-right
  }
