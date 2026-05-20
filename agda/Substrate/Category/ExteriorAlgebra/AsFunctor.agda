------------------------------------------------------------------------
-- Substrate.Category.ExteriorAlgebra.AsFunctor
--
-- Substrate-level naming of Λ as a functor Vect → ExtAlg.
--
-- M5 of the M-arc. Closes the L3-orphan gap identified by the
-- [[grothendieck-coherence-rule]]: L3 ExteriorAlgebra defines the
-- OBJECTS (= "an exterior algebra over V_base") but the ASSIGNMENT
-- V ↦ Λ(V) as a substrate-level functor was not named.
--
-- After M5: the substrate has the FUNCTOR Λ : Vect → ExtAlg as a
-- first-class M1 Functor instance, structurally enforceable per
-- [[grothendieck-coherence-rule]].
--
-- Module-parametric per substrate convention:
--   * Vect : CategoryOf — the source category (typically: vector
--     spaces + linear maps; user-supplied)
--   * ExtAlg : CategoryOf — the target category (typically:
--     ExteriorAlgebra records + L9 ExteriorAlgebra.Morphism;
--     user-supplied or constructed via a substrate
--     "ExteriorAlgebra.AsCategoryOf" slice — deferred)
--   * Λ : Functor Vect ExtAlg — the functor data
--
-- The substrate names the functor; the user supplies the categories
-- + the functor's object/morphism maps + laws. Per
-- [[coalgebraic-not-consumer-driven]]: the substrate's role is the
-- TYPE; the consumer's role is the construction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.ExteriorAlgebra.AsFunctor
  {ℓOV ℓMV ℓOE ℓME : Level}
  (Vect : CategoryOf {ℓOV} {ℓMV})
  (ExtAlg : CategoryOf {ℓOE} {ℓME})
  (Λ : Functor Vect ExtAlg)
  where

------------------------------------------------------------------------
-- 1. Λ as the substrate's named exterior-algebra functor.
------------------------------------------------------------------------

Λ-Functor : Functor Vect ExtAlg
Λ-Functor = Λ

------------------------------------------------------------------------
-- 2. Capstone — Λ as a substrate Functor.
--
-- M5 of the M-arc. With M5 landed, the substrate's L3
-- ExteriorAlgebra record + L9 ExteriorAlgebra.Morphism + M5 Λ-as-
-- Functor form the full functorial story:
--   L3: the objects of ExtAlg (= individual exterior algebras)
--   L9: the morphisms of ExtAlg (= wedge-preserving maps)
--   M5: the functor Λ producing ExtAlg-objects from Vect-objects
--
-- Together, these close the L3 orphan: V ↦ Λ(V) is now a substrate
-- functor, not just an unstructured assignment.
--
-- Per [[grothendieck-coherence-rule]]: the next Grothendieck lift
-- will see Λ as a fibration over Vect, not as an isolated record
-- bundle.
--
-- Per [[universal-property-discipline]]: Λ is the LEFT ADJOINT to
-- the forgetful functor ExtAlg → Vect (= take the V_base of each
-- exterior algebra). The adjunction (Λ ⊣ U_ExtAlg) is the
-- substrate's natural next slice after M5 (deferred).
--
-- Next: M6 LieAlgebra.AsFunctor (the underlying-Lie functor
-- Assoc → Lie).
------------------------------------------------------------------------
