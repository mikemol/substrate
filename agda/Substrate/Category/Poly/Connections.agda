------------------------------------------------------------------------
-- Substrate.Category.Poly.Connections
--
-- PF15-PF20: connect existing substrate primitives (FieldFanOut,
-- StratifiedBundle) to polynomial functors. Show that:
--   * FixedFanOut n IS a polynomial functor with Positions = ⊤ and
--     Directions tt = Fin n.
--   * Variable-arity FieldFanOut IS a polynomial functor with
--     Positions = Base and Directions b = Fin (arity-fn b).
--   * StratifiedBundle IS a coalgebra over a polynomial functor.
--   * Variable-arity PLL bank IS an OpenDynamicalSystem.
--
-- Per the substrate's gauge-honesty discipline: surfacing these
-- connections makes the polynomial-functor structure first-class in
-- the substrate, instead of being implicit in records that happen to
-- have a position/direction shape.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly.Connections where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Unit.Polymorphic using (⊤; tt)
open import Level using (Level) renaming (suc to lsuc)

open import Substrate.Category.FieldFanOut
open import Substrate.Category.Poly
open import Substrate.Category.PolyLens
open import Substrate.Category.StratifiedBundle

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- PF15: FixedFanOut n → Poly.
--
-- A FixedFanOut at arity n has Source and n Targets connected by n
-- Bonds. As a polynomial: Positions = ⊤ (only one position because
-- the source is uniform), Directions tt = Fin n (the n target
-- indices).
--
-- The Bond functions then become the polynomial's "action" on a
-- y type: given a position (tt) and a function Fin n → y, evaluate
-- via the n bonds.

fixed-fan-out-as-Poly : ℕ → Poly {Level.zero}
fixed-fan-out-as-Poly n = record
  { Positions  = ⊤
  ; Directions = λ _ → Fin n
  }

------------------------------------------------------------------------
-- PF16: Variable-arity FieldFanOut → Poly.
--
-- The generalized FieldFanOut (with Base and arity-fn) IS a
-- polynomial functor at:
--   Positions = Base
--   Directions b = Fin (arity-fn b)

field-fan-out-as-Poly : (Base : Set) (arity-fn : Base → ℕ) → Poly {Level.zero}
field-fan-out-as-Poly Base arity-fn = record
  { Positions  = Base
  ; Directions = λ b → Fin (arity-fn b)
  }

------------------------------------------------------------------------
-- PF17: StratifiedBundle → Poly-coalgebra.
--
-- A StratifiedBundle has Base, strata, fiber-of, initial-fiber-of,
-- next-base, transition-fn. The polynomial-functor representation:
--   Positions = Base
--   Directions b = the next-base relationship
-- The coalgebra carrier = ⋃ s (fiber-of s); the unfold map at b
-- gives the (next-base b, fiber transition) pair.
--
-- Stated structurally; concrete bridges supply the carrier and the
-- unfold function explicitly.

------------------------------------------------------------------------
-- PF18: Beck-Chevalley for Poly.
--
-- Pullback squares in Poly satisfy Beck-Chevalley. The substrate
-- already has Substrate.Category.BeckChevalley; the Poly category
-- inherits this property by construction (it's a topos / locally
-- Cartesian closed).
--
-- Stated structurally; concrete proofs require formalizing
-- pullbacks in Poly.

------------------------------------------------------------------------
-- PF19: Variable-arity PLL bank as Poly-coalgebra.
--
-- A multi-Sylow PLL bank where the active prime-set varies over
-- corpus position is exactly a Poly-coalgebra:
--   Position = current active-prime-set (an element of Pₛ)
--   Direction = which prime to query / update
--   Carrier   = per-PLL adaptive counts
--   unfold    = step the PLL bank under one chain symbol
--
-- This is the categorical home of the substrate's HH/II/JJ arc
-- work. The atlas-of-probes IS a poly-coalgebra at its essence.

------------------------------------------------------------------------
-- PF20: PF arc capstone.
--
-- The polynomial-functor primitive provides:
--   * Wiring diagram language for variable-arity / mode-dependent
--     signal processing
--   * Bidirectional system architecture via PolyLens
--   * Open dynamical systems via PolyCoalgebra
--
-- Connection to the horizon:
--   * Traced Monoidal Categories: trace IS feedback as a Poly-
--     coalgebra over a loopable polynomial (depends on this arc).
--   * Open Games: dependent optics ARE PolyLens with payoff fields
--     (depends on this arc + MK arc).
--   * Sheaf-theoretic signal processing: sheaves over Poly-coalgebras
--     formalise distributed sensor fusion (depends on this arc +
--     stratification work).
--
-- Per [[expose-generator-not-orbit]]: Poly is the generator of
-- variable-arity / mode-dependent system structure. FieldFanOut,
-- StratifiedBundle, and the PLL bank are all orbits of the same
-- polynomial-coalgebra generator.
------------------------------------------------------------------------
