------------------------------------------------------------------------
-- Substrate.Category.CategoryOf
--
-- The generic "category of substrate-primitive-X" enabler. Given a
-- primitive type P (= records of some substrate primitive) and a
-- morphism notion between P-instances, packages the category
-- structure as a single substrate object.
--
-- Z5 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on.
--
-- KEY STRUCTURAL CONTENT:
--
--   The substrate has many primitive RECORD types (Cone, GTorsor,
--   PFG, PresentedGroup, ConjugationCoalgebra, CCA, etc.). Each has
--   instances; the morphisms between instances are what Z1 Morphism
--   captures parametrically.
--
--   This primitive bundles "primitive type + morphisms + category
--   axioms" into "the category of P-instances" — making the
--   Grothendieck construction over any substrate primitive
--   substrate-internal.
--
-- Per [[universal-property-discipline]] + [[categorical-name-first]]:
-- "category of X" is the standard categorical name; this primitive
-- packages it as a substrate object.
--
-- Per [[expose-generator-not-orbit]]: rather than enumerating
-- specific morphism-categories per primitive (one for Cone, one for
-- GTorsor, etc.), this primitive captures the COMMON PATTERN —
-- substrate primitives are generators; their morphism categories
-- are derivable.
--
-- Substrate-pragmatic scope: stated equationally / axiomatically.
-- The full strict-2-category formalism is downstream
-- specialization.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.CategoryOf where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq
  using (_≡_; refl)

private
  variable
    ℓO ℓM : Level

------------------------------------------------------------------------
-- The CategoryOf record.
--
-- Bundles:
--   * Obj : Set ℓO — the objects (= instances of some substrate
--     primitive)
--   * Mor : Obj → Obj → Set ℓM — morphisms between objects
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

record CategoryOf : Set (lsuc (ℓO ⊔ ℓM)) where
  constructor mkCategoryOf
  field
    Obj      : Set ℓO
    Mor      : Obj → Obj → Set ℓM
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
