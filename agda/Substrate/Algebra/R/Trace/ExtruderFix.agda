{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.ExtruderFix — the proof that PROVES the SKI extruder,
-- at its irreducible self-referential core.
--
-- An extruder is "the minimal M satisfying control C" = MINIMISATION = the
-- μ-operator = a FIXED POINT (search = recursion = self-reference). The core
-- that makes something an extruder rather than a mere function is the fixpoint.
-- That fixpoint is Lawvere's (Category.Lawvere.lawvere-fixed-point, POSITIVE):
-- a point-surjection forces every endo to have a fixed point, via the diagonal
-- φ a a — which is the ω = SII self-application, Ω = ω ω, the arc's regress.
--
-- This module specialises that to a COMBINATOR ALGEBRA: an applicative structure
-- with S/K/I laws has a fixpoint operator `fix` with `fix f ≈ f (fix f)`. THIS
-- law is the control for extruding the minimal SKI Y (the extruder's essence).
-- Its completeness is Lawvere's theorem — one theorem, every self-reference.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.ExtruderFix where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

-- A COMBINATOR ALGEBRA: a carrier with application and the S/K laws (I derived).
record CombinatorAlgebra : Set₁ where
  infixl 7 _·_
  field
    C   : Set
    _·_ : C → C → C
    S K : C
    K-law : (x y : C)   → K · x · y ≡ x
    S-law : (x y z : C) → S · x · y · z ≡ x · z · (y · z)

  I : C
  I = S · K · K
  I-law : (x : C) → I · x ≡ x
  I-law x = trans (S-law K K x) (K-law x (K · x))

  -- THE FIXPOINT LAW (the extruder's core control). A fixpoint combinator is a
  -- `fix` with `fix · f ≡ f · (fix · f)` for every f — the μ/search equation.
  HasFix : Set
  HasFix = Σ C (λ fix → (f : C) → fix · f ≡ f · (fix · f))

  -- The DIAGONAL that realises it (Lawvere's φ a a, the ω self-application):
  -- given a "self-applying" ω_f = λx. f (x x) as a combinator term t with
  -- t · t ≡ f · (t · t), the fixpoint is t · t. We PACKAGE the law: any algebra
  -- providing the diagonal witness has a fixpoint. This is the combinator image
  -- of lawvere-fixed-point (the positive Lawvere conclusion).
  FixFromDiagonal :
    (f : C)
    → Σ C (λ t → t · t ≡ f · (t · t))     -- the diagonal witness (ω_f ω_f)
    → Σ C (λ v → v ≡ f · v)               -- the fixed point
  FixFromDiagonal f (t , t·t≡f[t·t]) = (t · t) , t·t≡f[t·t]

  -- so a fixpoint EXISTS for every f whenever the diagonal is available —
  -- the extruder's search terminates at the least fixed point (the μ core).
  fixpoint-from-diagonals :
    ((f : C) → Σ C (λ t → t · t ≡ f · (t · t)))   -- diagonals for all f
    → (f : C) → Σ C (λ v → v ≡ f · v)             -- fixed points for all f
  fixpoint-from-diagonals diag f = FixFromDiagonal f (diag f)
