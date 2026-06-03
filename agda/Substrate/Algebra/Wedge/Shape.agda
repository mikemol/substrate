------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape
--
-- THE CARRIER-FREE WEDGE OPERATOR. Feeding the wedge type as numerator and
-- the carrier as denominator gives the fixed-point equation
--     Wedge = Wedge · C + Cshape
-- whose least solution is the geometric series  Cshape × List C  — realized
-- already as the `Trace` (the free term). Dividing the carrier out (C := 1)
-- collapses  μT. (1 + C·ℕ·C·T)  to  μT. (1 + ℕ·T) = List ℕ. So the wedge
-- operator, stripped of every carrier, IS `List ℕ` — the sequence of
-- quotients, i.e. the CONTINUED FRACTION.
--
-- This is the strongest form of genericity: not a second carrier, but NO
-- carrier. `shape` projects any trace over any DivStr to its carrier-free
-- type; the carrier was only positional fill. It closes "Peano derives from
-- partition" [[project_center_free_universal_property]]: the operator's sole
-- carrier-free content is the count of partition-steps — it is ℕ-structured.
--
-- CROSS-SILO PAYOFF: two silos' Euclidean runs CORRESPOND exactly when their
-- shapes agree — `shape t₁ ≡ shape t₂` — a carrier-free comparison. The
-- bridge is then "same shape, different fill"; the shape is the invariant the
-- correspondence is read against, with no carrier to translate.
--
-- (The full container iso  Wedge D a b ≅ ⟦ shape ⟧ C  — shape + a fill of
-- C-positions recovering the wedge — is the deeper statement; this module
-- builds the carrier-free PROJECTION, which is what "a type with no carrier"
-- asks for. The iso is the next refinement, not claimed here.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Shape where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Wedge
  using (DivStr; C; Wedge; quot; Trace; done; more; ℕ-div; fromEEATrace)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)

------------------------------------------------------------------------
-- 1. The carrier-free type of the wedge operator.
------------------------------------------------------------------------

-- the sequence of quotients = the continued fraction. NO carrier appears.
WedgeShape : Set
WedgeShape = List ℕ

------------------------------------------------------------------------
-- 2. The projection: any trace over any carrier ↦ its carrier-free shape.
--    Uniform in D — the codomain mentions no C D.
------------------------------------------------------------------------

shape : {D : DivStr} {a b g : C D} → Trace D a b g → WedgeShape
shape (done _)      = []
shape (more _ w tr) = quot w ∷ shape tr

------------------------------------------------------------------------
-- 3. Cross-silo invariant: correspondence is shape-equality (carrier-free).
--    `Corresponds t₁ t₂` is a statement with no carrier in it.
------------------------------------------------------------------------

Corresponds : {D₁ D₂ : DivStr} {a₁ b₁ g₁ : C D₁} {a₂ b₂ g₂ : C D₂} →
              Trace D₁ a₁ b₁ g₁ → Trace D₂ a₂ b₂ g₂ → Set
Corresponds t₁ t₂ = shape t₁ ≡ shape t₂

-- a trace corresponds to itself: reflexivity of the carrier-free reading.
self-corresponds : {D : DivStr} {a b g : C D} (t : Trace D a b g) →
                   Corresponds t t
self-corresponds _ = refl

------------------------------------------------------------------------
-- 4. Oracle: the ℕ-Euclid shape of an EEATrace is its quotient sequence.
------------------------------------------------------------------------

ℕ-shape : {a b g : ℕ} → EEATrace a b g → WedgeShape
ℕ-shape t = shape (fromEEATrace t)
