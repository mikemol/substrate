------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.FromImages.Permutation
--
-- Universal-property combinators for linear maps built from
-- permutations of basis vectors.
--
-- When the images of `linear-from-images` are themselves basis vectors
-- (= the function is `basis ∘ σ` for some `σ : Fin n → Fin n`), the
-- resulting Linear map IS the "basis permutation" linear map. Its
-- iterates correspond to iterates of `σ` — in particular, if `σ` is
-- an involution then so is `apply (linear-from-images (basis ∘ σ))`
-- at the basis-vector level.
--
-- This module names the universal property at the basis level. The
-- lift to "involution on all vectors" composes with M-3.5's
-- `linear-extensionality` (one line at the call site).
--
-- Per [[feedback-universal-property-discipline]]: this combinator
-- saves callers from re-deriving the three-step trans-cong chain
-- (apply L on inner, apply L on outer, cong basis on σ-involution)
-- for every order-2 basis-permutation. Sites currently using the
-- inlined chain: HodgeStar.hodge-involution-basis.
--
-- Per [[feedback-categorical-name-first]]: "involution on basis from
-- σ² = id" is the universal property the inlined trans-chain instantiates;
-- this module names it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.FromImages.Permutation where

open import Data.Fin using (Fin)
open import Relation.Binary.PropositionalEquality
  using (_≡_; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)

------------------------------------------------------------------------
-- N-0: basis-permutation-Linear — the linear map induced by a basis
-- permutation σ : Fin n → Fin n.
--
-- The natural categorical object: any `σ : Fin n → Fin n` lifts to a
-- linear endomorphism of Vector n that permutes basis vectors as σ
-- specifies. This is the universal "linear map from a basis function."
--
-- Definitionally just `linear-from-images (basis ∘ σ)`; the alias names
-- the construction at the call site.
--
-- After this definition:
--   * hodge-star = basis-permutation-Linear complement
--   * (future) cyclic permutations, transposition, sign-changes give
--     other basis-permutation-Linear instances with order-k structure.
------------------------------------------------------------------------

basis-permutation-Linear : ∀ {n} → (Fin n → Fin n) → Linear n n
basis-permutation-Linear σ = linear-from-images (λ j → basis (σ j))

-- The defining property: applying the basis-permutation-Linear at σ
-- to basis i gives basis (σ i). Direct restatement of
-- apply-linear-from-images-basis specialised to basis-images.
apply-basis-permutation-Linear :
  ∀ {n} (σ : Fin n → Fin n) (i : Fin n) →
  apply (basis-permutation-Linear σ) (basis i) ≡ basis (σ i)
apply-basis-permutation-Linear σ i =
  apply-linear-from-images-basis (λ j → basis (σ j)) i

------------------------------------------------------------------------
-- N-1: basis-permutation-involution — at basis vectors, iterating the
-- basis-permutation linear map twice agrees with σ ∘ σ on the index.
--
-- For σ : Fin n → Fin n with σ² = id, the linear map
--   L = linear-from-images (basis ∘ σ)
-- satisfies `apply L (apply L (basis i)) ≡ basis i` for every i.
--
-- Chain (each step is one universal-property lemma):
--   apply L (apply L (basis i))
--     ≡ apply L (basis (σ i))             [apply-basis on inner]
--     ≡ basis (σ (σ i))                   [apply-basis on outer]
--     ≡ basis i                           [cong basis ∘ σ-invol]
--
-- The combinator absorbs the three-step trans chain that callers
-- otherwise inline.
------------------------------------------------------------------------

basis-permutation-involution :
  ∀ {n} (σ : Fin n → Fin n) →
  ((i : Fin n) → σ (σ i) ≡ i) →
  (i : Fin n) →
  apply (linear-from-images (λ j → basis (σ j)))
        (apply (linear-from-images (λ j → basis (σ j))) (basis i))
    ≡ basis i
basis-permutation-involution σ σ-invol i =
  trans (cong (apply (linear-from-images (λ j → basis (σ j))))
              (apply-linear-from-images-basis (λ j → basis (σ j)) i))
  (trans (apply-linear-from-images-basis (λ j → basis (σ j)) (σ i))
         (cong basis (σ-invol i)))

------------------------------------------------------------------------
-- N-2: Capstone — universal-property combinator landed.
--
-- After this slice:
--
--   * basis-permutation-involution — the named universal property
--     "if σ² = id on Fin n, then linear-from-images (basis ∘ σ) squares
--     to identity at basis vectors."
--
-- Slice 2 (next): retrofit HodgeStar.hodge-involution-basis to apply
-- this combinator at σ = complement.
--
-- Slice 3 (planned): name the construction itself —
-- `basis-permutation-Linear σ = linear-from-images (basis ∘ σ)` —
-- as a substrate primitive, surfacing the categorical "linear map
-- induced by a basis permutation" object directly.
--
-- Per [[project-torsion-element-universal]]: this combinator is the
-- order-2 case of a general "basis-permutation iterates as σ^k"
-- pattern. Order-k generalization (σ^k = id ⇒ Lᵏ = id at basis) is a
-- natural follow-on.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: the
-- combinator names a universal property; sites that re-derive the
-- chain become one-line applications.
------------------------------------------------------------------------
