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
open import Data.Nat using (ℕ; zero; suc)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal using (linear-extensionality)
open import Substrate.Category.Coalgebra.FiniteOrder using (iterate; HasOrder)

------------------------------------------------------------------------
-- N-(-1): σ-iterate + HasOrderPerm — foundational data for order-k
-- basis-permutation work.
--
-- σ-iterate k σ = σ ∘ σ ∘ ⋯ ∘ σ  (k times).
-- HasOrderPerm σ k = ∀ i → σ-iterate k σ i ≡ i  (pointwise σ^k = id).
--
-- Slice-1 of the order-k arc. These types let later slices state
-- "if σ has order k as a permutation, then basis-permutation-Linear σ
-- has order k as a Linear" without re-deriving iteration semantics.
--
-- The order-2 special case (σ ∘ σ ≡ id pointwise) is what
-- complement-involution witnesses; basis-permutation-involution
-- (N-1 below) is the order-k = 2 specialization of the future
-- basis-permutation-order-k combinator.
------------------------------------------------------------------------

σ-iterate : ∀ {n} → ℕ → (Fin n → Fin n) → (Fin n → Fin n)
σ-iterate zero    σ = λ i → i
σ-iterate (suc k) σ = λ i → σ (σ-iterate k σ i)

HasOrderPerm : ∀ {n} → (Fin n → Fin n) → ℕ → Set
HasOrderPerm σ k = ∀ i → σ-iterate k σ i ≡ i

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
-- N-0.5: Composition law at the basis level.
--
-- `basis-permutation-Linear (σ ∘ τ)` agrees with `basis-permutation-
-- Linear σ ∘L basis-permutation-Linear τ` on every basis vector.
-- The composition of basis permutations IS the composition of the
-- induced linear maps — at least at the basis level.
--
-- Combined with linear-extensionality, this gives the full-vector
-- agreement; deferred to the call site for now (extensionality is
-- one line).
--
-- Both sides reduce to `basis (σ (τ i))`:
--   LHS: apply (basis-permutation-Linear (σ ∘ τ)) (basis i)
--          ≡ basis ((σ ∘ τ) i) = basis (σ (τ i))  [apply-basis]
--   RHS: apply (basis-permutation-Linear σ ∘L basis-permutation-Linear τ) (basis i)
--          = apply L-σ (apply L-τ (basis i))
--          ≡ apply L-σ (basis (τ i))                [apply-basis on τ]
--          ≡ basis (σ (τ i))                        [apply-basis on σ]
------------------------------------------------------------------------

basis-permutation-compose-at-basis :
  ∀ {n} (σ τ : Fin n → Fin n) (i : Fin n) →
  apply (basis-permutation-Linear (λ x → σ (τ x))) (basis i)
    ≡ apply (basis-permutation-Linear σ ∘L basis-permutation-Linear τ) (basis i)
basis-permutation-compose-at-basis σ τ i =
  trans (apply-basis-permutation-Linear (λ x → σ (τ x)) i)
  (trans (sym (apply-basis-permutation-Linear σ (τ i)))
         (sym (cong (apply (basis-permutation-Linear σ))
                    (apply-basis-permutation-Linear τ i))))

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
-- N-1.5: iterate-on-basis — iteration of basis-permutation-Linear at a
-- basis vector tracks σ-iterate at the index.
--
--   iterate k (apply (basis-permutation-Linear σ)) (basis i)
--     ≡ basis (σ-iterate k σ i)
--
-- Induction on k:
--   * k = 0: both sides reduce to basis i.
--   * k = suc k': apply-basis-permutation-Linear + IH chain.
--
-- This is THE structural identity that makes order-k generalization
-- work: applying L k times at a basis vector permutes the index by
-- σ^k.
------------------------------------------------------------------------

iterate-on-basis :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) (i : Fin n) →
  iterate k (apply (basis-permutation-Linear σ)) (basis i)
    ≡ basis (σ-iterate k σ i)
iterate-on-basis σ zero    i = refl
iterate-on-basis σ (suc k) i =
  trans (cong (apply (basis-permutation-Linear σ)) (iterate-on-basis σ k i))
        (apply-basis-permutation-Linear σ (σ-iterate k σ i))

------------------------------------------------------------------------
-- N-1.6: basis-permutation-order-k — order-k generalization at the
-- basis level. The order-k analog of basis-permutation-involution.
--
-- If HasOrderPerm σ k (= σ^k ≡ id pointwise on Fin n), then iterating
-- apply (basis-permutation-Linear σ) k times at any basis vector
-- returns the same basis vector.
--
-- Composition: trans iterate-on-basis with cong basis on the order
-- witness. The "FLT-for-dimensional-spaces" identity at the basis
-- level for any basis-permutation-Linear.
------------------------------------------------------------------------

basis-permutation-order-k :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) →
  HasOrderPerm σ k →
  (i : Fin n) →
  iterate k (apply (basis-permutation-Linear σ)) (basis i) ≡ basis i
basis-permutation-order-k σ k order-witness i =
  trans (iterate-on-basis σ k i) (cong basis (order-witness i))

------------------------------------------------------------------------
-- N-1.7: L-iterate + iterate-apply-as-L-iterate — package
-- function-level iteration as Linear-level composition.
--
-- L-iterate k L = L ∘L L ∘L ... ∘L L (k times, with id-L at k=0).
-- Then `iterate k (apply L) v ≡ apply (L-iterate k L) v` definitionally
-- at each step (apply (L ∘L M) = apply L ∘ apply M; apply id-L = id).
--
-- This is the "iteration commutes with apply" universal property —
-- the structural bridge between function-iteration (used by HasOrder)
-- and Linear-iteration (where linear-extensionality applies).
------------------------------------------------------------------------

L-iterate : ∀ {n} → ℕ → Linear n n → Linear n n
L-iterate zero    L = id-L
L-iterate (suc k) L = L ∘L L-iterate k L

iterate-apply-as-L-iterate :
  ∀ {n} (L : Linear n n) (k : ℕ) (v : Vector n) →
  iterate k (apply L) v ≡ apply (L-iterate k L) v
iterate-apply-as-L-iterate L zero    v = refl
iterate-apply-as-L-iterate L (suc k) v =
  cong (apply L) (iterate-apply-as-L-iterate L k v)

------------------------------------------------------------------------
-- N-1.8: HasOrder-from-perm — lift permutation order to Linear order.
--
-- Given HasOrderPerm σ k, the linear endomap apply (basis-permutation-
-- Linear σ) has HasOrder k. This is the structural bridge from
-- "permutation σ has order k as a function on Fin n" to "the induced
-- linear map has order k as an endomap on Vector n."
--
-- Composition (per the order-k arc):
--   1. basis-permutation-order-k gives basis-level agreement of
--      iterate k (apply L) (basis i) with basis i.
--   2. iterate-apply-as-L-iterate rephrases iterate k (apply L) as
--      apply (L-iterate k L).
--   3. linear-extensionality lifts the basis-level agreement between
--      L-iterate k L and id-L to all vectors.
--   4. iterate-apply-as-L-iterate (the other way) rephrases back to
--      iterate k (apply L) v ≡ v.
--
-- The "FLT-for-dimensional-spaces" lift, made structural and reusable.
------------------------------------------------------------------------

HasOrder-from-perm :
  ∀ {n} (σ : Fin n → Fin n) (k : ℕ) →
  HasOrderPerm σ k →
  HasOrder (apply (basis-permutation-Linear σ)) k
HasOrder-from-perm {n} σ k order-witness v =
  trans (iterate-apply-as-L-iterate (basis-permutation-Linear σ) k v)
        (linear-extensionality
          (L-iterate k (basis-permutation-Linear σ))
          id-L
          basis-agreement
          v)
  where
    L = basis-permutation-Linear σ

    basis-agreement :
      (i : Fin n) → apply (L-iterate k L) (basis i) ≡ apply id-L (basis i)
    basis-agreement i =
      trans (sym (iterate-apply-as-L-iterate L k (basis i)))
            (basis-permutation-order-k σ k order-witness i)

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
