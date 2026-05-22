------------------------------------------------------------------------
-- Substrate.Category.Functor
--
-- The categorical primitive for functors F : C → D between two
-- substrate categories (Z5 CategoryOf instances).
--
-- A functor is an object-map + morphism-map preserving identity +
-- composition. Per [[grothendieck-coherence-rule]]: every substrate
-- "the assignment X ↦ S(X)" claim must instantiate this primitive
-- to escape orphan-status — record primitives like L3 ExteriorAlgebra
-- name the OBJECTS of the fiber but not the FUNCTOR that produces
-- them from the base.
--
-- M1 of the M-arc (functorial closure of the L-arc). Foundation for:
--   * M2 NaturalTransformation (morphisms of functors)
--   * M5 ExteriorAlgebra.AsFunctor (Λ : Vect → ExtAlg)
--   * M7 UniversalEnvelopingAlgebra.AsFunctor (U : Lie → Assoc)
--   * M8 Coxeter.AsCartanType.Functor (functorial upgrade of L13)
--   * M9 HodgeStar.AsNaturalTransformation (via M2)
--
-- Per [[categorical-name-first]]: "functor" / "covariant functor" /
-- "homomorphism of categories" are standard. The universal property
-- is "the carriers of a 2-category Cat whose 0-cells are categories,
-- 1-cells are functors, 2-cells are natural transformations" — M1
-- + M2 provide the 1-cell + 2-cell content; the strict 2-category
-- packaging is downstream.
--
-- Per [[universal-property-discipline]]: many existing substrate
-- assignments (Aut(_), CategoryOf(_), GrothendieckConstruction, …)
-- have HIDDEN FUNCTOR structure that this primitive lets us name
-- explicitly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Functor where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CategoryOf using (CategoryOf)

private
  variable
    ℓOC ℓMC ℓOD ℓMD : Level

------------------------------------------------------------------------
-- The Functor record.
--
-- Bundles:
--   * F-obj : Obj C → Obj D — object map
--   * F-mor : ∀ {a b} → Mor C a b → Mor D (F-obj a) (F-obj b) —
--     morphism map
--   * F-id  : ∀ a → F-mor (id C a) ≡ id D (F-obj a) — identity
--     preservation
--   * F-compose : ∀ {a b c} (f : Mor C a b) (g : Mor C b c) →
--                 F-mor (compose C g f) ≡ compose D (F-mor g) (F-mor f)
--                 — composition preservation
--
-- The two laws together establish that F respects the categorical
-- structure of C in D.
------------------------------------------------------------------------

record Functor
  (C : CategoryOf {ℓOC} {ℓMC})
  (D : CategoryOf {ℓOD} {ℓMD}) : Set (ℓOC ⊔ ℓMC ⊔ ℓOD ⊔ ℓMD) where
  constructor mkFunctor

  private
    module C = CategoryOf C
    module D = CategoryOf D

  field
    F-obj      : C.Obj → D.Obj
    F-mor      : {a b : C.Obj} → C.Mor a b → D.Mor (F-obj a) (F-obj b)
    F-id       : (a : C.Obj) → F-mor (C.id a) ≡ D.id (F-obj a)
    F-compose  : {a b c : C.Obj} (f : C.Mor a b) (g : C.Mor b c) →
                 F-mor (C.compose g f) ≡ D.compose (F-mor g) (F-mor f)

------------------------------------------------------------------------
-- Identity functor.
--
-- The functor C → C sending every object/morphism to itself; trivially
-- preserves identity + composition.
------------------------------------------------------------------------

open import Substrate.Foundation.Eq using (refl)

id-Functor : (C : CategoryOf {ℓOC} {ℓMC}) → Functor C C
id-Functor C = mkFunctor
  (λ a → a)
  (λ f → f)
  (λ _ → refl)
  (λ _ _ → refl)

------------------------------------------------------------------------
-- Composition of functors.
--
-- Given F : C → D and G : D → E, the composite G ∘F F : C → E sends
-- objects via G-obj ∘ F-obj and morphisms via G-mor ∘ F-mor.
------------------------------------------------------------------------

compose-Functor :
  {ℓOE ℓME : Level}
  {C : CategoryOf {ℓOC} {ℓMC}}
  {D : CategoryOf {ℓOD} {ℓMD}}
  {E : CategoryOf {ℓOE} {ℓME}}
  (G : Functor D E) (F : Functor C D) → Functor C E
compose-Functor {C = C} {D = D} {E = E} G F = mkFunctor
  (λ a → Functor.F-obj G (Functor.F-obj F a))
  (λ f → Functor.F-mor G (Functor.F-mor F f))
  id-pres
  comp-pres
  where
    module C = CategoryOf C
    module D = CategoryOf D
    module E = CategoryOf E
    module F = Functor F
    module G = Functor G

    open import Substrate.Foundation.Eq
      using (trans; cong)

    id-pres : (a : C.Obj) →
              G.F-mor (F.F-mor (C.id a)) ≡ E.id (G.F-obj (F.F-obj a))
    id-pres a = trans (cong G.F-mor (F.F-id a)) (G.F-id (F.F-obj a))

    comp-pres : {a b c : C.Obj} (f : C.Mor a b) (g : C.Mor b c) →
                G.F-mor (F.F-mor (C.compose g f))
                ≡ E.compose (G.F-mor (F.F-mor g)) (G.F-mor (F.F-mor f))
    comp-pres f g =
      trans (cong G.F-mor (F.F-compose f g))
            (G.F-compose (F.F-mor f) (F.F-mor g))

------------------------------------------------------------------------
-- Capstone — Functor primitive in place.
--
-- M1 of the M-arc. With M1 landed, the substrate can name "X ↦ S(X)"
-- assignments as proper functors with composition + identity
-- preservation, not just record-instance bundles.
--
-- After M1: hidden-orphan primitives from prior arcs become
-- recoverable as Functor instances. Concrete next steps:
--   * M5 Λ : Vect → ExtAlg
--   * M6 underlying-Lie : Assoc → Lie
--   * M7 U : Lie → Assoc
--   * M8 Coxeter ↦ Cartan functoriality
--
-- Per [[grothendieck-coherence-rule]]: this primitive is the
-- structural enforcement mechanism for "no orphan primitives" —
-- every assignment that should be functorial can now be REQUIRED
-- to instantiate Functor, or it stays an orphan.
--
-- Next: M2 NaturalTransformation.
------------------------------------------------------------------------
