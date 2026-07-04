{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.NuRegistryEntry — ⟡nu-registry-entry: register
-- the ν EXISTENCE-SOLVER (nu-backed, 169) onto the registry. Unlike the mechanical
-- conses (mu/count/shape), nu-backed is PARAMETRIC over a WedgeCoalg ℕ-div (its divide
-- IS the unfold), so registering it needs a CONCRETE coalgebra — built here from the
-- substrate's own construct-wedge (the deterministic DivMod unfold) + ℕ's decidable
-- equality, then fed to nu-backed and consed.
--
-- GROUNDED (not invented): construct-wedge a b : N.Wedge a (suc b) (the DivMod unfold);
-- fromℕ-Wedge bridges N.Wedge → Wedge ℕ-div; at b=0, recon ℕ-div 0 0 a = 0*0+a = a
-- (definitionally), so the b=0 wedge is direct (quot=0, rem=a, wedge-eq=refl). eq? = ℕ's
-- _≟_. This is THE canonical ℕ-div coalgebra: divide = the Euclidean division step.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.NuRegistryEntry where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_)
open import Substrate.Foundation.List using (List; _∷_)
open import Substrate.Algebra.Wedge using (DivStr; C; ℕ-div; fromℕ-Wedge) renaming (Wedge to Wedge⟦478f66a6⟧)
open import Substrate.Algebra.Nat.GCD.ConstructWedge using (construct-wedge)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP)
open import Substrate.Category.UniversalProperty.Registry using (registry)
import Substrate.Category.UniversalProperty.NuBacked as Nu

------------------------------------------------------------------------
-- ① THE b=0 wedge over ℕ-div: recon ℕ-div 0 0 a = 0*0+a = a (definitional), so a ≡ that.
------------------------------------------------------------------------
wedge-zero : (a : ℕ) → Wedge⟦478f66a6⟧ ℕ-div a 0
wedge-zero a = record { quot = 0 ; rem = a ; wedge-eq = refl }

------------------------------------------------------------------------
-- ② THE TOTAL divide: b=0 direct, suc b via construct-wedge (bridged). This is the
-- canonical ℕ-div Euclidean unfold — deterministic, total over all (a, b).
------------------------------------------------------------------------
ℕ-divide : (a b : ℕ) → Wedge⟦478f66a6⟧ ℕ-div a b
ℕ-divide a zero    = wedge-zero a
ℕ-divide a (suc b) = fromℕ-Wedge (construct-wedge a b)

------------------------------------------------------------------------
-- ③ THE CONCRETE ℕ-div COALGEBRA: divide + decidable residue equality.
------------------------------------------------------------------------
ℕ-coalg : WedgeCoalg ℕ-div
ℕ-coalg = record { divide = ℕ-divide ; eq? = _≟_ }

------------------------------------------------------------------------
-- ④ nu-backed INSTANTIATED at ℕ-coalg + REGISTERED.
------------------------------------------------------------------------
nu-backed-ℕ : BackedUP
nu-backed-ℕ = Nu.nu-backed ℕ-coalg

nu-registry : List BackedUP
nu-registry = nu-backed-ℕ ∷ registry

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the ν solver registered, its coalgebra grounded): the
-- ν existence-solver (nu-backed, 169) was PARAMETRIC over a WedgeCoalg — the unfold it
-- solves with. Registering it needed the CONCRETE unfold, and that unfold is the
-- substrate's OWN Euclidean division step (construct-wedge, the DivMod bridge; direct at
-- b=0). So ℕ-coalg = the canonical ℕ-div coalgebra, nu-backed-ℕ = the ν solver at it, and
-- nu-registry cons's it — the ν unfold joins μ (fold), shape, count, and the deferred
-- list as a registered solver. The "abstract parametric solver vs concrete registered
-- entry" either/or dissolves: the parameter is discharged by the substrate's real unfold
-- (grounded, not invented), and registration is the solver's existence re-presented as a
-- compiling entry. μ (fold, ≡-unique) ⊣ ν (unfold, bisim-unique) are NOW BOTH registered
-- concretely — the fold⊣unfold adjunction's two ends, both in the registry.
------------------------------------------------------------------------
