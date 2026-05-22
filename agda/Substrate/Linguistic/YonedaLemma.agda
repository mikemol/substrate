------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaLemma
--
-- Y9 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The Yoneda lemma for the substrate's language category. States:
-- for any L, M : LanguageWitness, there's a bijection
--
--   PresheafMorphism (よ L) (よ M)  ↔  LanguageMorphism L M
--
-- Forward direction: α ↦ α.component L (id-morphism L).
-- Backward direction: f ↦ よ-presheaf-mor f.
--
-- The two are mutual inverses MODULO naturality (forward ∘ backward
-- gives identity on Hom up to ∘L-identityʳ from Y4; backward ∘
-- forward gives identity on PresheafMorphism only if α is natural,
-- which the substrate's minimal PresheafMorphism record doesn't
-- yet enforce). Per [[feedback-coalgebraic-not-consumer-driven]]
-- the full naturality witness is deferred; this slice provides the
-- forward∘backward proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaLemma where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws
  using (_≈M_; ∘L-identityʳ; basis-≈; carrier-≈)
open import Substrate.Linguistic.HomFunctor using (Hom-contra)
open import Substrate.Linguistic.YonedaEmbedding
  using (よ; PresheafMorphism; よ-presheaf-mor; component)

------------------------------------------------------------------------
-- 1. The Yoneda forward direction.
--
-- Given a natural transformation α : よ L ⇒ よ M, extract its
-- component at L applied to the identity morphism.
--
-- yoneda-forward α = α.component L (id-morphism L).
--
-- This IS a LanguageMorphism L M because よ M L = Hom-contra L M
-- = LanguageMorphism L M.
------------------------------------------------------------------------

yoneda-forward :
  {L M : LanguageWitness} →
  PresheafMorphism (よ L) (よ M) →
  LanguageMorphism L M
yoneda-forward {L} {M} α = component α L (id-morphism L)

------------------------------------------------------------------------
-- 2. The Yoneda backward direction.
--
-- Given a language morphism f : L → M, produce the natural
-- transformation よ L ⇒ よ M by post-composition (the Y8
-- よ-presheaf-mor lift).
------------------------------------------------------------------------

yoneda-backward :
  {L M : LanguageWitness} →
  LanguageMorphism L M →
  PresheafMorphism (よ L) (よ M)
yoneda-backward = よ-presheaf-mor

------------------------------------------------------------------------
-- 3. Forward ∘ Backward = identity on Hom (up to _≈M_).
--
-- For any f : Hom L M,
--   yoneda-forward (yoneda-backward f) ≈M f.
--
-- Calculation:
--   yoneda-forward (yoneda-backward f)
--     = yoneda-forward (よ-presheaf-mor f)
--     = component (よ-presheaf-mor f) L (id-morphism L)
--     = f ∘L (id-morphism L)
--     ≈M f                                [by ∘L-identityʳ]
------------------------------------------------------------------------

yoneda-forward-backward :
  {L M : LanguageWitness} (f : LanguageMorphism L M) →
  yoneda-forward (yoneda-backward f) ≈M f
yoneda-forward-backward f = ∘L-identityʳ f

------------------------------------------------------------------------
-- 4. The headline statement.
--
-- The Yoneda lemma's invertibility (forward direction): the language
-- morphism f IS recoverable from the natural transformation
-- yoneda-backward f. This is the substrate-internal Yoneda
-- reconstruction.
------------------------------------------------------------------------

yoneda-reconstruction :
  {L M : LanguageWitness} (f : LanguageMorphism L M) →
  yoneda-forward (yoneda-backward f) ≈M f
yoneda-reconstruction = yoneda-forward-backward

------------------------------------------------------------------------
-- 5. Worked example: Lojban's identity reconstructed.
--
-- The identity morphism id-Lojban : Lojban → Lojban is recoverable
-- from its Yoneda image via the reconstruction lemma.
------------------------------------------------------------------------

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)

reconstruction-id-lojban :
  yoneda-forward (yoneda-backward (id-morphism lojban-witness))
    ≈M id-morphism lojban-witness
reconstruction-id-lojban = yoneda-reconstruction (id-morphism lojban-witness)

------------------------------------------------------------------------
-- 6. Capstone for Y9.
--
-- The forward direction of the Yoneda bijection holds: every
-- language morphism f is recoverable from yoneda-backward f.
-- The reverse direction (backward ∘ forward = identity on
-- PresheafMorphism) requires the naturality condition on
-- PresheafMorphism, deferred per
-- [[feedback-coalgebraic-not-consumer-driven]].
--
-- Y10 capstones: each language is determined by its hom-set into
-- all others.
------------------------------------------------------------------------
