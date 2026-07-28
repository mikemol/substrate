{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Abelian.V4-as-PFG-Applied
--
-- ⟡S4-wire-apply. Feeds the substrate's OWN V₄ group data into the
-- parameterized V4-as-PFG, producing the concrete CDSW-torsor-as-AbelianPFG
-- with NO remaining parameters. Everything supplied is already proven in
-- Groups/V4/Axioms (⟡H0′ grep — nothing derived here):
--   _·_, ε            — Groups.V4.Operations
--   ·-assoc, ·-comm   — Groups.V4.Axioms (v4×v4×v4-cover / v4×v4-cover)
--   ε-left, ε-right   — Groups.V4.Axioms.ε-identity (as the two projections)
--   selfinv           — Groups.V4.Axioms.inv-left, since `inv x = x`
--                       DEFINITIONALLY (Operations.inv), so
--                       inv-left : (inv x · x) ≡ ε  IS  (x · x) ≡ ε.
------------------------------------------------------------------------

module Substrate.Algebra.Abelian.V4-as-PFG-Applied where

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.V4.Operations using (_·_; ε)
open import Substrate.Groups.V4.Axioms.Assoc using (·-assoc)
open import Substrate.Groups.V4.Axioms.Comm using (·-comm)
open import Substrate.Groups.V4.Axioms.EpsilonLeft using (ε-left)
open import Substrate.Groups.V4.Axioms.EpsilonRight using (ε-right)
open import Substrate.Groups.V4.Axioms.InvLeft using (inv-left)
open import Substrate.Foundation.Eq using (_≡_)

-- inv-left : (inv x · x) ≡ ε, and inv x = x definitionally ⇒ (x · x) ≡ ε.
selfinv : (x : V₄) → (x · x) ≡ ε
selfinv = inv-left



open import Substrate.Algebra.Abelian.V4-as-PFG
  V₄ _·_ ε ·-assoc ε-left ε-right selfinv ·-comm
  public
-- `v4-AbelianPFG : AbelianPFG V₄ V₄ _·_ ε _≡_ _≡_ 1` is now a CLOSED term:
-- the CDSW gauge as a bona-fide substrate AbelianPFG, no parameters left.
