------------------------------------------------------------------------
-- Substrate.Category.RootSystem
--
-- The categorical primitive for root systems.
--
-- A root system Φ is a finite set of vectors in an inner-product
-- space, closed under reflection through any α ∈ Φ, with each
-- reflection sending Φ to Φ, and satisfying the crystallographic
-- integrality condition.
--
-- The substrate-level primitive captures the COMBINATORIAL DATA:
--   * Root : Set — finite-index set of roots
--   * neg : Root → Root — the root negation involution (α ↦ -α)
--   * reflect : Root → Root → Root — reflection action s_α applied
--     to β, packaged as the resulting root index
--   * neg-involution : neg (neg α) ≡ α
--   * reflect-self : reflect α α ≡ neg α
-- This is sufficient for the Coxeter ↔ Cartan bridge (L13). The
-- inner-product / integrality data layers on top.
--
-- L11 of the L-arc; foundation for L12 [[CartanType]] (the labeled-
-- Dynkin packaging) and L13 [[Coxeter.AsCartanType]] (the bridge
-- from Coxeter Word algebra to Cartan type).
--
-- Per [[categorical-name-first]]: "root system" / "crystallographic
-- root system" / "Cartan-Killing classification" are standard
-- names. The universal property is the Serre presentation: every
-- semisimple Lie algebra is determined by its root system up to
-- isomorphism (Killing 1888-94, Cartan 1894, Serre's relations).
--
-- Per [[expose-generator-not-orbit]]: the GENERATORS are the simple
-- roots (a small set, typically n = rank); the ORBIT under the Weyl
-- group is the full root system (often ≫ n elements: e.g. A_n has
-- n simple roots, n(n+1) total roots; E_8 has 8 simple, 240 total).
-- The substrate-level primitive packages the full orbit by index;
-- concrete instances expose the generators via L12 CartanType.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.RootSystem where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Relation.Binary.PropositionalEquality using (_≡_)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The RootSystem record.
------------------------------------------------------------------------

record RootSystem : Set (lsuc ℓ) where
  constructor mkRootSystem
  field
    Root            : Set ℓ
    neg             : Root → Root
    reflect         : Root → Root → Root
    neg-involution  : (α : Root) → neg (neg α) ≡ α
    reflect-self    : (α : Root) → reflect α α ≡ neg α

------------------------------------------------------------------------
-- Capstone — root system primitive in place.
--
-- L11 of the L-arc. Foundation for:
--   * L12 CartanType (Dynkin-diagram labelling of the simple roots)
--   * L13 Coxeter.AsCartanType (bridge from Coxeter Word algebra
--     to Cartan type via the simple-reflection generators)
--   * L14 sl₂ (rank-1 root system A₁: Φ = {α, -α})
--   * L15 so₃ (= sl₂ over ℝ; same A₁ root system)
--
-- After L11: substrate has the discrete combinatorial side of the
-- Coxeter ↔ Lie correspondence. L12 + L13 close the bridge.
--
-- Per [[homology-cohomology-recursion]]: root systems are the
-- "observed" side; CartanType labels (= Dynkin diagrams) are the
-- "cataloged" side. The classification A/B/C/D + E/F/G is the
-- level-2 structure over the root-system level.
--
-- Next: L12 CartanType.
------------------------------------------------------------------------
