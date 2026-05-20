------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.Bijection
--
-- F₂-linear bijection primitive: a record bundling two F₂-linear maps
-- (forward + backward) with two-sided pointwise-inverse witnesses.
-- The categorical "isomorphism in F₂-Vect."
--
-- Foundational for the GaugeTorsor work
-- ([[multi-route-equivariance-recovery]] + the universal-property
-- unification arc): the space of F₂-linear bijections between two
-- specific n-dim and m-dim spaces is precisely the orbit of any
-- particular bijection under the GL(n, F₂)-action.
--
-- Generalises Substrate.Algebra.GL3F2 (which is the n=m=3 endomorphism
-- case). GL3F2 could be refactored to layer on top of this; deferred
-- as a separate follow-on to keep this slice minimal.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "F₂-linear bijection" IS the standard categorical name; the
-- universal property is "two-sided inverse exists" (encoded as
-- forward∘backward = id and backward∘forward = id pointwise).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.Bijection where

open import Data.Nat using (ℕ)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear
  using (Linear; id-L; _∘L_; apply)

------------------------------------------------------------------------
-- 1. The bijection record.
--
-- Bundles forward + backward + the two pointwise-inverse witnesses.
-- Both forward and backward inherit their F₂-linearity from their
-- Linear records; no separate "inverse-is-linear" obligation is
-- needed at the record level (the user supplies the backward
-- direction explicitly).
------------------------------------------------------------------------

record LinearBijection (n m : ℕ) : Set where
  constructor mkLinearBijection
  field
    forward     : Linear n m
    backward    : Linear m n
    forward-back-id : (v : Vector n) → apply backward (apply forward v) ≡ v
    back-forward-id : (v : Vector m) → apply forward (apply backward v) ≡ v

open LinearBijection public

------------------------------------------------------------------------
-- 2. Identity bijection.
------------------------------------------------------------------------

id-LB : ∀ {n} → LinearBijection n n
id-LB = mkLinearBijection id-L id-L (λ _ → refl) (λ _ → refl)

------------------------------------------------------------------------
-- 3. Inverse: swap forward and backward.
------------------------------------------------------------------------

_⁻¹LB : ∀ {n m} → LinearBijection n m → LinearBijection m n
β ⁻¹LB = mkLinearBijection (backward β) (forward β)
                           (back-forward-id β) (forward-back-id β)

------------------------------------------------------------------------
-- 4. Composition: (γ ∘LB β) = γ after β. Inverse is built from the
-- per-component inverses in reverse order.
------------------------------------------------------------------------

infixr 9 _∘LB_

_∘LB_ : ∀ {n m k} → LinearBijection m k → LinearBijection n m → LinearBijection n k
γ ∘LB β = mkLinearBijection
  (forward γ ∘L forward β)
  (backward β ∘L backward γ)
  (λ v →
    trans (cong (apply (backward β)) (forward-back-id γ (apply (forward β) v)))
          (forward-back-id β v))
  (λ v →
    trans (cong (apply (forward γ)) (back-forward-id β (apply (backward γ) v)))
          (back-forward-id γ v))

------------------------------------------------------------------------
-- 5. Bijective-application: apply the forward direction (sugar).
------------------------------------------------------------------------

applyLB : ∀ {n m} → LinearBijection n m → Vector n → Vector m
applyLB β = apply (forward β)

------------------------------------------------------------------------
-- 6. Composition with the inverse gives identity (right + left).
-- These are direct projections of the inverse witnesses; included as
-- named lemmas for downstream readability.
------------------------------------------------------------------------

inv-left :
  ∀ {n m} (β : LinearBijection n m) (v : Vector n) →
  applyLB (β ⁻¹LB ∘LB β) v ≡ v
inv-left β v = forward-back-id β v

inv-right :
  ∀ {n m} (β : LinearBijection n m) (v : Vector m) →
  applyLB (β ∘LB β ⁻¹LB) v ≡ v
inv-right β v = back-forward-id β v
