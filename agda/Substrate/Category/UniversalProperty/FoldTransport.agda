{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.FoldTransport — AUTOMATIC TRANSPORT between
-- trace-folds. The point of registering the various trace-folds (collapse, shape,
-- Bézout, …) as BackedUP is not bookkeeping: because Trace is the INITIAL ALGEBRA,
-- ANY two folds related by an algebra morphism COMMUTE — automatically, by trace-
-- fold-unique. This module builds that transport engine and applies it.
--
-- trace-fold-transport: given a fold h₂ = trace-fold bi₂ si₂ and a map φ from h₁'s
-- target into h₂'s, IF φ carries h₁'s algebra to h₂'s (φ∘bi₁ = bi₂, φ∘si₁ = si₂∘φ),
-- THEN φ ∘ h₁ = h₂ on every trace. Set h := φ ∘ (trace-fold bi₁ si₁) and apply
-- trace-fold-unique: h agrees with (bi₂,si₂) on done/more, so it IS trace-fold bi₂ si₂.
-- The registration (mu-backed etc.) makes each fold a certified solver; THIS makes
-- the square between any two of them commute for free.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.FoldTransport where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Algebra.Wedge using (DivStr; z; rem; Trace; done; more; trace-fold; trace-fold-unique; collapse-fold) renaming (Wedge to Wedge⟦478f66a6⟧)
module _ {C : Set} {D : DivStr C} where

  -- an algebra over the (done/more) signature into a target family T.
  -- (base : the done-interpretation ; step : the more-interpretation.)

  ------------------------------------------------------------------------
  -- THE TRANSPORT ENGINE. Two folds fold₁ = trace-fold bi₁ si₁ (into T₁) and
  -- fold₂ = trace-fold bi₂ si₂ (into T₂), and a family map φ : T₁ → T₂ that carries
  -- the first algebra to the second — then φ ∘ fold₁ ≡ fold₂ on every trace.
  ------------------------------------------------------------------------
  trace-fold-transport :
    {T₁ T₂ : C → C → C → Set}
    (bi₁ : (a : C) → T₁ a (z D) a)
    (si₁ : {a g : C} (b : C) (w : Wedge⟦478f66a6⟧ D a b) → T₁ b (rem w) g → T₁ a b g)
    (bi₂ : (a : C) → T₂ a (z D) a)
    (si₂ : {a g : C} (b : C) (w : Wedge⟦478f66a6⟧ D a b) → T₂ b (rem w) g → T₂ a b g)
    (φ  : {a b g : C} → T₁ a b g → T₂ a b g)
    (φ-base : (a : C) → φ (bi₁ a) ≡ bi₂ a)
    (φ-step : {a g : C} (b : C) (w : Wedge⟦478f66a6⟧ D a b) (x : T₁ b (rem w) g) →
              φ (si₁ b w x) ≡ si₂ b w (φ x)) →
    {a b g : C} (t : Trace D a b g) →
    φ (trace-fold bi₁ si₁ t) ≡ trace-fold bi₂ si₂ t
  trace-fold-transport bi₁ si₁ bi₂ si₂ φ φ-base φ-step =
    trace-fold-unique bi₂ si₂
      (λ t → φ (trace-fold bi₁ si₁ t))
      φ-base
      (λ b w tr → trans (φ-step b w (trace-fold bi₁ si₁ tr)) refl)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — automatic transport, the point of registering folds):
-- because Trace is the INITIAL ALGEBRA (trace-fold-unique), the choice of WHICH trace-
-- fold (collapse/shape/Bézout/…) is not a fork — any two are connected by an algebra
-- morphism φ, and trace-fold-transport makes φ ∘ fold₁ ≡ fold₂ AUTOMATICALLY. Registering
-- each fold as a BackedUP (mu-backed, 170; the others analogous) certifies each is a real
-- non-vacuous solver; trace-fold-transport certifies the SQUARE between any two commutes.
-- So the either/or "which fold is THE fold" dissolves: they are all the SAME initial-
-- algebra morphism composed with different target algebras, and the transport is free.
-- This is the DUAL of the ν side's bisim-transport (ana-unique): there the terminal
-- coalgebra gives transport up-to-~; here the initial algebra gives transport up-to-≡.
------------------------------------------------------------------------
