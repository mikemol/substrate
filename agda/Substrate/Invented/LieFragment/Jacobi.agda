------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi
--
-- D4 of the Closure-debt arc per [scratch/closure_arc_plan.md].
--
-- Surfaces the Jacobi identity, the second Lie-algebra axiom. Since
-- the C7 LieExpr (gen + bracket constructors only) lacks the formal
-- SUM and ZERO needed to state Jacobi, this slice defines an
-- EXTENDED carrier LieAlgExpr (LieExpr + zero + ⊕L) and surfaces
-- both Lie axioms (anti-commutativity from D3, plus Jacobi) as
-- constructors of a Setoid relation on the extended carrier.
--
-- Per [[feedback-comments-dont-overclaim]]: the Jacobi identity
-- requires a notion of sum + zero in the carrier, so the Setoid
-- here works on LieAlgExpr, not on the bare LieExpr. D3's
-- anti-commutativity Setoid is the SUB-relation living inside this
-- extended one (concretely: swap-L IS the embedded anti-comm).
--
-- Together D3 + D4 give the FULL Lie-algebra equational quotient
-- at the LieFragment level. The connection to
-- Substrate.Category.LieAlgebra (the substrate's general
-- Lie-algebra primitive) is the next step — deferred per
-- [[feedback-coalgebraic-not-consumer-driven]] to a future arc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi where

open import Substrate.Invented.LieFragment using (LieGen; x; y; z)

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

infixl 6 _⊕L_

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

infix 4 _≈L_

data _≈L_ : LieAlgExpr → LieAlgExpr → Set where
  -- Setoid laws
  refl-L  : {e : LieAlgExpr} → e ≈L e
  sym-L   : {e₁ e₂ : LieAlgExpr} → e₁ ≈L e₂ → e₂ ≈L e₁
  trans-L : {e₁ e₂ e₃ : LieAlgExpr} → e₁ ≈L e₂ → e₂ ≈L e₃ → e₁ ≈L e₃
  -- Sum laws (commutative monoid; F₂ characteristic makes self-inverse)
  ⊕L-assoc :
    (a b c : LieAlgExpr) → (a ⊕L b) ⊕L c ≈L a ⊕L (b ⊕L c)
  ⊕L-comm :
    (a b : LieAlgExpr) → a ⊕L b ≈L b ⊕L a
  ⊕L-zeroˡ :
    (a : LieAlgExpr) → zero-L ⊕L a ≈L a
  -- Bracket congruence
  bracket-cong :
    {x₁ x₂ y₁ y₂ : LieAlgExpr} →
    x₁ ≈L x₂ → y₁ ≈L y₂ → bracket x₁ y₁ ≈L bracket x₂ y₂
  ⊕L-cong :
    {a₁ a₂ b₁ b₂ : LieAlgExpr} →
    a₁ ≈L a₂ → b₁ ≈L b₂ → a₁ ⊕L b₁ ≈L a₂ ⊕L b₂
  -- Lie axiom #1: anti-commutativity (D3's headline at the
  -- LieAlgExpr level; F₂-flavoured)
  swap-L :
    (a b : LieAlgExpr) → bracket a b ≈L bracket b a
  -- Lie axiom #2: Jacobi identity
  --   [x, [y, z]] + [y, [z, x]] + [z, [x, y]] ≈L zero-L
  jacobi-L :
    (a b c : LieAlgExpr) →
    ((bracket a (bracket b c) ⊕L bracket b (bracket c a))
      ⊕L bracket c (bracket a b))
    ≈L zero-L

------------------------------------------------------------------------
-- 3. The headline axiom (named).
------------------------------------------------------------------------

jacobi-identity :
  (a b c : LieAlgExpr) →
  ((bracket a (bracket b c) ⊕L bracket b (bracket c a))
    ⊕L bracket c (bracket a b))
  ≈L zero-L
jacobi-identity = jacobi-L

------------------------------------------------------------------------
-- 4. Worked example at concrete generators.
--
-- Jacobi applied to the three basis generators (gen x, gen y, gen z)
-- — the canonical Lie-axiom verification.
------------------------------------------------------------------------

example-jacobi-xyz :
  ((bracket (gen x) (bracket (gen y) (gen z)) ⊕L
    bracket (gen y) (bracket (gen z) (gen x))) ⊕L
   bracket (gen z) (bracket (gen x) (gen y)))
  ≈L zero-L
example-jacobi-xyz = jacobi-L (gen x) (gen y) (gen z)

------------------------------------------------------------------------
-- 5. Right-identity of ⊕L (derived).
--
-- a ⊕L zero-L ≈L a, from ⊕L-comm + ⊕L-zeroˡ.
------------------------------------------------------------------------

⊕L-zeroʳ : (a : LieAlgExpr) → a ⊕L zero-L ≈L a
⊕L-zeroʳ a = trans-L (⊕L-comm a zero-L) (⊕L-zeroˡ a)

------------------------------------------------------------------------
-- 6. Capstone.
--
-- LieAlgExpr + _≈L_ is the substrate-native realisation of the Lie
-- equational quotient over the C7 generators. D3 + D4 jointly
-- close the "fuller Lie treatment" deferred at C7's capstone.
--
-- Future arc: connect to Substrate.Category.LieAlgebra (which
-- provides the abstract Lie-algebra record). The connection would
-- be a functor LieAlgExpr/≈L → LieAlgebra-instance, demonstrating
-- the substrate's general Lie primitive subsumes the LieFragment.
------------------------------------------------------------------------
