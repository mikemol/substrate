------------------------------------------------------------------------
-- Substrate.Category.AutomorphismGroup.AsFunctor
--
-- Substrate-level naming of Aut(_) as a functor.
--
-- N1 of the N-arc (first slice of the second coherence iteration).
--
-- Z2 AutomorphismGroup is parametric on (V, Preserves); the assignment
-- "carrier V ↦ group Aut(V)" is functorial in V (in the appropriate
-- subcategory respecting Preserves). Per [[grothendieck-coherence-
-- rule]]: this assignment was a hidden orphan after the Z-arc; N1
-- closes it by naming Aut as an M1 Functor.
--
-- Module-parametric per substrate convention. The functor's source
-- (= category of carriers + preservation-respecting morphisms) and
-- target (= category of groups + group homs) are user-supplied as
-- CategoryOf instances; the substrate names the identification.
--
-- HIGH PRIORITY orphan per the M-arc's [[OrphanAudit]]; load-bearing
-- because Z2 Aut(_) is the universal-property mechanism for Z9
-- Monster.AsAutGriess and similar identifications.
--
-- Per [[universal-property-discipline]]: Aut is the right adjoint
-- to the "free group on a set" functor (in a categorical-monoid
-- sense); the substrate's N1 names the functor, the adjunction
-- composes via #4 Adjunction primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Level using (Level)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

module Substrate.Category.AutomorphismGroup.AsFunctor
  {ℓOS ℓMS ℓOG ℓMG : Level}
  -- The category of carriers + preservation-respecting morphisms.
  (CarrierCat : CategoryOf {ℓOS} {ℓMS})
  -- The category of groups + group homomorphisms.
  (GroupCat : CategoryOf {ℓOG} {ℓMG})
  -- The Aut functor.
  (Aut : Functor CarrierCat GroupCat)
  where

------------------------------------------------------------------------
-- 1. Aut as the substrate's named automorphism-group functor.
------------------------------------------------------------------------

Aut-Functor : Functor CarrierCat GroupCat
Aut-Functor = Aut

------------------------------------------------------------------------
-- 2. Capstone — Aut as M1 Functor.
--
-- N1 of the N-arc. With N1 landed, Z2's "carrier ↦ Aut(carrier)"
-- assignment is a substrate Functor; the next Grothendieck lift sees
-- Aut as a fibration over the carrier category.
--
-- Per [[grothendieck-coherence-rule]]: closes the highest-priority
-- audit orphan (Aut was load-bearing for Z9 Monster.AsAutGriess).
--
-- Next: N2 CategoryOf.AsFunctor.
------------------------------------------------------------------------
