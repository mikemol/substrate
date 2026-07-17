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

open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; _++ᵤ_)
open import Substrate.Category.UniversalProperty.Category using (++ᵤ-assoc)
open import Substrate.Category.UniversalProperty.Presheaf using (UPPresheaf)

-- ⟡odecode-residues: InstancesAt is now MIGRATED to the Set₀ O-form as a FULL
-- UPPresheaf (was a bare `UPArrowP → Set` signature-stub reading per-object
-- SourceP/TargetP/WitnessP, which the O-form object does not carry). The faithful
-- O-form does NOT need the semantic evaluator: the FREE-category word-structure
-- (++ᵤ + its laws) supplies the contravariant action and the presheaf laws.

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. The "instances" presheaf (O-form, faithful): the CONTRAVARIANT
  --    morphisms-out-of-U presheaf. An "instance of U" = a morphism U → W of
  --    the site (the ways U participates as a source — the O-form of the old
  --    Source/Target/Witness span, now carried by Hom). The action restricts
  --    along t : V → U by PRECOMPOSITION (t ++ᵤ g), contravariant. pres-id is
  --    refl ([] ++ᵤ g = g); pres-∘ is ++ᵤ-assoc. A genuine UPPresheaf, no stub.
  ------------------------------------------------------------------------

  InstancesAt : UPPresheaf O Hom (λ U → Σ O (λ W → UPTerm O Hom U W))
  InstancesAt = record
    { action  = λ t (W , g) → W , (t ++ᵤ g)
    ; pres-id = λ (W , g) → refl
    ; pres-∘  = λ t u (W , g) → cong (W ,_) (++ᵤ-assoc u t g)
    }

------------------------------------------------------------------------
-- 2. Capstone for UP29.
--
-- The substrate's canonical instance-presheaf signature lands.
-- UP30 closes Phase 3.
------------------------------------------------------------------------
