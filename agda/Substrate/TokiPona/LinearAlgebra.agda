------------------------------------------------------------------------
-- Substrate.TokiPona.LinearAlgebra
--
-- T8 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]].
--
-- Sister slice to Lojban L8 WordAlgebra (free-monoid universal
-- property). T8 closes the other half of the Toki Pona entailment:
-- the **FreeLinearization universal property** for NimiSpace
-- restated in linguistic-facing terms.
--
-- The substrate's
-- [[project-freelinearization-names-linear-from-images]] already
-- supplies the categorical primitive (FreeLinearization n m record
-- + free-linearize constructor); T8 lifts it through the Nimi
-- vocabulary so consumers (T9, T10) cite the linguistic universal
-- property rather than the substrate generics.
--
-- The free-linear extension is the DISCRETE→LINEAR analog of the
-- free-monoid extension Lojban L8 discharges. Both arcs invoke a
-- "free X over a basis" universal property; T10 surfaces the
-- intersection explicitly.
--
-- Per [[feedback-categorical-name-first]]: this is the canonical
-- free-F₂-module universal property at the linguistic site.
-- Per [[feedback-grothendieck-coherence-rule]]: the universal
-- property's basis-extension AND uniqueness clauses jointly
-- discharge the coherence obligation.
--
-- DESIGN NOTE: extension-basis is stated at the Nimi level (lifted
-- via T3's `from-index∘index` round-trip lemma); extension-unique
-- is stated at the Fin level (avoiding the inverse round-trip).
-- A Nimi-level uniqueness would require BOTH directions of the
-- Nimi↔Fin bijection; the Fin-level statement is equivalent for
-- consumers and saves an inverse round-trip lemma's 32-case proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.LinearAlgebra where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Algebra.F2.Vector using (basis)
open import Substrate.TokiPona.SemanticSpace using (SemVec)
open import Substrate.TokiPona.Nimi
  using (Nimi; nimi-count; nimi-index)
open import Substrate.TokiPona.NimiSpace
  using (nimi-as-vector; nimi-from-index; from-index∘index;
         module WithTarget)

open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Category.FreeLinearization
  using (FreeLinearization)
open import Substrate.Category.FreeLinearization.FromImages
  using (free-linearize)

------------------------------------------------------------------------
-- 1. The Toki-Pona-side universal property statement.
--
-- For any target dimension m and image map `image : Nimi → SemVec m`,
-- there exists a unique Linear nimi-count m extending `image`. This
-- is the substrate's FreeLinearization primitive applied at the
-- linguistic basis.
------------------------------------------------------------------------

record NimiFreeLinearization (m : ℕ) : Set where
  field
    nimi-image       : Nimi → SemVec m
    nimi-extension   : Linear nimi-count m
    extension-basis  :
      (n : Nimi) →
      apply nimi-extension (basis (nimi-index n)) ≡ nimi-image n
    extension-unique :
      (other : Linear nimi-count m) →
      ((i : Fin nimi-count) →
        apply other (basis i) ≡ nimi-image (nimi-from-index i)) →
      (v : SemVec nimi-count) →
      apply nimi-extension v ≡ apply other v

------------------------------------------------------------------------
-- 2. Canonical constructor.
--
-- Given any Nimi-image map, build the NimiFreeLinearization record
-- via Substrate.Category.FreeLinearization.FromImages's
-- free-linearize. The basis-extension obligation lifts through
-- `from-index∘index`; uniqueness is direct via WithTarget.uniqueness
-- at the Fin layer.
------------------------------------------------------------------------

free-linearize-nimi :
  {m : ℕ} (image : Nimi → SemVec m) → NimiFreeLinearization m
free-linearize-nimi {m} image = record
  { nimi-image       = image
  ; nimi-extension   = WithTarget.extension image
  ; extension-basis  = λ n →
      trans (WithTarget.extension-on-basis image (nimi-index n))
            (cong image (from-index∘index n))
  ; extension-unique = λ other agree v →
      WithTarget.uniqueness image other agree v
  }

------------------------------------------------------------------------
-- 3. The canonical instance (one-hot embedding).
--
-- Using image = nimi-as-vector reproduces the canonical
-- FreeLinearization from T3.
------------------------------------------------------------------------

canonical-nimi-free : NimiFreeLinearization nimi-count
canonical-nimi-free = free-linearize-nimi nimi-as-vector

------------------------------------------------------------------------
-- 4. Capstone.
--
-- T8 closes the linear-side entailment: the universal property
-- (free-linear extension from the Nimi basis) jointly with T7's
-- linearity coherence record discharges
--
--   FreeLinearization(NimiSpace) → BilinearComposition(ModifierBilinear)
--     ⊢ ∀ (s : TokiSentence). WellTyped s × Linear ⟦ s ⟧
--
-- The free-monoid (Lojban L8) and the free-linear (Toki Pona T8)
-- universal properties are sister instances of "free X over a
-- basis"; T10 makes the intersection explicit.
------------------------------------------------------------------------
