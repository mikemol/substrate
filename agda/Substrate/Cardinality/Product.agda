------------------------------------------------------------------------
-- Substrate.Cardinality.Product
--
-- Slice 16: product-cardinality infrastructure. Turns the catalog
-- claim "24 signatures = 6 orbits × 4 V_4-translates" from a
-- comment-level enumeration into a compositional theorem.
--
-- Primitives (re-exported from stdlib):
--
--   fin-product   : (Fin m × Fin n) ↔ Fin (m * n)
--     — `↔-sym` of stdlib's `Data.Fin.Properties.*↔×`. The
--       direction we want for composition (product → flat index).
--
--   cardinality-product :
--     A ↔ Fin m → B ↔ Fin n → (A × B) ↔ Fin (m * n)
--     — combine two cardinality witnesses via `_×-↔_` then
--       `fin-product`. Lets downstream cardinalities compose without
--       hand-coded `(Fin m × Fin n) ↔ Fin (m*n)` tables.
--
-- Composed cardinalities:
--
--   orbitkey×v4-↔-fin24 : (OrbitKey × V₄) ↔ Fin 24
--     — slice 15's `orbitkey-↔-fin6` and `v4-↔-fin4` composed.
--   totalspace-↔-fin24  : TotalSpace ↔ Fin 24
--     — TotalSpace = Σ OrbitKey Fiber with `Fiber _ = V₄`, so it
--       is definitionally OrbitKey × V₄.
--
-- Discipline notes (per
-- [[feedback-comments-dont-overclaim]] and
-- [[feedback-ordering-is-chirality-choice]]):
--
-- * The composed bijections inherit the ordering CONVENTIONS of
--   their components. `orbitkey×v4-↔-fin24` numbers via
--   stdlib `combine`, which is row-major in (m, n)-order — a
--   chirality choice, not a structural fact.
--
-- * Downstream modules SHOULD consume `orbitkey×v4-↔-fin24` and
--   `totalspace-↔-fin24` abstractly (as "a bijection exists") and
--   MUST NOT pattern-match on the specific Fin 24 indices. Agda
--   cannot machine-enforce that discipline from these
--   definitions; it lives at the import boundary.
--
-- See: Substrate.Cardinality (slice 15) — basic Fin n bijections.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cardinality.Product where

open import Level using (0ℓ)
open import Data.Nat using (ℕ; zero; suc; _*_)
open import Data.Fin using (Fin)
open import Data.Product using (_×_; _,_)
open import Data.Product.Function.NonDependent.Propositional
  using (_×-↔_)
open import Data.Fin.Properties using (*↔×)
open import Function.Bundles using (_↔_)
open import Function.Properties.Inverse using (↔-sym; ↔-trans)

open import Substrate.Groups.V4 using (V₄)
open import Substrate.Cocycles.V4Signature using (OrbitKey)
open import Substrate.Cardinality using (orbitkey-↔-fin6; v4-↔-fin4)

------------------------------------------------------------------------
-- Core primitive: (Fin m × Fin n) ↔ Fin (m * n).
--
-- Stdlib provides the reverse direction `*↔× : Fin (m * n) ↔ (Fin m
-- × Fin n)`; we want the forward direction for cardinality
-- composition, so we take its symmetry.
------------------------------------------------------------------------

fin-product : ∀ {m n} → (Fin m × Fin n) ↔ Fin (m * n)
fin-product = ↔-sym *↔×

------------------------------------------------------------------------
-- Cardinality composition helper.
------------------------------------------------------------------------

cardinality-product :
  ∀ {A B : Set} {m n : ℕ} →
  A ↔ Fin m → B ↔ Fin n → (A × B) ↔ Fin (m * n)
cardinality-product f g = ↔-trans (f ×-↔ g) fin-product

------------------------------------------------------------------------
-- OrbitKey × V₄ ↔ Fin 24.
------------------------------------------------------------------------

orbitkey×v4-↔-fin24 : (OrbitKey × V₄) ↔ Fin 24
orbitkey×v4-↔-fin24 = cardinality-product orbitkey-↔-fin6 v4-↔-fin4

------------------------------------------------------------------------
-- TotalSpace ↔ Fin 24.
--
-- TotalSpace = Σ OrbitKey Fiber where `Fiber _ = V₄`. Since the
-- family is constant, `Σ OrbitKey (λ _ → V₄)` is definitionally
-- `OrbitKey × V₄`, so the bijection is just
-- `orbitkey×v4-↔-fin24`. We re-export under the
-- TotalSpace-flavoured name for downstream clarity.
------------------------------------------------------------------------

open import Substrate.Cocycles.V4Signature.S4Iso using (TotalSpace)

totalspace-↔-fin24 : TotalSpace ↔ Fin 24
totalspace-↔-fin24 = orbitkey×v4-↔-fin24

------------------------------------------------------------------------
-- Notes
--
-- 1. The catalog's "24 = 6 × 4" claim is now machine-checked
--    compositionally: `orbitkey×v4-↔-fin24` is built by `↔-trans`
--    over `_×-↔_` of the two component bijections from slice 15,
--    then `fin-product`. No new hand enumeration.
--
-- 2. `cardinality-product` is the load-bearing combinator. Any
--    future product cardinality (e.g., `Axis × Bool ↔ Fin 8` via
--    `axis-↔-fin4` + a `Bool ↔ Fin 2`) reuses it.
--
-- 3. `totalspace-↔-fin24` works by definitional unfolding of
--    `Σ OrbitKey Fiber` to `OrbitKey × V₄`. If Fiber were ever
--    made non-constant (a per-orbit twist), this equality would
--    break — at that point a proper `Σ` enumeration would be
--    needed.
--
-- 4. Deferred (per slice 15's notes, downstream of this slice):
--    * Reserved ↔ Fin 8 (via Reserved ↔ Axis × Bool + cardinality-
--      product over Axis ↔ Fin 4 and a Bool ↔ Fin 2).
--    * Permutation ↔[≈] Fin 24 (via TotalSpace ↔ Permutation +
--      this slice's totalspace-↔-fin24, modulo pointwise ≈).
--    * Live ↔[≈] Fin 24 (via Live ≃ Permutation + above).
--    * Stab(anchor) ↔[≈] Fin 6 (via stab≃s₃ + |SFin.Permutation 3|
--      = 6; the latter is its own deferred enumeration).
--
-- 5. Cross-references:
--    * Slice 15: basic |X| = n bijections.
--    * Slice 4: TotalSpace ↔ Permutation.
--    * stdlib Data.Fin.Properties.*↔× — the underlying combine/
--      remQuot construction.
------------------------------------------------------------------------
