------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Shape
--
-- THE WEDGE OPERATOR'S QUOTIENT SEQUENCE. Feeding the wedge type as numerator
-- and the carrier as denominator gives the fixed-point equation
--     Wedge = Wedge · C + Cshape
-- whose least solution is the geometric series  Cshape × List C  — realized
-- already as the `Trace` (the free term). Stripping the positional fill but
-- KEEPING the quotients (each now a carrier representative `C D`, no longer a
-- bare ℕ count) collapses the term to  List (C D)  — the sequence of
-- quotients, i.e. the CONTINUED FRACTION.
--
-- `shape` projects any trace over a fixed DivStr D to this quotient sequence;
-- the only positional fill discarded is `b` and the witnesses. The quotient,
-- being a carrier representative ([[feedback_coordinate_to_geometry]]: the old
-- ℕ count was a frozen coordinate), is retained — so the shape lives over the
-- carrier C D, not over a carrier-free ℕ. This closes "Peano derives from
-- partition" [[project_center_free_universal_property]] for the ℕ carrier,
-- where each quotient representative is a count; over a polynomial carrier the
-- same sequence carries F₂[x] quotients.
--
-- CROSS-SILO PAYOFF: two silos' Euclidean runs over the SAME carrier CORRESPOND
-- exactly when their shapes agree — `shape t₁ ≡ shape t₂` — a comparison of
-- quotient sequences. The bridge is then "same quotients, different positional
-- fill"; the shape is the invariant the correspondence is read against.
--
-- (The full container iso  Wedge D a b ≅ ⟦ shape ⟧ C  — shape + a fill of
-- C-positions recovering the wedge — is the deeper statement; this module
-- builds the quotient-sequence PROJECTION. The iso is the next refinement, not
-- claimed here.)
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
-- 1. The quotient-sequence type of the wedge operator over a carrier D.
------------------------------------------------------------------------

-- the sequence of quotient representatives = the continued fraction. The
-- positional fill (b, the witnesses) is gone; the quotients are retained as
-- carrier elements `C D`.
WedgeShape : DivStr → Set
WedgeShape D = List (C D)

------------------------------------------------------------------------
-- 2. The projection: any trace over a carrier D ↦ its quotient sequence.
------------------------------------------------------------------------

shape : {D : DivStr} {a b g : C D} → Trace D a b g → WedgeShape D
shape (done _)      = []
shape (more _ w tr) = quot w ∷ shape tr

------------------------------------------------------------------------
-- 3. Cross-silo invariant: correspondence is shape-equality. Over the SAME
--    carrier D, two runs correspond when their quotient sequences agree.
------------------------------------------------------------------------

Corresponds : {D : DivStr} {a₁ b₁ g₁ : C D} {a₂ b₂ g₂ : C D} →
              Trace D a₁ b₁ g₁ → Trace D a₂ b₂ g₂ → Set
Corresponds t₁ t₂ = shape t₁ ≡ shape t₂

-- a trace corresponds to itself: reflexivity of the carrier-free reading.
self-corresponds : {D : DivStr} {a b g : C D} (t : Trace D a b g) →
                   Corresponds t t
self-corresponds _ = refl

------------------------------------------------------------------------
-- 4. Oracle: the ℕ-Euclid shape of an EEATrace is its quotient sequence.
------------------------------------------------------------------------

ℕ-shape : {a b g : ℕ} → EEATrace a b g → WedgeShape ℕ-div
ℕ-shape t = shape (fromEEATrace t)
