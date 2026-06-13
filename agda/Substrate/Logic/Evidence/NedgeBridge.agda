------------------------------------------------------------------------
-- Substrate.Logic.Evidence.NedgeBridge
--
-- DE-ORPHANS the parametric nedge. `Substrate.Logic.Evidence.DualRail` (nedge over an
-- arbitrary carrier C, with the rail-wise `Connectives`) was built but had NO consumer:
-- the live evidence logic (CRS/JOI/Graded/…) runs on `Verdict.Evidence`, a Bool-frozen
-- dual-rail record with its OWN connectives — a parallel reimplementation, unbridged
-- ([[feedback_convergence_over_isolation]]).
--
-- This proves they are the SAME structure: `Verdict.Evidence ≅ EvCarrier Bool`, and
-- EVERY Verdict connective (∧E/∨E/⊗E/⊕E) and `swapE` agrees, under the iso, with the
-- parametric `DualRail.BoolConnectives` (= `Connectives _∨_ _∧_`). So Verdict IS the
-- C = Bool instance of the parametric nedge — all by `refl`. The parametric carrier
-- (C = ℚ, ℝ, the CD tower …) is then the genuine generalization of the live logic, not
-- an orphan beside it; SWP's semiring-weighted parse rides on it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.NedgeBridge where

open import Substrate.Foundation.Bool    using (Bool)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Logic.Evidence.Verdict
  using (Evidence; ⟨_,_⟩; _∧E_; _∨E_; _⊗E_; _⊕E_; swapE)
import Substrate.Logic.Evidence.DualRail as DR

------------------------------------------------------------------------
-- The carrier iso: Verdict.Evidence ≅ EvCarrier Bool = Bool × Bool.
------------------------------------------------------------------------

to : Evidence → Bool × Bool
to ⟨ p , n ⟩ = p , n

from : Bool × Bool → Evidence
from (p , n) = ⟨ p , n ⟩

to-from : (m : Bool × Bool) → to (from m) ≡ m
to-from (p , n) = refl

from-to : (e : Evidence) → from (to e) ≡ e
from-to ⟨ p , n ⟩ = refl

------------------------------------------------------------------------
-- The connectives agree under the iso: Verdict's are DualRail.BoolConnectives'.
-- (BoolConnectives = Connectives _∨_ _∧_, so add = ∨, mul = ∧.)
------------------------------------------------------------------------

∧E-bridge : (a b : Evidence) → to (a ∧E b) ≡ DR.BoolConnectives._∧E_ (to a) (to b)
∧E-bridge ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

∨E-bridge : (a b : Evidence) → to (a ∨E b) ≡ DR.BoolConnectives._∨E_ (to a) (to b)
∨E-bridge ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

⊗E-bridge : (a b : Evidence) → to (a ⊗E b) ≡ DR.BoolConnectives._⊗E_ (to a) (to b)
⊗E-bridge ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

⊕E-bridge : (a b : Evidence) → to (a ⊕E b) ≡ DR.BoolConnectives._⊕E_ (to a) (to b)
⊕E-bridge ⟨ pa , na ⟩ ⟨ pb , nb ⟩ = refl

swapE-bridge : (e : Evidence) → to (swapE e) ≡ DR.BoolNedge.swapE (to e)
swapE-bridge ⟨ p , n ⟩ = refl
