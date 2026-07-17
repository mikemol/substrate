------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.CoverageAxioms
--
-- UP16 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The three Grothendieck pretopology axioms, stated explicitly at
-- the UPCategory level.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; homs are UPTerm O Hom.
-- (O, Hom) enter via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.CoverageAxioms where

open import Substrate.Foundation.Unit using (⊤)
open import Substrate.Category.UniversalProperty.Term using (UPTerm; [])
open import Substrate.Category.UniversalProperty.Coverage using (UPCover)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Identity axiom: the singleton {id_U : U → U} is a cover.
  --
  -- Substrate-honest: stated as a function producing such a cover.
  ------------------------------------------------------------------------

  singleton-id-Cover : (U : O) → UPCover O Hom U ⊤
  singleton-id-Cover U = record
    { src   = λ _ → U
    ; arrow = λ _ → []
    }

  -- ⟡rc-topos (⟡set1-rerank2): UPCover's `Idx` is now a PARAMETER, so the
  -- hollow `StabilityAxiom` / `TransitivityAxiom` obligation-placeholders
  -- (`= Set₁`, unconsumed anywhere) are DELETED; concrete pretopology
  -- obligations live at the sites that state them (Pretopology, Saturation).

------------------------------------------------------------------------
-- 4. Capstone for UP16.
--
-- The three axioms are stated. UP17 discharges identity by exhibiting
-- the singleton-id cover; UP18 the substrate's concrete UPCovers.
------------------------------------------------------------------------
