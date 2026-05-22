------------------------------------------------------------------------
-- Substrate.Category.FreeOverBasis
--
-- C1 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- The shared parent primitive of "Free X over a basis" — extracted
-- per [[feedback-coalgebraic-not-consumer-driven]] now that Lojban
-- L8 (free-monoid extension) and Toki Pona T8 (free-F₂-module
-- extension) have demonstrated the pattern twice. This arc adds
-- four more witness instances, taking the count of sister sites
-- past the extraction threshold.
--
-- The categorical content: a FreeOverBasis pairs a basis B with a
-- free carrier F-of-B and a unit η : B → F-of-B (the embedding of
-- generators into the free structure). The UNIVERSAL PROPERTY (any
-- function B → M into a target-with-structure extends uniquely to
-- a structure-preserving F-of-B → M) is per-instance because the
-- "structure" depends on the AlgebraClass (Monoid for free monoid,
-- F₂-Module for free F₂-module, CCC for free CCC, ...). Each
-- instance provides its own AlgebraClass-specific universal-
-- property witness; this module just names the shared SHAPE.
--
-- The classification enum FreeConstructionClass indexes which cell
-- of the language-by-free-construction lattice each instance
-- occupies. C8 (Classification) consumes the enum to package the
-- six witness instances; C9 (RosettaTable) consumes the
-- classification for pairwise cross-language alignment.
--
-- Per [[feedback-categorical-name-first]]: "free X over basis" is
-- the universal categorical name covering free monoid, free module,
-- free CCC, free relation, etc. The parent primitive names the
-- pattern; instances cite it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FreeOverBasis where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

private
  variable
    ℓB ℓF : Level

------------------------------------------------------------------------
-- 1. FreeOverBasis: the shared shape.
--
-- A FreeOverBasis pairs a basis B with a free carrier F-of-B and a
-- unit η : B → F-of-B. The universal property is instance-specific:
-- each AlgebraClass (Monoid, F₂-Module, CCC, ...) provides its own
-- structure-preservation laws and uniqueness witness. This record
-- captures only the data; the universal property lives in
-- per-instance modules.
------------------------------------------------------------------------

record FreeOverBasis (B : Set ℓB) (F-of-B : Set ℓF) : Set (ℓB ⊔ ℓF) where
  constructor mkFreeOverBasis
  field
    η : B → F-of-B

open FreeOverBasis public

------------------------------------------------------------------------
-- 1a. AlgebraClass: structured record of (Has-structure, Hom-preserves).
--
-- Per peer-review recommendation: tighten the "algebra class" notion
-- from a free-floating predicate into a record bundling
--   * Has-structure : Set → Set     (which carriers have this structure)
--   * Hom-preserves : ...             (when a function preserves structure)
--
-- Each FreeConstructionClass (Free-monoid, Free-F2-module, Free-CCC,
-- Free-relation, ...) provides ONE canonical AlgebraClass instance,
-- packaging the structural laws + morphism-preservation predicate
-- that downstream consumers (C8 Classification, C9 RosettaTable) can
-- reference uniformly.
--
-- KEPT LIGHT: instances may or may not fill in a rich AlgebraClass —
-- the universal property's heavy lifting still lives in per-instance
-- modules (Lojban L8 WordAlgebra, Toki Pona T8 LinearAlgebra, etc.).
-- This record exists so C8/C9 have a uniform handle when they need
-- one. Per [[feedback-coalgebraic-not-consumer-driven]]: surfaced
-- now because two existing consumers (L8, T8) and four planned ones
-- (C4-C7) collectively pass the extraction threshold.
------------------------------------------------------------------------

record AlgebraClass : Set₁ where
  constructor mkAlgebraClass
  field
    Has-structure : Set → Set
    Hom-preserves :
      {M N : Set} →
      Has-structure M → Has-structure N → (M → N) → Set

open AlgebraClass public

------------------------------------------------------------------------
-- 1b. Trivial AlgebraClass: any set, any function.
--
-- The default / fallback for instances where bundling a rich
-- AlgebraClass adds friction without insight (e.g., the Lie-
-- fragment sketch at C7). Per [[feedback-coalgebraic-not-consumer-driven]]:
-- richer AlgebraClass per cell is future work; C1 publishes the
-- trivial instance so C8/C9 can typecheck against it.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤; tt)

trivial-AlgebraClass : AlgebraClass
trivial-AlgebraClass = mkAlgebraClass
  (λ _ → ⊤)
  (λ _ _ _ → ⊤)

------------------------------------------------------------------------
-- 2. FreeConstructionClass: lattice index for the classification.
--
-- Each linguistic / algebraic instance occupies exactly one cell of
-- the lattice. The enum is extensible — new classes can be added
-- as future arcs surface them.
--
-- Per [[user-rosetta-code-contrastive-pedagogy]]: the contrast
-- across cells IS the pedagogical content. The Rosetta-table
-- generator (C9) pairs cells via this enum.
------------------------------------------------------------------------

data FreeConstructionClass : Set where
  Free-monoid    : FreeConstructionClass   -- Lojban (C2)
  Free-F2-module : FreeConstructionClass   -- Toki Pona (C3)
  Free-cyclic    : FreeConstructionClass   -- Solresol (C4)
  Free-relation  : FreeConstructionClass   -- Kēlen (C5)
  Free-CCC       : FreeConstructionClass   -- Lambda calculus (C6)
  Free-Lie       : FreeConstructionClass   -- Invented Lie-fragment (C7)
  Free-other     : FreeConstructionClass   -- extensible

------------------------------------------------------------------------
-- 3. WitnessName: substrate-native naming for language witnesses.
--
-- Per [[feedback-minimize-stdlib-deps]]-strengthened: substrate-
-- native enum rather than Data.String. Each name corresponds to a
-- specific language instantiated in C2-C7.
------------------------------------------------------------------------

data WitnessName : Set where
  Lojban    : WitnessName
  TokiPona  : WitnessName
  Solresol  : WitnessName
  Kelen     : WitnessName
  Lambda    : WitnessName
  LieFrag   : WitnessName

------------------------------------------------------------------------
-- 4. LanguageWitness: packaged FreeOverBasis with classification.
--
-- A witness bundles:
--   * the witness name (for prose / table display)
--   * the basis and free carrier types
--   * the FreeOverBasis structure (with η)
--   * the FreeConstructionClass classification
--
-- Lives at Set₁ because it quantifies over Set-level basis and
-- carrier types. Each of C2-C7 produces one LanguageWitness; C8
-- bundles them into the classification lattice.
------------------------------------------------------------------------

record LanguageWitness : Set₁ where
  constructor mkWitness
  field
    name          : WitnessName
    Basis         : Set
    FreeCarrier   : Set
    structure     : FreeOverBasis Basis FreeCarrier
    class         : FreeConstructionClass

open LanguageWitness public

------------------------------------------------------------------------
-- 5. Classification helper: two witnesses are SAME-CLASS or
-- DIFFERENT-CLASS.
--
-- Used by C9 (RosettaTable) to dispatch on whether a pair occupies
-- the same lattice cell (refining within a free-construction class)
-- or different cells (cross-class Rosetta alignment).
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (Dec; yes; no)

same-class? : (w₁ w₂ : LanguageWitness) → Set
same-class? w₁ w₂ = class w₁ ≡ class w₂

------------------------------------------------------------------------
-- 6. Capstone for C1.
--
-- After this slice: the parent shape is named; the classification
-- enum is published; LanguageWitness packages instances. C2-C7
-- each produce one witness; C8 bundles; C9 generates Rosetta
-- tables. The universal property for each AlgebraClass lives in
-- the witness's own module — this parent does not enforce.
------------------------------------------------------------------------
