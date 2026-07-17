------------------------------------------------------------------------
-- Substrate.Linguistic.Classification
--
-- C8 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- The lattice record: catalogues all six LanguageWitness instances
-- across the classification cells, provides lookup by name and by
-- FreeConstructionClass, and exposes the classification as a
-- substrate-internal structure that C9 (RosettaTable) consumes for
-- pairwise cross-language alignment.
--
-- This is the "objects" side of the category-of-languages
-- (Yoneda perspective): C8 gives the set of objects; C9 gives the
-- morphisms / alignments. Per the peer-review observation:
-- "study objects via how they relate to each other" — this slice
-- + C9 jointly are the substrate's category-of-languages.
--
-- Per [[feedback-categorical-name-first]]: the categorical name is
-- "an indexed family of free constructions" — a discrete category
-- whose objects are FreeConstructionClass cells with one witness
-- per occupied cell.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Classification where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis
  using (WitnessName;
         Lojban; TokiPona; Solresol; Kelen; Lambda; LieFrag;
         FreeConstructionClass;
         Free-monoid; Free-F2-module; Free-cyclic; Free-relation;
         Free-CCC; Free-Lie; Free-other;
         name; class)

open import Substrate.Linguistic.Roster
  using (Lang; lojban; tokipona; solresol; kelen; lambda-lang; lie-lang; witness-of)

------------------------------------------------------------------------
-- 1. The catalogue of six witnesses.
--
-- One Lang value per occupied cell of the classification lattice.
-- The Vec-shaped collection lets C9 iterate over all pairs for
-- Rosetta-table generation. (⟡rc-lang, W5-L3: the Vec now carries
-- the Set₀ enum, not the witnesses directly — witness-of decodes.)
------------------------------------------------------------------------

witness-count : ℕ
witness-count = 6

all-witnesses : Vec Lang witness-count
all-witnesses =
  lojban      ∷
  tokipona    ∷
  solresol    ∷
  kelen       ∷
  lambda-lang ∷
  lie-lang    ∷
  []

------------------------------------------------------------------------
-- 2. Lookup by WitnessName.
--
-- A six-case dispatch from the enum to the corresponding Lang value.
-- C9 uses this to display witness pairs in tables.
------------------------------------------------------------------------

witness-by-name : WitnessName → Lang
witness-by-name Lojban   = lojban
witness-by-name TokiPona = tokipona
witness-by-name Solresol = solresol
witness-by-name Kelen    = kelen
witness-by-name Lambda   = lambda-lang
witness-by-name LieFrag  = lie-lang

------------------------------------------------------------------------
-- 3. Lookup by FreeConstructionClass.
--
-- Each cell has exactly one witness in this arc (extensible: future
-- arcs may add multiple witnesses per cell, in which case this
-- becomes a Vec-valued lookup).
--
-- The `Free-other` cell has NO witness in this arc — returned by
-- convention as the Lojban witness (placeholder); future arcs
-- adding witnesses fix this. Per [[feedback-comments-dont-overclaim]]
-- this is documented rather than overclaimed.
------------------------------------------------------------------------

witness-by-class : FreeConstructionClass → Lang
witness-by-class Free-monoid    = lojban
witness-by-class Free-F2-module = tokipona
witness-by-class Free-cyclic    = solresol
witness-by-class Free-relation  = kelen
witness-by-class Free-CCC       = lambda-lang
witness-by-class Free-Lie       = lie-lang
witness-by-class Free-other     = lojban  -- placeholder

------------------------------------------------------------------------
-- 4. Round-trip coherence: name → witness → name preserves.
--
-- Each witness records its own name; lookup followed by name
-- recovery is the identity. Six refl cases.
------------------------------------------------------------------------

name∘witness-by-name : (n : WitnessName) → name (witness-of (witness-by-name n)) ≡ n
name∘witness-by-name Lojban   = refl
name∘witness-by-name TokiPona = refl
name∘witness-by-name Solresol = refl
name∘witness-by-name Kelen    = refl
name∘witness-by-name Lambda   = refl
name∘witness-by-name LieFrag  = refl

------------------------------------------------------------------------
-- 5. Round-trip coherence: class → witness → class preserves.
--
-- For the six occupied cells, witness-by-class then class recovers
-- the original. Free-other is the documented placeholder.
------------------------------------------------------------------------

-- Substrate-native disjoint union for the round-trip statement
-- (avoids Data.Sum per [[feedback-minimize-stdlib-deps]]-strengthened).
data _⊎-OR_ (A B : Set) : Set where
  here  : A → A ⊎-OR B
  there : B → A ⊎-OR B

class∘witness-by-class :
  (c : FreeConstructionClass) →
  (c ≡ Free-other) ⊎-OR (class (witness-of (witness-by-class c)) ≡ c)
class∘witness-by-class Free-monoid    = there refl
class∘witness-by-class Free-F2-module = there refl
class∘witness-by-class Free-cyclic    = there refl
class∘witness-by-class Free-relation  = there refl
class∘witness-by-class Free-CCC       = there refl
class∘witness-by-class Free-Lie       = there refl
class∘witness-by-class Free-other     = here refl
