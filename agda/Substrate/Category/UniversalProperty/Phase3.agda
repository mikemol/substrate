------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Phase3
--
-- UP30 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Phase-3 capstone: presheaves + sheaves on UPCategory.
--
-- ===================================================================
-- PHASE-3 SUMMARY (UP21-UP30)
-- ===================================================================
--
--   UP21  Presheaf.agda          UPPresheaf record + functoriality
--   UP22  Yoneda.agda            よ : UPArrow → UPPresheaf₁
--   UP23  Sheaf.agda             UPSheaf record (descent obligation)
--   UP24  MatchingFamily.agda    matching-family shape
--   UP25  Sheafify.agda          sheafification signature
--   UP26  ConstantSheaf.agda     constant-Presheaf at A
--   UP27  SheafPullback.agda     restriction-to-slice signature
--   UP28  InternalHom.agda       cartesian-closed [P,Q] signature
--   UP29  SubstrateSheaves.agda  InstancesAt sheaf signature
--   UP30  Phase3.agda            this file
--
-- Phase-4 (UP31-UP40) builds the Grothendieck topos.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Phase3 where

open import Substrate.Category.UniversalProperty.Presheaf          public
  using (UPPresheaf)
open import Substrate.Category.UniversalProperty.Yoneda            public
  using (よ)
open import Substrate.Category.UniversalProperty.Sheaf             public
  using (UPSheaf)
open import Substrate.Category.UniversalProperty.MatchingFamily    public
  using (MatchingFamily)
open import Substrate.Category.UniversalProperty.Sheafify          public
  using (SheafifyType)
open import Substrate.Category.UniversalProperty.ConstantSheaf     public
  using (constant-Presheaf)
open import Substrate.Category.UniversalProperty.SheafPullback     public
  using (PullbackToSlice)
open import Substrate.Category.UniversalProperty.InternalHom       public
  using (InternalHomType)
open import Substrate.Category.UniversalProperty.SubstrateSheaves  public
  using (InstancesAt)
