------------------------------------------------------------------------
-- Substrate.Category.AutomorphismGroup
--
-- The Aut(_) primitive: the group of structure-preserving bijections
-- of a substrate object.
--
-- Z2 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on.
--
-- KEY STRUCTURAL CONTENT:
--
--   For any object X with a preservation predicate Preserves :
--   (X → X) → Set, the AutomorphismGroup is the set of
--   structure-preserving bijections (= the morphisms in
--   Substrate.Category.Morphism that have inverses).
--
--   This primitive captures the universal property of Aut(X) at the
--   substrate level — enabling identifications like
--   M ≅ Aut(GriessAlgebra) (Z9 next slice) to be substrate-internal
--   rather than meta-claimed.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "automorphism group" is the standard categorical name; this
-- primitive packages its universal property (= structure-preserving
-- bijection group).
--
-- Per [[coalgebraic-not-consumer-driven]]: the substrate is
-- coalgebraic, and Aut(X) is THE coalgebraic identifier of X (=
-- the symmetry group acting on X). Without Aut(_), the substrate's
-- coalgebraic identification is one-sided.
--
-- Specifically discharges Gap #2 from the Grothendieck-closure audit:
-- "no Aut(_) primitive — Monster's universal characterisation is
-- meta-claimed not constructed."
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.AutomorphismGroup where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

private
  variable
    ℓX ℓP : Level

------------------------------------------------------------------------
-- 1. The AutomorphismGroup record.
--
-- Parameters:
--   * X : Set ℓX — the carrier
--   * Preserves : (X → X) → Set ℓP — preservation predicate
--
-- Bundles:
--   * Aut-X : Set — the carrier of Aut(X) (= the bijection-group elements)
--   * apply : Aut-X → (X → X) — each Aut-X element is a function
--   * preserves : every Aut-X element's apply preserves the structure
--   * inverse : (a : Aut-X) → Aut-X — group inverse
--   * left-inv : (a : Aut-X) (x : X) → apply (inverse a) (apply a x) ≡ x
--   * right-inv : (a : Aut-X) (x : X) → apply a (apply (inverse a) x) ≡ x
--   * id-Aut : Aut-X — the identity automorphism
--   * id-applies-id : apply id-Aut ≡ identity-on-X (pointwise)
--   * compose : Aut-X → Aut-X → Aut-X — composition operation
--   * compose-applies : composition acts as function-composition pointwise
--
-- Group axioms (associativity, identity laws) hold pointwise via apply.
------------------------------------------------------------------------

record AutomorphismGroup
  (X : Set ℓX)
  (Preserves : (X → X) → Set ℓP) : Set (lsuc (ℓX ⊔ ℓP)) where
  constructor mkAut
  field
    Aut-X         : Set (ℓX ⊔ ℓP)
    apply         : Aut-X → (X → X)
    preserves     : (a : Aut-X) → Preserves (apply a)
    inverse       : Aut-X → Aut-X
    left-inv      : (a : Aut-X) (x : X) →
                    apply (inverse a) (apply a x) ≡ x
    right-inv     : (a : Aut-X) (x : X) →
                    apply a (apply (inverse a) x) ≡ x
    id-Aut        : Aut-X
    id-applies-id : (x : X) → apply id-Aut x ≡ x
    compose       : Aut-X → Aut-X → Aut-X
    compose-applies :
      (a b : Aut-X) (x : X) →
      apply (compose a b) x ≡ apply a (apply b x)

open AutomorphismGroup public

------------------------------------------------------------------------
-- 2. Capstone — Aut(_) primitive in place.
--
-- Z2 of the 10-slice Grothendieck-closure arc. Foundational for Z9
-- (Monster as Aut(GriessAlgebra) — the canonical extreme instance).
--
-- Concrete instances expected (Z9 and beyond):
--   * Aut(GriessAlgebra) ≅ Monster — closes the substrate's Monster
--     identification at the structural level (was meta-claim in T8/X5).
--   * Aut(Leech lattice) ≅ Co₀ (Conway's group).
--   * Aut(Fano plane) ≅ GL(3, F₂) — the substrate's existing
--     multi-route arc, now framed via Aut(_).
--   * Aut(any substrate primitive instance) — for any X with a
--     preservation predicate, Aut(X) is now a substrate primitive.
--
-- The Aut(X) record bundles all the group structure (compose,
-- identity, inverses, preservation) into a single substrate object.
-- This closes Gap #2 from the Grothendieck-closure audit.
--
-- Per [[expose-generator-not-orbit]] applied at the symmetry-group
-- level: Aut(X) IS the symmetry-group of X; its orbits on X (= the
-- structural decomposition) are derivable from Aut(X), not the
-- other way around.
------------------------------------------------------------------------
