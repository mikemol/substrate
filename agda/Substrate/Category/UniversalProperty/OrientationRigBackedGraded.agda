------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.OrientationRigBackedGraded — ⟡C2 (graded): register the
-- orientation-rig universal property as a Set₀ graded backing.
--
-- The flat OrientationRigBacked (BackedUP : Set₁) was blocked by the Set₁ ratchet. Here the SAME
-- proven content — LehmerPath is the initial rig-algebra, `foldR` the unique out (OrientationRigInitial),
-- identity instance `LehmerRig` (fold = id, OrientationRigInstance) — is a `BackedUPᴳ` (Set₀), so it
-- registers with ZERO Set₁ cost. Spec = Sol = LehmerPath (the graded carrier); the constructive solve =
-- foldR LehmerRig (= id); content = the two distinct LehmerPath-2 paths (fold-is-id ⇒ the candidate is a
-- genuine non-solution ⇒ non-vacuous). Routed THROUGH the witness tower's proven initiality.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.OrientationRigBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (_,_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationRigInitial using (foldR)
open import Substrate.WitnessTower.Wedge.OrientationRigInstance using (LehmerRig)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ; Contentfulᴳ)

-- the constructive universal arrow: solve = foldR LehmerRig (the initial ◂-catamorphism, = id).
orientationRig-arrowᴳ : UPArrowᴳ LehmerPath LehmerPath
orientationRig-arrowᴳ = mkUP (λ l → foldR LehmerRig l)

-- the orientation rig as a Set₀ graded backing (registration = this term typechecks).
orientationRig-backedᴳ : BackedUPᴳ LehmerPath LehmerPath
orientationRig-backedᴳ = record
  { arrowᴳ  = orientationRig-arrowᴳ
  ; content = 2 , ((start ◂ zero) ◂ zero) , ((start ◂ zero) ◂ (suc zero)) , λ ()
  }
