------------------------------------------------------------------------
-- Substrate.Category.CategoryOf.CategoryOf
--
-- Defines: CategoryOf, assoc, compose, id, left-id, mkCategoryOf, right-id
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Category.CategoryOf; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CategoryOf.CategoryOf where

open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Category.CategoryOf.Private
open import Substrate.Foundation.Eq
open import Substrate.Probability.MarkovCategory



------------------------------------------------------------------------
-- The CategoryOf record.
--
-- Parameterized by (⟡set1-rp-categoryof — carriers are params, not fields):
--   * Obj : Set ℓO — the objects (= instances of some substrate
--     primitive)
--   * Mor : Obj → Obj → Set ℓM — morphisms between objects
-- Bundles:
--   * id : (o : Obj) → Mor o o — identity morphism
--   * compose : ∀ {a b c} → Mor b c → Mor a b → Mor a c — composition
--   * left-id : ∀ {a b} (f : Mor a b) → compose (id b) f ≡ f
--   * right-id : ∀ {a b} (f : Mor a b) → compose f (id a) ≡ f
--   * assoc : ∀ {a b c d} (f : Mor a b) (g : Mor b c) (h : Mor c d) →
--             compose h (compose g f) ≡ compose (compose h g) f
--
-- Standard category-record structure. Each substrate primitive
-- instantiates it by supplying (Obj, Mor, id, compose) and proving
-- the laws.
------------------------------------------------------------------------

-- ⟡set1-rp-categoryof: Obj and Mor are PARAMETERS now — a Set-valued
-- field pins the record at Set (lsuc _), while carriers as params never
-- raise the sort (set1-carrier-always-parameterize; Site.agda precedent).
record CategoryOf (Obj : Set ℓO) (Mor : Obj → Obj → Set ℓM) : Set (ℓO ⊔ ℓM) where
  constructor mkCategoryOf
  field
    id       : (o : Obj) → Mor o o
    compose  : {a b c : Obj} → Mor b c → Mor a b → Mor a c
    left-id  : {a b : Obj} (f : Mor a b) → compose (id b) f ≡ f
    right-id : {a b : Obj} (f : Mor a b) → compose f (id a) ≡ f
    assoc    : {a b c d : Obj}
               (f : Mor a b) (g : Mor b c) (h : Mor c d) →
               compose h (compose g f) ≡ compose (compose h g) f

open CategoryOf public

------------------------------------------------------------------------
-- Capstone — category-of primitive in place.
--
-- Z5 of the 10-slice Z-arc. Closes Gap #1 (universal "no morphism
-- layer") from the Grothendieck-closure audit at the structural
-- level: any substrate primitive can now name its category by
-- instantiating CategoryOf.
--
-- Composed with Z3 GrothendieckConstruction: given a base category
-- (= CategoryOf instance) + a fiber (= primitive → CategoryOf
-- function), the Grothendieck construction's total category is
-- itself a CategoryOf instance.
--
-- Concrete instances expected (downstream):
--   * Cone-category over any base diagram (via Cone.Morphism Z6).
--   * GTorsor-category over any group (via GTorsor.Morphism Z7).
--   * Aut(_)-categories at every primitive layer.
--
-- Per [[universal-property-discipline]]: CategoryOf names the
-- universal property "objects + morphisms + composition laws" at
-- the substrate level. Specific primitive categories specialize.
--
-- Next: Z6 (concrete Cone.Morphism instance via Z1).
------------------------------------------------------------------------
