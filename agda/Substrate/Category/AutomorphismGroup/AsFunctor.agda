------------------------------------------------------------------------
-- Substrate.Category.AutomorphismGroup.AsFunctor
--
-- Substrate-level naming of Aut(_) as a functor.
--
-- N1 of the N-arc (first slice of the second coherence iteration).
--
-- Z2 AutomorphismGroup is parametric on (V, Preserves). This slice
-- NAMES a user-supplied Aut : Functor (the assignment "carrier V ↦
-- group Aut(V)"); functoriality in V is the caller's obligation, not
-- built here. Per [[grothendieck-coherence-rule]]: this assignment
-- was a hidden orphan after the Z-arc; N1 closes it by naming Aut as
-- an M1 Functor.
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
-- Per [[universal-property-discipline]] (prose: classically Aut is
-- the right adjoint to the "free group on a set" functor in a
-- categorical-monoid sense). The right-adjoint framing is prose — no
-- Adjunction instance is constructed here; N1 only names the functor.
-- The adjunction would compose via the #4 Adjunction primitive.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level)

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
--
-- Thin projection from [[Category.Functor.AsNamed]] — the 1:N cone
-- witness for substrate-level Functor naming.
------------------------------------------------------------------------

open import Substrate.Category.Functor.AsNamed
  CarrierCat GroupCat Aut public
  renaming (named-Functor to Aut-Functor)

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
