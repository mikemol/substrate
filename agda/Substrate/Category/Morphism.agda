------------------------------------------------------------------------
-- Substrate.Category.Morphism
--
-- The generic morphism primitive: a function between two carriers
-- together with a parametric preservation predicate.
--
-- Z1 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on (per the user's "where does
-- the system lack Grothendieck closure" audit).
--
-- KEY STRUCTURAL CONTENT:
--
--   Different substrate primitives have different "morphism" notions:
--     * Cone: cone-morphism preserves apex + legs
--     * GTorsor: torsor-morphism is G-equivariant
--     * PFG: PFG-morphism is gauge-equivariant + Sylow-respecting
--     * CommutativeNonAssociativeAlgebra: algebra-hom preserves
--       product + bilinear form
--     * etc.
--
--   This primitive provides the COMMON SHAPE: a function + a
--   user-supplied preservation predicate. Each downstream primitive
--   defines its own preservation predicate and consumes Morphism
--   to package its morphisms.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "morphism in a concrete category" is the standard categorical name;
-- this primitive captures the function + preservation universal
-- property at the substrate level.
--
-- Per [[composable-primitives-over-flat-enumeration]]: the Preserves
-- predicate is parametric, so concrete morphism categories (cone-
-- category, torsor-category, etc.) compose cleanly from Morphism +
-- primitive-specific preservation.
--
-- Without Z1, the substrate's upper categorical primitives (Cone,
-- GTorsor, PFG, CCA, etc.) lack inter-instance morphisms, blocking
-- Grothendieck construction across the board.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Morphism where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

private
  variable
    ℓX ℓY ℓP : Level

------------------------------------------------------------------------
-- 1. The Morphism record.
--
-- Parameters:
--   * X : Set ℓX — source carrier
--   * Y : Set ℓY — target carrier
--   * Preserves : (X → Y) → Set ℓP — predicate on functions that the
--     morphism must satisfy
--
-- Fields:
--   * apply : X → Y — the function itself
--   * preserves : Preserves apply — the structural-preservation
--     witness
--
-- For each downstream primitive, the user supplies Preserves
-- specific to that primitive's structure. E.g.:
--   * For Cone-Morphism: Preserves f = "f maps apex to apex and
--     respects legs"
--   * For GTorsor-Morphism: Preserves f = "f commutes with G-action"
--   * For Algebra-Morphism: Preserves f = "f respects · and ⟨_,_⟩"
------------------------------------------------------------------------

record Morphism
  (X : Set ℓX)
  (Y : Set ℓY)
  (Preserves : (X → Y) → Set ℓP) : Set (ℓX ⊔ ℓY ⊔ ℓP) where
  constructor mkMorphism
  field
    apply     : X → Y
    preserves : Preserves apply

open Morphism public

------------------------------------------------------------------------
-- 2. Identity morphism.
--
-- For any X with a "trivially preserves itself" predicate, the
-- identity function is a morphism. The user supplies the
-- preservation witness for the identity.
------------------------------------------------------------------------

id-Morphism :
  {X : Set ℓX}
  (Preserves : (X → X) → Set ℓP)
  (id-preserves : Preserves (λ x → x)) →
  Morphism X X Preserves
id-Morphism Preserves id-preserves = mkMorphism (λ x → x) id-preserves

------------------------------------------------------------------------
-- 3. Composition.
--
-- Compose two morphisms when the preservation predicates compose
-- (which they typically do: if f preserves and g preserves, then
-- g ∘ f preserves — this is the COMMON case for structure-
-- preserving maps).
--
-- The user supplies the composition lemma for their specific
-- Preserves predicate; the substrate provides the structural
-- composition.
------------------------------------------------------------------------

compose-Morphism :
  {X : Set ℓX} {Y : Set ℓY} {Z : Set ℓX}
  {PreservesXY : (X → Y) → Set ℓP}
  {PreservesYZ : (Y → Z) → Set ℓP}
  {PreservesXZ : (X → Z) → Set ℓP}
  (composes :
    (f : X → Y) (g : Y → Z) →
    PreservesXY f → PreservesYZ g →
    PreservesXZ (λ x → g (f x))) →
  Morphism X Y PreservesXY →
  Morphism Y Z PreservesYZ →
  Morphism X Z PreservesXZ
compose-Morphism composes m₁ m₂ = mkMorphism
  (λ x → apply m₂ (apply m₁ x))
  (composes (apply m₁) (apply m₂) (preserves m₁) (preserves m₂))

------------------------------------------------------------------------
-- 4. Capstone — generic morphism primitive in place.
--
-- Z1 of the 10-slice Grothendieck-closure arc. Foundational for
-- Z6 (Cone.Morphism), Z7 (GTorsor.Morphism), Z8/Z9 (concrete
-- instances), and ultimately Z3 (GrothendieckConstruction) +
-- Z5 (CategoryOf) which compose morphism layers into full
-- categorical structure.
--
-- Each downstream primitive's morphism category:
--   1. Defines its Preserves predicate
--   2. Constructs its identity-preserves witness
--   3. Constructs its preservation-composition lemma
--   4. Inherits the rest from this Morphism primitive
--
-- This is the substrate's universal morphism shape — enables
-- Grothendieck closure at any layer once a primitive defines its
-- Preserves.
------------------------------------------------------------------------
