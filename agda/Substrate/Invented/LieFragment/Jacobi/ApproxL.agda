------------------------------------------------------------------------
-- Substrate.Invented.LieFragment.Jacobi.ApproxL
--
-- Defines: _≈L_, bracket-cong, jacobi-L, refl-L, swap-L, sym-L, trans-L
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Invented.LieFragment.Jacobi; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Invented.LieFragment.Jacobi.ApproxL where

open import Substrate.Invented.LieFragment
open import Substrate.Invented.LieFragment.Jacobi.LieAlgExpr

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
