------------------------------------------------------------------------
-- Substrate.Kelen.Fragment
--
-- C5 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Kēlen as the **Free relation** witness — the most structurally
-- distinctive cell of the lattice per the peer review. Kēlen is a
-- conlang by Sylvia Sotomayor that has NO VERBS; meaning is carried
-- by four "relationals" (la, nā, pa, jana) applied to argument
-- lists. The categorical home is the category of sets and
-- RELATIONS (Rel) rather than the category of sets and functions
-- (Set).
--
-- DISTINGUISHING FEATURE versus Lojban / Toki Pona:
--   - Lojban: composition of functions (free monoid → CCC)
--   - Toki Pona: linear pooling (free F₂-module)
--   - Kēlen: relations (free relation algebra) — non-functional,
--     possibly non-deterministic, dagger-style
--
-- Real Kēlen relations have rich semantics (la = "state of being",
-- nā = "existence/event", pa = "composition/possession", jana =
-- "motion/change"); the fragment captures only the basis +
-- free-monoid-of-relations layer per [[feedback-comments-dont-overclaim]].
--
-- Per [[feedback-categorical-name-first]]: the categorical name for
-- this cell is "free relation algebra" or "free dagger category" —
-- in either case fundamentally non-functional.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Kelen.Fragment where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Category.FreeOverBasis
  using (FreeOverBasis; mkFreeOverBasis;
         LanguageWitness; mkWitness;
         FreeConstructionClass; Free-relation;
         WitnessName; Kelen)

------------------------------------------------------------------------
-- 1. The 4 Kēlen relationals.
--
-- Each carries a place-structure arity (the number of NP slots);
-- in real Kēlen, the relationals have positional semantics tied
-- to their meaning.
------------------------------------------------------------------------

data Relational : Set where
  la    : Relational   -- "is in state of" (2-place: la NP-be NP-state)
  nā    : Relational   -- "happens / exists" (1-place existential)
  pa    : Relational   -- "consists of / has" (3-place possession)
  jana  : Relational   -- "moves toward / changes" (3-place motion)

arity : Relational → ℕ
arity la    = 2
arity nā    = 1
arity pa    = 3
arity jana  = 3

------------------------------------------------------------------------
-- 2. Sequences of relationals.
--
-- A KelenWord is a sequence of relationals; this is the free
-- carrier in the Free-relation cell. Composition of relationals
-- (relation composition in Rel) is the algebra acting on this
-- carrier; full relation composition is deferred per
-- [[feedback-coalgebraic-not-consumer-driven]].
------------------------------------------------------------------------

KelenWord : Set
KelenWord = Word Relational

ε : KelenWord
ε = []

single : Relational → KelenWord
single r = r ∷ []

------------------------------------------------------------------------
-- 3. Worked example: a small Kēlen sentence skeleton.
--
-- "la NP NP" — a state-of-being assertion. In real Kēlen this
-- requires Sumti-like noun-phrase arguments; here we represent
-- just the relational skeleton.
------------------------------------------------------------------------

example-la-skeleton : KelenWord
example-la-skeleton = la ∷ []

-- A composed sentence skeleton: "la ... pa ..." — being-state
-- followed by composition-of (relation composition).
example-la-pa : KelenWord
example-la-pa = la ∷ pa ∷ []

------------------------------------------------------------------------
-- 4. The DISTINGUISHING note: Kēlen relations are NOT functions.
--
-- A relation R : A ↔ B is a subset of A × B (multiple outputs per
-- input allowed; some inputs may have NO outputs). This is
-- fundamentally different from Lojban's Selbri (a function-like
-- n-ary morphism) or Toki Pona's modify (a binary commutative-
-- monoid op).
--
-- Per [[feedback-comments-dont-overclaim]] the full Rel-category
-- machinery (dagger, residuals, etc.) is not in this slice; the
-- FreeOverBasis witness here records that the cell IS occupied,
-- with deeper relation-algebra structure deferred.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 5. The FreeOverBasis instance.
------------------------------------------------------------------------

kelen-free-structure : FreeOverBasis Relational KelenWord
kelen-free-structure = mkFreeOverBasis single

kelen-witness : LanguageWitness
kelen-witness = mkWitness
  Kelen
  Relational
  KelenWord
  kelen-free-structure
  Free-relation
