------------------------------------------------------------------------
-- Substrate.Groups.SFin
--
-- The parameterised symmetric group S_n on Fin n. Thin adapter over
-- Substrate.Groups.Symmetric instantiated at Fin n.
--
-- Permutation : ℕ → Set is exposed as a type alias so downstream
-- modules can write `SFin.Permutation 3` (etc.) unchanged. All other
-- machinery is re-exported from `Symmetric (Fin n)` inside an
-- anonymous parameterized module, giving `SFin._·_`, `SFin.ε`, etc.
-- their familiar `{n : ℕ}` implicit shape.
--
-- Per [[feedback-v4-typeclass-architecture]]: zero duplicated
-- machinery vs the previous standalone implementation.
--
-- See: catalog/cocycles.md § CY-2 — S_n acting on the variable space
--      V for the K-rule cocycle.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.SFin where

open import Algebra.Bundles using (Group)
open import Level using (0ℓ)
open import Data.Nat using (ℕ)
open import Data.Fin using (Fin)

import Substrate.Groups.Symmetric as Sym

------------------------------------------------------------------------
-- Permutation n = bijection Fin n → Fin n (type alias).
------------------------------------------------------------------------

Permutation : ℕ → Set
Permutation n = Sym.Permutation (Fin n)

------------------------------------------------------------------------
-- All operations and axioms, parametric in n.
--
-- `open Sym (Fin n) public hiding (Permutation)` re-exports
-- _≈_, _·_, ε, _⁻¹, the axioms, Symmetric-Group, σ-injective, and
-- the field accessors apply / invₐ / inv-l / inv-r — all with
-- implicit `{n : ℕ}` parameterization.
------------------------------------------------------------------------

module _ {n : ℕ} where

  open Sym (Fin n) public hiding (Permutation)

  -- Alias the bundled Group as S-Group for backwards compatibility.
  S-Group : Group 0ℓ 0ℓ
  S-Group = Symmetric-Group
