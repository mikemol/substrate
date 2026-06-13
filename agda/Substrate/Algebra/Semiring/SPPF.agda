------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.SPPF
--
-- Semiring-weighted parsing (el-atlas SWP): ONE CHART, PLUGGABLE SEMIRING.
-- A packed parse forest is the free-semiring term on its generators; a single
-- fold `inside` evaluates it in ANY semiring, with a valuation of the generators.
-- The carrier semiring carries the SPPF's packed multiplicity: the ambiguity node
-- `_⊕_` folds to the semiring's `+`, sequencing `_⊗_` to its `×`.
--
-- Plug the semiring, read off the chart:
--   ℕ (counting)        → the derivation COUNT (the packed multiplicity itself)
--   tropical ℕ∞ (min,+) → Viterbi: the minimum-cost derivation (idempotent pinning)
--   a probability rig   → inside×outside probability (the positive-rail section)
-- One forest, one fold; the reading is entirely the plugged semiring.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Semiring.SPPF where

open import Substrate.Algebra.Magma     using (Magma)
open import Substrate.Algebra.Semigroup using (magma)
open import Substrate.Algebra.Monoid    using (semigroup; ε)
open import Substrate.Algebra.Semiring  using (Semiring; +-monoid; *-monoid)

------------------------------------------------------------------------
-- The packed parse forest = the free-semiring term on generators G.
--   gen g  — a leaf/edge, weighted by the valuation
--   one    — the empty derivation (multiplicative unit)
--   _⊗_    — sequencing (a derivation's children, concatenated)
--   _⊕_    — PACKED ambiguity (alternative derivations sharing a node)
------------------------------------------------------------------------

data SPPF (G : Set) : Set where
  gen : G → SPPF G
  one : SPPF G
  _⊗_ : SPPF G → SPPF G → SPPF G
  _⊕_ : SPPF G → SPPF G → SPPF G

infixr 7 _⊗_
infixr 6 _⊕_

------------------------------------------------------------------------
-- THE fold: one chart, pluggable semiring. `_⊕_ ↦ +`, `_⊗_ ↦ ×`, `one ↦ 1`.
-- Parametric over the semiring S and the generator valuation v.
------------------------------------------------------------------------

inside : {A G : Set} → Semiring A → (G → A) → SPPF G → A
inside S v (gen g) = v g
inside S v one     = ε (*-monoid S)
inside S v (a ⊗ b) = Magma._·_ (magma (semigroup (*-monoid S))) (inside S v a) (inside S v b)
inside S v (a ⊕ b) = Magma._·_ (magma (semigroup (+-monoid S))) (inside S v a) (inside S v b)
