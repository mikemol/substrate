------------------------------------------------------------------------
-- Substrate.TokiPona.SemanticSpace
--
-- T1 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]]. Wraps Substrate.Algebra.F2.Vector
-- as the Toki Pona semantic carrier — the sister to Lojban's L2
-- (Coxeter Word wrapper) on the linear side of the arc.
--
-- A SemVec m is an F₂-vector of dimension m. Polysemy lands as
-- multi-hot activations: each nimi is a basis direction; combinations
-- via modifier-chains add directions via the F₂ XOR structure.
--
-- Per [[feedback-prefer-coxeter-backed]] the linear analog: prefer
-- existing F₂ infrastructure over re-rolling vector arithmetic. The
-- substrate's Substrate.Algebra.F2.Vector already supplies what we
-- need; this slice gives it Toki-Pona-facing names so the arc reads
-- locally without dipping into the F₂ generics.
--
-- Per [[feedback-categorical-name-first]]: "semantic vector space"
-- is the standard distributional-semantics name; F₂-VectorSpace is
-- the substrate-restricted realisation.
--
-- Per [[feedback-comments-dont-overclaim]]: F₂-vector semantics is
-- a deliberate fragment-only simplification; real distributional
-- Toki Pona semantics would want ℝ-valued vectors. Generalising
-- FreeLinearization to ℝ-modules is a separate arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.SemanticSpace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

-- Re-export the underlying F₂-Vector machinery publicly so consumers
-- can `open import Substrate.TokiPona.SemanticSpace` and get the
-- whole carrier surface in one shot.

open import Substrate.Algebra.F2.Vector public
  using (Vector; 𝟎ⱽ; _+ⱽ_; basis;
         +ⱽ-identityˡ; +ⱽ-identityʳ; +ⱽ-comm; +ⱽ-assoc;
         +ⱽ-self-inverse)

------------------------------------------------------------------------
-- 1. Linguistic alias: SemVec m IS the F₂-Vector of dimension m.
--
-- The Toki Pona semantic universe is parametric in dimension m so
-- T3 can choose m = number of nimi (one-hot basis) or m smaller
-- (projected feature semantics). The fragment uses one-hot.
------------------------------------------------------------------------

SemVec : ℕ → Set
SemVec m = Vector m

------------------------------------------------------------------------
-- 2. Semantic empty / null vector (identity for merge).
------------------------------------------------------------------------

∅ : ∀ {m} → SemVec m
∅ = 𝟎ⱽ

------------------------------------------------------------------------
-- 3. Semantic merge (XOR / F₂ vector addition).
--
-- The fragment's compositional merge: "soweli lili" merges the
-- semantic vectors of soweli and lili. F₂ structure means double-
-- activation cancels (self-inverse), which is fine for the polysemy-
-- direction reading at this level.
------------------------------------------------------------------------

infixl 6 _⊕_

_⊕_ : ∀ {m} → SemVec m → SemVec m → SemVec m
_⊕_ = _+ⱽ_

------------------------------------------------------------------------
-- 4. The abelian-group laws for SemVec under _⊕_.
--
-- Per [[feedback-grothendieck-coherence-rule]]: these are the laws
-- T8 (LinearAlgebra) consumes to discharge the FreeLinearization
-- universal property. F₂'s characteristic-2 makes the negation
-- identity (self-inverse), so SemVec is in particular a vector
-- space, not merely an abelian monoid.
------------------------------------------------------------------------

⊕-identityˡ : ∀ {m} (v : SemVec m) → (∅ ⊕ v) ≡ v
⊕-identityˡ = +ⱽ-identityˡ

⊕-identityʳ : ∀ {m} (v : SemVec m) → (v ⊕ ∅) ≡ v
⊕-identityʳ = +ⱽ-identityʳ

⊕-comm : ∀ {m} (u v : SemVec m) → (u ⊕ v) ≡ (v ⊕ u)
⊕-comm = +ⱽ-comm

⊕-assoc :
  ∀ {m} (u v w : SemVec m) →
  ((u ⊕ v) ⊕ w) ≡ (u ⊕ (v ⊕ w))
⊕-assoc = +ⱽ-assoc

⊕-self-inverse : ∀ {m} (v : SemVec m) → (v ⊕ v) ≡ ∅
⊕-self-inverse = +ⱽ-self-inverse
