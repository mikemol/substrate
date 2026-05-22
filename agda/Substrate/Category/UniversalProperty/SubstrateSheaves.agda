------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.SubstrateSheaves
--
-- UP29 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Substrate-relevant sheaves on UPCategory.
--
-- The canonical example: the "instances-of-UP" sheaf. For each
-- UPArrow U, F(U) is the set of (Source U × Target U)-pairs
-- satisfying Witness U. A UPTerm V → U restricts an instance from
-- U to an instance at V via the source-map / target-map.
--
-- Whether the descent condition holds depends on the cover; for
-- the trivial cover it holds vacuously. Concrete covers (FLQ-style
-- linear-extension covers, modular covers, ...) realise the
-- substrate's structural cohomology = the sheaf cohomology of the
-- instance-sheaf on UPCategory.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.SubstrateSheaves where

open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.UniversalProperty
  using (UPArrow; Source; Target; Witness)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)

------------------------------------------------------------------------
-- 1. The "instances" presheaf.
--
-- F(U) = Σ (s : Source U) (i : Target U). Witness U s i
--
-- The action is contravariant: given t : V → U, restrict an
-- instance at U to an instance at V via the substrate's UPMorphism
-- source-map (forward on spec) + target-map (back on instance).
--
-- Substrate-honest: the action's full implementation needs the
-- semantic evaluator (UP3); we package the SHAPE here and signal
-- the obligation via record discipline.
------------------------------------------------------------------------

InstancesAt : UPArrow → Set
InstancesAt U = Σ (Source U) (λ s → Σ (Target U) (Witness U s))

-- Note: a full presheaf requires `action` and `pres-*` proofs that
-- depend on the UPMorphism evaluator. The signature lands here;
-- concrete instances connect at the post-Phase-4 specialisation.

------------------------------------------------------------------------
-- 2. Capstone for UP29.
--
-- The substrate's canonical instance-presheaf signature lands.
-- UP30 closes Phase 3.
------------------------------------------------------------------------
