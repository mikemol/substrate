------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.GriessAlgebra.AsJordan
--
-- Parametric bridge from a Griess-like commutative algebra to L16
-- [[JordanAlgebra]].
--
-- L17 of the L-arc.
--
-- CAVEAT — DOES NOT ASSERT GRIESS IS JORDAN:
--
--   The standard 196,884-dim Griess algebra is a CommutativeNonAss-
--   ociativeAlgebra satisfying the Frobenius form-product associativity
--   (⟨xy, z⟩ = ⟨x, yz⟩) — captured by X3 CNAA + X4 GriessAlgebra in
--   the substrate. Whether Griess additionally satisfies the standard
--   Jordan identity (x²·y)·x ≡ x²·(y·x) depends on the specific
--   structure-constant choice + is NOT universally true in the
--   literature (Griess's algebra is famously a commutative non-
--   associative algebra without an asserted Jordan identity; the
--   substrate must not overclaim).
--
--   Per [[comments-dont-overclaim]]: this module's job is structural —
--   provide the bridge type IF the user can supply the Jordan
--   identity. The substrate ITSELF does not assert Griess is Jordan.
--
--   The user supplies the V + algebra structure + Jordan-identity
--   proof as module parameters. If the user's specific Griess
--   structure-constant choice DOES satisfy the Jordan identity, this
--   module names that fact structurally. If not, the module is
--   uninstantiable for Griess — which is the honest substrate-side
--   outcome.
--
-- Per [[universal-property-discipline]]: the substrate's L17 names
-- "the bridge from a commutative algebra to JordanAlgebra"; whether
-- a specific Griess instance fits depends on the form-of-Griess used.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)
open import Relation.Binary.PropositionalEquality using (_≡_)

open import Substrate.Category.JordanAlgebra
  using (JordanAlgebra; mkJordanAlgebra)

module Substrate.Algebra.Sporadic.GriessAlgebra.AsJordan
  -- The Griess-like algebra's carrier + commutative structure.
  {ℓ : Level}
  (V : Set ℓ)
  (0V : V)
  (_+V_ : V → V → V)
  (_·_ : V → V → V)
  (comm : (x y : V) → (x · y) ≡ (y · x))
  -- The Jordan identity — user-supplied OBLIGATION. If the user's
  -- Griess structure satisfies it, the bridge applies; otherwise, the
  -- module is uninstantiable.
  (jordan-identity :
    (x y : V) → (((x · x) · y) · x) ≡ ((x · x) · (y · x)))
  where

------------------------------------------------------------------------
-- 1. The user-supplied algebra as L16 JordanAlgebra.
--
-- Direct re-package: the V + commutative · + user's Jordan identity
-- IS a JordanAlgebra. The substrate's role is to name the bridge,
-- not to prove the Jordan identity for Griess.
------------------------------------------------------------------------

Griess-AsJordan : JordanAlgebra
Griess-AsJordan = mkJordanAlgebra V 0V _+V_ _·_ comm jordan-identity

------------------------------------------------------------------------
-- 2. Capstone — parametric Griess-Jordan bridge in place.
--
-- L17 of the L-arc. Per the substrate's [[comments-dont-overclaim]]
-- discipline: this module DOES NOT assert Griess is Jordan; it
-- provides the bridge structure for users whose specific Griess
-- presentation satisfies the Jordan identity.
--
-- Per the substrate's broader algebra taxonomy:
--   * X4 GriessAlgebra: 196,884-dim CNAA with Frobenius form
--     (canonical substrate Griess)
--   * L17 Griess-AsJordan (THIS): same V + commutative ·, with
--     user-supplied Jordan identity as obligation
--
-- The two views are NOT structurally equivalent; if a user
-- constructs both for the same V/+V/·, they witness that this
-- specific Griess-presentation satisfies both Frobenius AND Jordan
-- — a fact the user must establish.
--
-- Next: L18 UniversalEnvelopingAlgebra (the Lie → Assoc adjunction).
------------------------------------------------------------------------
