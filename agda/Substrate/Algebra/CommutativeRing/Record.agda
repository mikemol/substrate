------------------------------------------------------------------------
-- Substrate.Algebra.CommutativeRing.Record
--
-- THE RECORD ALONE — the type `CommutativeRing`, with its fields reachable
-- only as QUALIFIED projections (`CommutativeRing.ring`,
-- `CommutativeRing.*-comm`). No `open … public`.
--
-- ⚑ WHY THIS MODULE EXISTS: THE RE-EXPORT WAS THE COLLISION.
-- `CommutativeRing.agda:28` was `open CommutativeRing public`, which put the
-- FIELD names `ring` and `*-comm` into every one of 33 importers' scope as
-- bare names. A consumer that needs only the record TYPE — to write
-- `(CR : CommutativeRing A)` in a telescope — was forced to take the field
-- names too.
--
-- MEASURED: `Graded.FromCommRing.TimesComm` defines `*-comm = CommutativeRing.*-comm CR`
-- and needs `CommutativeRing` for its telescope, so it bare-imported the module
-- and got `[ClashingDefinition] Multiple definitions of *-comm`. That leaf's
-- import set is MINIMAL (an emitter-chained prune left 0 unused across all 22
-- sibling leaves), so the clash survives a perfect prune — it is a GRANULARITY
-- fact, not a pruning failure. The remedy is to make the import hierarchy fine
-- enough that "I need the type" and "I want the fields unqualified" are
-- different imports.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CommutativeRing.Record where

open import Substrate.Algebra.Magma
open import Substrate.Algebra.Semigroup
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Semiring
open import Substrate.Algebra.Ring
open import Substrate.Foundation.Eq

record CommutativeRing (A : Set) : Set where
  field
    ring : Ring A
    *-comm :
      let _*_ = Magma._·_ (magma (semigroup (*-monoid (semiring ring))))
      in (a b : A) → a * b ≡ b * a
