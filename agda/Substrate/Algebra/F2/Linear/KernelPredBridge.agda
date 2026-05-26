------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.KernelPredBridge
--
-- Bridge primitives between a F₂-vector subspace expressed as
--   (a) a Pred-tuple of component-equalities Pi(w) ≡ 𝟘,
--   (b) the kernel of a selector linear map S : Linear n p,
-- given per-component "selector-lookup-i" lemmas
--   lookup (apply S w) i ≡ Pi(w).
--
-- The two micro-lemmas exposed here compose with `≡-from-lookup` at
-- the call site to produce full `pred→kernel` and `kernel→pred`
-- bridges. The per-site code reduces to one line per index plus a
-- single `≡-from-lookup` fold.
--
-- Discovered via typed-holes on ChiralityAxis ↔ V4Plane after the
-- Foundation.Eq trio extraction arc; the post-trio bodies surfaced
-- a substrate-level discipline pattern that this module names.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.KernelPredBridge where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Vec using (lookup)
open import Substrate.Foundation.Eq
  using (_≡_; sym; trans; cong; cong-trans; sym-trans; trans-sym)

open import Substrate.Algebra.F2 using (F₂; 𝟘)
open import Substrate.Algebra.F2.Vector using (Vector; 𝟎ⱽ; lookup-𝟎)
open import Substrate.Algebra.F2.Linear using (Linear; apply)

------------------------------------------------------------------------
-- pred-at-i → kernel-at-i.
--
-- Given:
--   sl  : lookup (apply S w) i ≡ pi-of-w     [per-component selector lemma]
--   pi  : pi-of-w ≡ 𝟘                        [the i-th predicate clause]
--
-- Produce the kernel-component witness
--   lookup (apply S w) i ≡ lookup (𝟎ⱽ {p}) i
--
-- which `≡-from-lookup` then folds across i ∈ Fin p to give the full
-- kernel equation apply S w ≡ 𝟎ⱽ.
------------------------------------------------------------------------

pred-at-i→kernel-at-i :
  ∀ {n p} (S : Linear n p) (w : Vector n) (i : Fin p) {pi-of-w : F₂} →
  lookup (apply S w) i ≡ pi-of-w →
  pi-of-w ≡ 𝟘 →
  lookup (apply S w) i ≡ lookup (𝟎ⱽ {p}) i
pred-at-i→kernel-at-i _ _ i sl pi =
  trans-sym (trans sl pi) (lookup-𝟎 i)

------------------------------------------------------------------------
-- kernel-at-i → pred-at-i.
--
-- Given:
--   sl   : lookup (apply S w) i ≡ pi-of-w    [per-component selector lemma]
--   ker  : apply S w ≡ 𝟎ⱽ                    [in-kernel witness]
--
-- Produce the i-th predicate clause
--   pi-of-w ≡ 𝟘.
--
-- The call site bundles N invocations (one per index) into the Pred tuple.
------------------------------------------------------------------------

kernel-at-i→pred-at-i :
  ∀ {n p} (S : Linear n p) (w : Vector n) (i : Fin p) {pi-of-w : F₂} →
  lookup (apply S w) i ≡ pi-of-w →
  apply S w ≡ 𝟎ⱽ →
  pi-of-w ≡ 𝟘
kernel-at-i→pred-at-i _ _ i sl ker =
  sym-trans sl (cong-trans (λ x → lookup x i) ker (lookup-𝟎 i))
