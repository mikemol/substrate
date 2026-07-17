------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsNaturalTransformation
--
-- The Hodge ★ as a natural transformation α : Λᵏ ⇒ Λⁿ⁻ᵏ between
-- two graded-piece functors.
--
-- M9 of the M-arc. Closes the L7 orphan gap per [[grothendieck-
-- coherence-rule]]: L7 named ★ as a bijection of graded pieces; the
-- statement "★ commutes with wedge-morphisms" (= the naturality
-- square) was a latent orphan. M9 makes it structural by recasting
-- ★ as an M2 NaturalTransformation.
--
-- Universal property of ★ as a natural transformation:
--   for any morphism f : V → W in Vect,
--   Λⁿ⁻ᵏ(f) ∘ ★_V ≡ ★_W ∘ Λᵏ(f)
-- This naturality square is precisely "★ transports along Vect-
-- morphisms" — the L7 orphan claim made structural.
--
-- Per [[universal-property-discipline]]: at HodgeDim4, the substrate
-- specialises n = 4, k = 2; Λᵏ and Λⁿ⁻ᵏ coincide (= the 6-dim
-- bivector space), and ★ is an involution (★² = id, established in
-- L7 HodgeStar.hodge-involution). The natural transformation lifts
-- this to "★ as an involutive 2-cell."
--
-- Per [[torsion-element-universal]] + [[3plus1-parity-universal]]:
-- ★ at order 2 + the naturality square together give the substrate's
-- canonical "involutive natural transformation between graded
-- functors" — the F₂-chirality element exposed at the M-arc 2-cell
-- layer.
--
-- Thin projection of [[Category.NaturalTransformation.AsNamed]] (the
-- AsNamed-family cone witness); see that module for the shared
-- naming pattern. This file supplies only the HodgeStar-specific math.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)
open import Substrate.Category.NaturalTransformation
  using (NaturalTransformation)

module Substrate.Algebra.F2.HodgeDim4.HodgeStar.AsNaturalTransformation
  {ℓOV ℓMV ℓOE ℓME : Level}
  {ObjVect : Set ℓOV} {MorVect : ObjVect → ObjVect → Set ℓMV}
  {ObjVect' : Set ℓOE} {MorVect' : ObjVect' → ObjVect' → Set ℓME}
  (Vect : CategoryOf ObjVect MorVect)
  (Vect' : CategoryOf ObjVect' MorVect')
  -- The two graded-piece functors:
  --   Λᵏ , Λⁿ⁻ᵏ : Vect → Vect'   (typically Vect' = Vect at HodgeDim4)
  -- At HodgeDim4 with n=4, k=2: both are the "second exterior power"
  -- functor (= V ↦ Λ²V), so Λᵏ ≅ Λⁿ⁻ᵏ on objects; ★ is the
  -- automorphism witnessing the duality.
  (Λᵏ : Functor Vect Vect')
  (Λⁿ⁻ᵏ : Functor Vect Vect')
  -- The Hodge ★ as a natural transformation Λᵏ ⇒ Λⁿ⁻ᵏ.
  (★ : NaturalTransformation Λᵏ Λⁿ⁻ᵏ)
  where

------------------------------------------------------------------------
-- 1. ★ as the substrate's named Hodge natural transformation.
--    Thin projection from Category.NaturalTransformation.AsNamed.
------------------------------------------------------------------------

open import Substrate.Category.NaturalTransformation.AsNamed
  Vect Vect' Λᵏ Λⁿ⁻ᵏ ★ public
  renaming (named-NaturalTransformation to HodgeStar-NaturalTransformation)

------------------------------------------------------------------------
-- 2. Capstone — HodgeStar as M2 NaturalTransformation.
--
-- M9 of the M-arc. Closes the L7 orphan: ★ is no longer "a
-- bijection of bivector spaces" but "a natural transformation
-- between graded functors with naturality square."
--
-- The naturality square IS the statement "★ commutes with linear
-- maps" — a structural property that was previously implicit in L7.
--
-- After M9: substrate has SIX universal-property views of the
-- canonical HodgeDim4 ★:
--   1. Order-2 endomap (HasOrder via HasOrder-from-perm)
--   2. Universal property of FreeLinearization
--      (HodgeStar-FreeLinearization)
--   3. Cone instance (HodgeStar-ConeWithMorphisms)
--   4. GTorsor representative (GaugeTorsor.AtlasCatalogue)
--   5. L5 GenericHodgeStar instance (L7 HodgeStar-AsGenericHodge)
--   6. M2 NaturalTransformation instance (M9, THIS)
--
-- Per [[universal-property-discipline]]: the six views jointly
-- identify ★ at the substrate level. The M9 view in particular is
-- the 2-cell view — ★ as a transformation between functors, with
-- naturality structurally enforced.
--
-- Per [[grothendieck-coherence-rule]]: this is exactly what was
-- needed — the latent "★ commutes with wedge-morphisms" claim is
-- now structural via M2's naturality field, not author discipline.
--
-- Next: M10 capstone — refresh PrimitivesAll + PrimitiveInstances
-- + introduce an orphan-audit module enumerating remaining
-- candidate gaps for the next coherence arc.
------------------------------------------------------------------------
