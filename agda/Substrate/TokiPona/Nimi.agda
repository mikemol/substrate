------------------------------------------------------------------------
-- Substrate.TokiPona.Nimi
--
-- T2 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]]. The vocabulary basis: 32 nimi
-- spanning the lexical classes of Toki Pona (content nouns, content
-- verbs/adjectives, pronouns, particles, connectives).
--
-- Per [[feedback-expose-generator-not-orbit]] the nimi ARE the
-- generators of the semantic space; flat enumeration is the correct
-- shape because nimi form a finite vocabulary, not a derived orbit.
--
-- The 32-nimi choice is deliberately small (one slice's-worth of
-- worked vocabulary). Real Toki Pona has ~120 core nimi pu; the
-- fragment can extend mechanically. The selection covers all five
-- grammatical classes so the linearity / particle structure can be
-- exercised without expanding scope.
--
-- Per [[feedback-multi-reading-ambient-discipline]]: each nimi has
-- broad polysemy in real Toki Pona; the fragment formalises one
-- reading per nimi at the basis level, and the contrastive richness
-- emerges through MODIFIER COMBINATIONS (T4 ModifierBilinear) rather
-- than per-nimi richness. Gauge-honest framing of polysemy.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Nimi where

open import Substrate.Foundation.Nat using (ℕ; suc; zero)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃; ₄; ₅; ₆; ₇; ₈; ₉; ₁₀; ₁₁; ₁₂; ₁₃; ₁₄; ₁₅; ₁₆; ₁₇; ₁₈; ₁₉; ₂₀; ₂₁; ₂₂; ₂₃; ₂₄; ₂₅; ₂₆; ₂₇; ₂₈; ₂₉; ₃₀)
open import Substrate.Foundation.Fin using (Fin; zero; suc)

------------------------------------------------------------------------
-- 1. The Nimi enumeration (32 nimi).
--
-- Grouped by grammatical class. Each nimi's prose gloss is the
-- comment; per [[feedback-comments-dont-overclaim]] the gloss is
-- prose-level and not enforced by the typechecker.
------------------------------------------------------------------------

data Nimi : Set where
  -- Content nouns (9)
  jan    : Nimi   -- person, human
  soweli : Nimi   -- animal, mammal
  kili   : Nimi   -- fruit, vegetable
  moku   : Nimi   -- food, eating
  tomo   : Nimi   -- house, building
  ma     : Nimi   -- land, country
  telo   : Nimi   -- water, liquid
  ilo    : Nimi   -- tool
  ijo    : Nimi   -- thing, object
  -- Content verbs / adjectives (9)
  pona   : Nimi   -- good, simple
  ike    : Nimi   -- bad
  suli   : Nimi   -- big, important
  lili   : Nimi   -- small
  wawa   : Nimi   -- strong, powerful
  sin    : Nimi   -- new
  toki   : Nimi   -- talk, communicate
  olin   : Nimi   -- love
  pana   : Nimi   -- give
  -- Pronouns (4)
  mi     : Nimi   -- I, we
  sina   : Nimi   -- you
  ona    : Nimi   -- he/she/it/they
  ni     : Nimi   -- this, that
  -- Particles (5) — treated structurally in T6
  li-p   : Nimi   -- li (predicate marker)
  e-p    : Nimi   -- e (object marker)
  pi-p   : Nimi   -- pi (modifier regrouping)
  la-p   : Nimi   -- la (context marker)
  o-p    : Nimi   -- o (vocative / imperative)
  -- Connectives (5)
  en     : Nimi   -- and
  tan    : Nimi   -- from, because
  tawa   : Nimi   -- toward, for
  lon    : Nimi   -- at, in
  kepeken : Nimi  -- use, with

------------------------------------------------------------------------
-- 2. NimiClass — lexical-class classification.
--
-- T6 uses this to dispatch on particle vs content vs pronoun when
-- constructing structural markers.
------------------------------------------------------------------------

data NimiClass : Set where
  content-noun : NimiClass
  content-verb : NimiClass
  pronoun      : NimiClass
  particle     : NimiClass
  connective   : NimiClass

classify : Nimi → NimiClass
classify jan      = content-noun
classify soweli   = content-noun
classify kili     = content-noun
classify moku     = content-noun
classify tomo     = content-noun
classify ma       = content-noun
classify telo     = content-noun
classify ilo      = content-noun
classify ijo      = content-noun
classify pona     = content-verb
classify ike      = content-verb
classify suli     = content-verb
classify lili     = content-verb
classify wawa     = content-verb
classify sin      = content-verb
classify toki     = content-verb
classify olin     = content-verb
classify pana     = content-verb
classify mi       = pronoun
classify sina     = pronoun
classify ona      = pronoun
classify ni       = pronoun
classify li-p     = particle
classify e-p      = particle
classify pi-p     = particle
classify la-p     = particle
classify o-p      = particle
classify en       = connective
classify tan      = connective
classify tawa     = connective
classify lon      = connective
classify kepeken  = connective

------------------------------------------------------------------------
-- 3. Vocabulary cardinality.
------------------------------------------------------------------------

nimi-count : ℕ
nimi-count = 32

------------------------------------------------------------------------
-- 4. Nimi → Fin nimi-count index map.
--
-- The basis-index assignment used by T3 (NimiSpace) to instantiate
-- FreeLinearization. Each nimi gets a unique position in [0, 32);
-- assignment follows the declaration order above.
--
-- Per [[feedback-ordering-is-chirality-choice]]: this ordering is a
-- gauge choice (any bijection Nimi ↔ Fin 32 works); we document it
-- as a convention and let it float. Downstream proofs do not depend
-- on the specific assignment.
------------------------------------------------------------------------

nimi-index : Nimi → Fin nimi-count
nimi-index jan      = zero
nimi-index soweli   = suc zero
nimi-index kili     = suc ₁
nimi-index moku     = suc ₂
nimi-index tomo     = suc ₃
nimi-index ma       = suc ₄
nimi-index telo     = suc ₅
nimi-index ilo      = suc ₆
nimi-index ijo      = suc ₇
nimi-index pona     = suc ₈
nimi-index ike      = suc ₉
nimi-index suli     = suc ₁₀
nimi-index lili     = suc ₁₁
nimi-index wawa     = suc ₁₂
nimi-index sin      = suc ₁₃
nimi-index toki     = suc ₁₄
nimi-index olin     = suc ₁₅
nimi-index pana     = suc ₁₆
nimi-index mi       = suc ₁₇
nimi-index sina     = suc ₁₈
nimi-index ona      = suc ₁₉
nimi-index ni       = suc ₂₀
nimi-index li-p     = suc ₂₁
nimi-index e-p      = suc ₂₂
nimi-index pi-p     = suc ₂₃
nimi-index la-p     = suc ₂₄
nimi-index o-p      = suc ₂₅
nimi-index en       = suc ₂₆
nimi-index tan      = suc ₂₇
nimi-index tawa     = suc ₂₈
nimi-index lon      = suc ₂₉
nimi-index kepeken  = suc ₃₀
