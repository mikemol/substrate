------------------------------------------------------------------------
-- Substrate.Algebra.Magma
--
-- M1 of the Algebra Ladder arc per [scratch/m_mod_arc_plan.md].
--
-- The universal generator of the algebraic-structure ladder. A
-- Magma is just a carrier with a binary operation — no laws.
-- All subsequent structures (Semigroup, Monoid, Group, ...) extend
-- this record with axioms.
--
-- Per [[feedback-categorical-name-first]]: "Magma" is the standard
-- universal-algebra name for (carrier, binary op, no laws).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Magma where

------------------------------------------------------------------------
-- 1. The Magma record.
------------------------------------------------------------------------

record Magma (A : Set) : Set where      -- ⟦shape:ec84712a _·_⟧
  field
    _·_ : A → A → A

open Magma public

------------------------------------------------------------------------
-- 2. The trivial Magma (1-element).
--
-- Carrier = one-point set; op is the unique constant. Smoke test
-- that the record accepts the degenerate case.
------------------------------------------------------------------------

open import Substrate.Foundation.Unit using (⊤; tt)

trivial-Magma : Magma ⊤
trivial-Magma = record { _·_ = λ _ _ → tt }

------------------------------------------------------------------------
-- 3. Capstone for M1.
--
-- Magma defined. M2 extends with associativity → Semigroup.
------------------------------------------------------------------------
