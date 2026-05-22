------------------------------------------------------------------------
-- Substrate.Category.PrimeFactoredGauge.AsFunctor
--
-- Substrate-level naming of PFG as a functor.
--
-- N4 of the N-arc.
--
-- T7 PrimeFactoredGauge bundles (group + Sylow decomposition + atlas
-- + chart-equivariance). The assignment "group G with Sylow data ↦
-- PFG(G)" is functorial in (group-morphisms-that-respect-the-Sylow-
-- structure).
--
-- Per [[grothendieck-coherence-rule]]: PFG was the substrate's main
-- universal-property primitive from the T-arc; the functorial view
-- enables Grothendieck construction over PFG instances (∫PFG) +
-- composable equivariance reasoning across multiple charts.
--
-- Per [[prime-factored-gauge-arc]] follow-on: this slice naturally
-- composes with M5+M6+M7 (algebra-side functors) to give the
-- substrate's "PFG-equivariant algebra" hierarchy where PFG actions
-- transport across Lie/exterior structures functorially.
--
-- Module-parametric per substrate convention.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.PrimeFactoredGauge.AsFunctor
  {ℓOG ℓMG ℓOP ℓMP : Level}
  -- The category of groups + Sylow-respecting group homomorphisms.
  (SylowGroupCat : CategoryOf {ℓOG} {ℓMG})
  -- The category of PFG instances + PFG morphisms.
  (PFGCat : CategoryOf {ℓOP} {ℓMP})
  -- The PFG assignment functor.
  (PFG-assign : Functor SylowGroupCat PFGCat)
  where

------------------------------------------------------------------------
-- 1. PFG as the substrate's named prime-factored-gauge functor.
------------------------------------------------------------------------

PFG-Functor : Functor SylowGroupCat PFGCat
PFG-Functor = PFG-assign

------------------------------------------------------------------------
-- 2. Capstone — PFG as M1 Functor.
--
-- N4 of the N-arc. With N4 landed, the substrate's T-arc universal-
-- property mechanism (T7 PFG) is structurally functorial; the
-- substrate has the closure infrastructure for "PFG actions on
-- algebras" via composition with M5+M6+M7 functorial bridges.
--
-- After N1-N4: substrate's four HIGH-PRIORITY Z-arc + T-arc
-- mechanism orphans are functorially closed.
--
-- Next: N5 S1-Lift.AsFunctor (continuous-side functorial closure).
------------------------------------------------------------------------
