------------------------------------------------------------------------
-- Substrate.Foundation
--
-- Phase-2 capstone: substrate-native foundations.
--
-- ===================================================================
-- WHAT LANDED (Phase 2: native implementations, no stdlib)
-- ===================================================================
--
--   Substrate.Foundation.Level       Agda.Primitive Level
--   Substrate.Foundation.Empty       data ⊥ + ⊥-elim
--   Substrate.Foundation.Unit        record ⊤ + tt
--   Substrate.Foundation.Bool        data Bool + BUILTIN BOOL + ops
--   Substrate.Foundation.Function    id / const / _∘_ / flip / _$_
--   Substrate.Foundation.Eq          _≡_ + BUILTIN EQUALITY + combinators
--                                    + level-polymorphic + ≡-Reasoning
--   Substrate.Foundation.Negation    ¬_ + Dec
--   Substrate.Foundation.Nat         data ℕ + BUILTIN NATURAL + arith
--                                    + decidable equality + NonZero
--   Substrate.Foundation.Nat.Properties
--                                    +-/*-assoc/comm/identity + distrib
--   Substrate.Foundation.Product     record Σ (level-poly) + sugar
--   Substrate.Foundation.Sum         data _⊎_ + eliminator
--   Substrate.Foundation.Fin         data Fin + toℕ/fromℕ + _≟_ + _<_
--   Substrate.Foundation.Fin.Properties
--                                    re-exports _≟_ / _<_ / _≤_
--   Substrate.Foundation.Vec         data Vec + replicate/lookup/map/
--                                    zipWith/_++_/foldr/foldl/length
--
-- ===================================================================
-- STDLIB DEPENDENCY: ELIMINATED
-- ===================================================================
--
-- The substrate's Foundation/ modules import ONLY Agda.Primitive
-- (the compiler's Level builtin, not stdlib). All ℕ / Fin / Vec /
-- Σ / _⊎_ / ⊥ / ⊤ / Bool / _≡_ / _∘_ / ¬_ / Dec definitions are
-- substrate-native datatypes / records. Downstream substrate code
-- routes EVERYTHING through Substrate.Foundation.* — no direct
-- stdlib imports.
--
-- The 520-file migration (Phase 1, scripts/migrate_to_foundation_v2.py)
-- moved every consumer to Substrate.Foundation.* imports. Phase 2
-- swapped the bodies of those modules from stdlib re-exports to
-- native definitions. Result: the substrate compiles without
-- agda-stdlib installed.
--
-- Per the user's "no stdlib we can grow ourselves" discipline.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation where

-- Level's `zero`/`suc` are renamed at the capstone level to avoid
-- the inevitable clash with Nat's `zero`/`suc`. Consumers needing
-- level constructors import Substrate.Foundation.Level directly.
open import Substrate.Foundation.Level
  using (Level; _⊔_; Setω)
open import Substrate.Foundation.Empty
open import Substrate.Foundation.Unit
open import Substrate.Foundation.Bool
open import Substrate.Foundation.Function
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Negation
open import Substrate.Foundation.Nat
open import Substrate.Foundation.Nat.Properties
open import Substrate.Foundation.Product
open import Substrate.Foundation.Sum
-- Fin's `zero`/`suc`/`_<_`/`_≤_`/`_≟_` clash with Nat's; consumers
-- needing Fin's variants import Substrate.Foundation.Fin directly.
open import Substrate.Foundation.Vec