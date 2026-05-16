------------------------------------------------------------------------
-- Substrate.Cardinality.Product
--
-- Slice 16: product-cardinality infrastructure. Houses every
-- cardinality bijection whose source type is a product (or
-- definitionally a product). Built on top of slice 15's atomic
-- enumerations via a single combinator.
--
-- Primitives:
--
--   fin-product   : (Fin m × Fin n) ↔ Fin (m * n)
--     — `↔-sym` of stdlib's `Data.Fin.Properties.*↔×`. The
--       direction we want for composition (product → flat index).
--
--   cardinality-product :
--     A ↔ Fin m → B ↔ Fin n → (A × B) ↔ Fin (m * n)
--     — combine two cardinality witnesses via `_×-↔_` then
--       `fin-product`. The load-bearing combinator: every product
--       cardinality below is one of its orbit elements.
--
-- Product cardinalities (orbit elements of `cardinality-product`):
--
--   orbitkey-↔-fin6      : OrbitKey ↔ Fin 6   = Pairing × Chirality
--   axis×bool-↔-fin8     : (Axis × Bool) ↔ Fin 8
--   orbitkey×v4-↔-fin24  : (OrbitKey × V₄) ↔ Fin 24
--   totalspace-↔-fin24   : TotalSpace ↔ Fin 24
--     — TotalSpace = Σ OrbitKey Fiber with `Fiber _ = V₄`, so it
--       is definitionally OrbitKey × V₄.
--
-- Per [[feedback-expose-generator-not-orbit]], the generator
-- (`cardinality-product`) is the right abstraction; each named
-- product cardinality is a one-liner orbit element rather than a
-- hand enumeration.
--
-- Discipline notes (per
-- [[feedback-comments-dont-overclaim]] and
-- [[feedback-ordering-is-chirality-choice]]):
--
-- * The composed bijections inherit the ordering CONVENTIONS of
--   their components. Numbering via stdlib `combine` is row-major
--   in (m, n)-order — a chirality choice, not a structural fact.
--
-- * Downstream modules SHOULD consume the composed bijections
--   abstractly (as "a bijection exists") and MUST NOT pattern-match
--   on the specific Fin n indices. Agda cannot machine-enforce that
--   discipline from these definitions; it lives at the import
--   boundary.
--
-- See: Substrate.Cardinality (slice 15) — atomic Fin n bijections.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cardinality.Product where

open import Level using (0ℓ)
open import Data.Bool using (Bool)
open import Data.Nat using (ℕ; zero; suc; _*_)
open import Data.Fin using (Fin)
open import Data.Product using (_×_; _,_)
open import Data.Product.Function.NonDependent.Propositional
  using (_×-↔_)
open import Data.Fin.Properties using (*↔×)
open import Function.Bundles using (_↔_)
open import Function.Properties.Inverse using (↔-sym; ↔-trans)

open import Substrate.Axes using (Axis)
open import Substrate.Groups.V4 using (V₄)
open import Substrate.Cocycles.V4Signature using (OrbitKey)
open import Substrate.Cardinality
  using (axis-↔-fin4; v4-↔-fin4; pairing-↔-fin3;
         chirality-↔-fin2; bool-↔-fin2)

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
-- OrbitKey ↔ Fin 6  (= Pairing × Chirality, definitionally).
--
-- OrbitKey is defined in Substrate.Cocycles.V4Signature as
-- `Pairing × Chirality`, so this is a direct product composition.
------------------------------------------------------------------------

orbitkey-↔-fin6 : OrbitKey ↔ Fin 6
orbitkey-↔-fin6 = cardinality-product pairing-↔-fin3 chirality-↔-fin2

------------------------------------------------------------------------
-- Axis × Bool ↔ Fin 8.
------------------------------------------------------------------------

axis×bool-↔-fin8 : (Axis × Bool) ↔ Fin 8
axis×bool-↔-fin8 = cardinality-product axis-↔-fin4 bool-↔-fin2

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
-- 1. Every product cardinality in the file is a one-liner orbit
--    element of `cardinality-product`. The catalog's numerical
--    claims (|OrbitKey| = 6, |Axis × Bool| = 8, |TotalSpace| = 24)
--    are machine-checked compositionally, not by hand enumeration.
--
-- 2. `totalspace-↔-fin24` works by definitional unfolding of
--    `Σ OrbitKey Fiber` to `OrbitKey × V₄`. If Fiber were ever
--    made non-constant (a per-orbit twist), this equality would
--    break — at that point a proper `Σ` enumeration would be
--    needed.
--
-- 3. Deferred:
--    * Reserved ↔ Fin 8 (via slice 10's Reserved ↔ Axis × Bool +
--      `axis×bool-↔-fin8` here).
--    * Permutation ↔[≈] Fin 24 (via TotalSpace ↔ Permutation +
--      `totalspace-↔-fin24`, modulo pointwise ≈).
--    * Live ↔[≈] Fin 24 (via Live ≃ Permutation + above).
--    * Stab(anchor) ↔[≈] Fin 6 (via stab≃s₃ + |SFin.Permutation 3|
--      = 6; the latter is its own deferred enumeration).
--
-- 4. Cross-references:
--    * Slice 15: atomic |X| = n bijections (Axis, V₄, Pairing,
--      Chirality, Bool).
--    * Slice 4: TotalSpace ↔ Permutation.
--    * stdlib Data.Fin.Properties.*↔× — the underlying combine/
--      remQuot construction.
------------------------------------------------------------------------
