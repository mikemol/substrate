------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi.LieAlgExpr
--
-- Defines: LieAlgExpr, _⊕L_, bracket, gen, zero-L
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.Jacobi; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi.LieAlgExpr where

open import Substrate.Invented.LieFragment

infixl 6 _⊕L_


------------------------------------------------------------------------
-- 1. The extended Lie-algebra carrier.
--
-- LieAlgExpr extends LieExpr from C7 with the formal SUM ⊕L and
-- ZERO needed to state Jacobi. Keeps the underlying gen + bracket
-- structure unchanged; just adds the additional operations.
------------------------------------------------------------------------

data LieAlgExpr : Set where
  gen      : LieGen → LieAlgExpr
  bracket  : LieAlgExpr → LieAlgExpr → LieAlgExpr
  zero-L   : LieAlgExpr
  _⊕L_     : LieAlgExpr → LieAlgExpr → LieAlgExpr


------------------------------------------------------------------------
-- 2. The Setoid relation _≈L_ — the full Lie-algebra equational
-- quotient.
--
-- Constructors include:
--   * Equivalence (refl, sym, trans)
--   * Sum laws (assoc, comm, identity, F₂ self-inverse)
--   * Bracket congruence
--   * anti-commutativity (swap-L) — the D3 axiom
--   * Jacobi identity (jacobi-L) — the headline D4 axiom
------------------------------------------------------------------------
