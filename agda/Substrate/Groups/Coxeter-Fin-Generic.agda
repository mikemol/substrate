------------------------------------------------------------------------
-- Substrate.Groups.Coxeter-Fin-Generic
--
-- Parametric module for the Zₙ-Coxeter ↔ Fin n chain: bijection +
-- action-of-a + HasOrderPerm.
--
-- Consolidates the Z3-Coxeter-Fin / Z4-Coxeter-Fin / Z5-Coxeter-Fin
-- per-n boilerplate: each instance becomes a thin record-pack + the
-- generic produces the σₙ-correspondence and HasOrderPerm uniformly.
--
-- Models on Substrate.Groups.Zn-x-FreeCyclic's consolidation pattern
-- (parametric-over-Zₙ-data, producing the consolidated structure).
--
-- Per [[feedback-roll-our-own-via-word-algebra]] +
-- [[feedback-expose-generator-not-orbit]]: the Zₙ × Fin n boilerplate
-- was an orbit of "any Zₙ instance gets the same chain"; this module
-- IS that chain, parametric over the Zₙ pieces.
--
-- Inputs (caller-supplied per-Zₙ):
--   * The Coxeter Word algebra (Gen, the rotation generator `a`,
--     Canonical predicate, insert / insert-canonical).
--   * The bijection (canonical-to-Fin, Fin-to-canonical).
--   * The σₙ permutation on Fin n (typically from
--     Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycleₙ).
--   * action-of-a-is-σₙ (correspondence between insert-a and σₙ).
--   * σₙ-aⁿ=ε (HasOrderPerm witness at the Fin level).
--
-- Output (derived):
--   * σₙ-HasOrderPerm — the order-n property of σₙ at Fin n level,
--     under the chain's canonical public name. NO per-Zₙ n-case
--     enumeration at the generic level.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Groups.Coxeter.Word using (Word)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation using (HasOrderPerm)

module Substrate.Groups.Coxeter-Fin-Generic
  -- Per-Zₙ Coxeter data:
  (n        : ℕ)
  (Gen      : Set)
  (a        : Gen)
  (Canonical : Word Gen → Set)
  (insert   : Gen → Word Gen → Word Gen)
  (insert-canonical :
    (g : Gen) {w : Word Gen} → Canonical w → Canonical (insert g w))

  -- The bijection between (canonical Words) and Fin n.
  -- These are still per-Zₙ n-case enumerations — the unavoidable
  -- "named-constructor world ↔ Fin world" connection. Each Zₙ instance
  -- supplies these directly (n cases each).
  (canonical-to-Fin : ∀ {w : Word Gen} → Canonical w → Fin n)
  (Fin-to-canonical : Fin n → Σ (Word Gen) Canonical)

  -- The σₙ permutation on Fin n (typically already-imported from
  -- Cycleₙ). The caller passes it in rather than re-defining.
  (σₙ : Fin n → Fin n)

  -- The action correspondence: applying `insert a` at the canonical
  -- level matches σₙ at the Fin level. Per-Zₙ n-case enumeration
  -- (unavoidable: connects insert-canonical's per-shape behaviour to
  -- σₙ's per-position behaviour).
  (action-of-a-is-σₙ :
    ∀ {w} (c : Canonical w) →
    canonical-to-Fin (insert-canonical a c) ≡ σₙ (canonical-to-Fin c))

  -- The Coxeter aⁿ = ε relation lifted to the bijection: iterating
  -- σₙ n times brings each Fin position home. This is `HasOrderPerm`
  -- by definition.
  (σₙ-aⁿ=ε : HasOrderPerm σₙ n)
  where

------------------------------------------------------------------------
-- Derived: HasOrderPerm for σₙ.
--
-- The generic re-exports the order witness with the canonical name
-- pattern used by per-Zₙ instances: `σₙ-HasOrderPerm-from-Zₙ-Coxeter`.
-- Concrete instances `open` this module with their n + bijection
-- + σₙ + action-of-a-is-σₙ; the order witness is supplied (typically
-- a single n-case enumeration at the Fin level, NOT a per-Zₙ
-- enumeration).
------------------------------------------------------------------------

σₙ-HasOrderPerm : HasOrderPerm σₙ n
σₙ-HasOrderPerm = σₙ-aⁿ=ε

------------------------------------------------------------------------
-- Future structural strengthening (substantive next arc, not a
-- slice-budget follow-on):
--
-- A truly generative `cyclic-suc-HasOrderPerm : ∀ {n} → HasOrderPerm
-- (cyclic-suc {n}) (suc n)` would eliminate the σₙ-HasOrderPerm
-- per-position enumeration that currently lives in
-- Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycleₙ
-- (n ∈ {3, 4, 5}). Each instance presently re-exports its Cycleₙ's
-- witness under the chain's canonical name; this dedupes the witness
-- between the Cycle and Coxeter-Fin layers but leaves it as an
-- enumeration at the Cycle layer.
--
-- The full structural derivation needs:
--   * `cyclic-suc : ∀ {n} → Fin (suc n) → Fin (suc n)` (defined via
--     `fromℕ<` + `mod-suc-bound`).
--   * `mod-suc-id : a < suc b → a mod-suc b ≡ a` (mod fixes below).
--   * `mod-suc-periodic : (a + suc b) mod-suc b ≡ a mod-suc b`
--     (period = suc b).
--   * Roundtrip lemmas in Substrate.Foundation.Fin.Properties
--     (toℕ-fromℕ<, toℕ-injective, toℕ-bound — already landed).
--
-- The mod-suc-id / mod-suc-periodic proofs require careful with-
-- abstraction over the mod-suc clauses; that's a separate Mod arc.
------------------------------------------------------------------------
