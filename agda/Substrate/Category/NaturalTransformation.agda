------------------------------------------------------------------------
-- Substrate.Category.NaturalTransformation
--
-- The categorical primitive for natural transformations α : F ⇒ G
-- between two functors F, G : C → D.
--
-- A natural transformation is an Obj-indexed family of morphisms
-- (= components) satisfying the naturality square:
--   for all f : Mor C a b,
--   G-mor f ∘ α a ≡ α b ∘ F-mor f
--
-- M2 of the M-arc. Foundation for M9 [[HodgeStar.AsNaturalTransformation]]
-- (★ as α : Λᵏ ⇒ Λⁿ⁻ᵏ on graded-pieces functors) and the 2-cell
-- structure of the M-arc's functor calculus.
--
-- Per [[categorical-name-first]]: "natural transformation" is THE
-- 2-cell primitive of Cat. The universal property: nat-transformations
-- form the morphisms of the functor category [C, D].
--
-- Per [[grothendieck-coherence-rule]]: natural transformations are
-- the mechanism for transporting structure across functors WHILE
-- respecting morphisms. ★ commuting with wedge-morphisms IS the
-- naturality square; failure of naturality = orphan transformation.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.NaturalTransformation where

open import Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans)

open import Substrate.Category.CategoryOf using (CategoryOf)
open import Substrate.Category.Functor using (Functor)

private
  variable
    ℓOC ℓMC ℓOD ℓMD : Level

------------------------------------------------------------------------
-- The NaturalTransformation record.
--
-- Bundles:
--   * components : ∀ a → Mor D (F-obj a) (G-obj a)
--   * naturality : for every f : Mor C a b,
--                  D.compose (G.F-mor f) (components a)
--                  ≡ D.compose (components b) (F.F-mor f)
--     (the "naturality square commutes")
------------------------------------------------------------------------

record NaturalTransformation
  {C : CategoryOf {ℓOC} {ℓMC}}
  {D : CategoryOf {ℓOD} {ℓMD}}
  (F G : Functor C D) : Set (ℓOC ⊔ ℓMC ⊔ ℓMD) where
  constructor mkNaturalTransformation

  private
    module C = CategoryOf C
    module D = CategoryOf D
    module F = Functor F
    module G = Functor G

  field
    components :
      (a : C.Obj) → D.Mor (F.F-obj a) (G.F-obj a)
    naturality :
      {a b : C.Obj} (f : C.Mor a b) →
      D.compose (G.F-mor f) (components a)
      ≡ D.compose (components b) (F.F-mor f)

------------------------------------------------------------------------
-- Identity natural transformation.
--
-- For any functor F : C → D, the identity nat-trans id-F : F ⇒ F has
-- components = id (F-obj a) and naturality is trivial (both sides
-- reduce to F-mor f via category laws — left and right unit laws on
-- D's identity).
------------------------------------------------------------------------

id-NaturalTransformation :
  {C : CategoryOf {ℓOC} {ℓMC}}
  {D : CategoryOf {ℓOD} {ℓMD}}
  (F : Functor C D) → NaturalTransformation F F
id-NaturalTransformation {D = D} F = mkNaturalTransformation
  (λ a → CategoryOf.id D (Functor.F-obj F a))
  (λ {a} {b} f →
    trans (CategoryOf.right-id D (Functor.F-mor F f))
          (sym (CategoryOf.left-id D (Functor.F-mor F f))))

------------------------------------------------------------------------
-- Capstone — NaturalTransformation primitive in place.
--
-- M2 of the M-arc. With M1 + M2 landed, the substrate has 1-cell
-- (functor) + 2-cell (natural transformation) infrastructure for
-- its category-theoretic layer.
--
-- After M2:
--   * Functors compose (M1 compose-Functor)
--   * Nat-transformations have identity (M2 id-NaturalTransformation)
--   * Vertical composition of nat-transformations + horizontal
--     composition (= the strict 2-category structure of Cat) follows
--     mechanically from M1 + M2 (downstream slice if needed)
--
-- Per [[universal-property-discipline]]: this primitive captures
-- the 2-cell universal property — "the natural way one functor
-- transforms into another, respecting all morphisms."
--
-- Per [[grothendieck-coherence-rule]]: M9 uses M2 to recast HodgeStar
-- ★ as the natural transformation between Λᵏ and Λⁿ⁻ᵏ functors;
-- the naturality square IS the statement "★ commutes with wedge-
-- morphisms," which was a latent orphan in L7.
--
-- Next: M3 SymmetricMonoidal (tensor + symmetry structure).
------------------------------------------------------------------------
