------------------------------------------------------------------------
-- Substrate.Category.FieldFanOut
--
-- Fan-out bond structure: one source field with n target fields,
-- each connected via an oriented bond from source to target.
--
-- Generalizes Substrate.Category.MultiFieldBond.FieldTower (chains)
-- to one of the natural DAG shapes — fan-out from a common root.
-- Captures CRT-style decomposition where Z/(p₁p₂...pₙ) projects to
-- each Z/pᵢ simultaneously.
--
-- For Z/30 = Z/2 × Z/3 × Z/5 specifically: source = Z/30, three
-- targets (Z/2, Z/3, Z/5), three bonds (n ↦ n mod 2; n ↦ n mod 3;
-- n ↦ n mod 5). FieldFanOut 3 captures this.
--
-- Per [[project-multi-field-tower-architecture]]: the deferred
-- "tree-shaped FieldBond" — fan-out is the simplest tree shape.
-- Combined with FieldTower (chains) and future composite Tree
-- structures, the substrate has multi-field decomposition coverage.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.FieldFanOut where

open import Data.Fin using (Fin)
open import Data.Nat using (ℕ)
open import Level using (Level) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The FieldFanOut record.
--
-- One source carrier + n target carriers + n oriented bond morphisms
-- (each from source to the corresponding target).
------------------------------------------------------------------------

record FieldFanOut (n : ℕ) : Set (lsuc ℓ) where
  field
    Source  : Set ℓ
    Target  : Fin n → Set ℓ
    Bond    : (i : Fin n) → Source → Target i

------------------------------------------------------------------------
-- Capstone.
--
-- After this slice: FieldFanOut captures the simplest tree-shaped
-- bond structure — one root with n leaves.
--
-- Substrate use:
--   * Z/30 = Z/2 × Z/3 × Z/5 (CRT fan-out): FieldFanOut 3.
--   * Z/(p₁p₂...pₙ) for coprime primes: FieldFanOut n.
--   * Combined chain + fan-out trees: the substrate's 168 = 2³·3·7
--     tower could be FieldFanOut 3 at the top level (one root with
--     three primes) or a chain FieldTower 2 (sequential extraction).
--     Different gauge choices.
--
-- Per [[project-3plus1-is-cone-instance]] bond extension: fan-out
-- is the CRT-friendly bond structure (parallel decomposition).
-- Chain is the sequential-extraction bond structure. Both are
-- substrate-friendly; arbitrary tree compositions are future work.
--
-- Deferred follow-ons:
--
--   * **Concrete Z/30 FieldFanOut instance**: source = Fin 30, three
--     targets (Fin 2, Fin 3, Fin 5) with explicit per-element mod
--     functions (30 cases each — large but mechanical).
--
--   * **Generic FieldTree primitive**: arbitrary DAG of bonds (root,
--     chains, fan-outs, all in one).
--
--   * **Bond composition (chain + fan-out)**: combining chains with
--     fan-outs gives the full tree generality.
------------------------------------------------------------------------
