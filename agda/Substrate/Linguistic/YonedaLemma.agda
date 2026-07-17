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

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws
  using (_≈M_; ∘L-identityʳ; basis-≈; carrier-≈)
open import Substrate.Linguistic.HomFunctor using (Hom-contra)
open import Substrate.Linguistic.YonedaEmbedding
  using (よ; PresheafMorphism; よ-presheaf-mor; よ-on-morphism)

------------------------------------------------------------------------
-- 1. The Yoneda forward direction.
--
-- Given a natural transformation α : よ L ⇒ よ M, extract its
-- component at L applied to the identity morphism.
--
-- yoneda-forward c α = c L (id-morphism L).
--
-- `component` moved from a FIELD to a PARAMETER of PresheafMorphism
-- (⟡rc-lang, W5-L4) — α no longer carries data to project (its body
-- is vestigial), so the component function `c` the caller built the
-- PresheafMorphism type at is threaded in explicitly instead.
--
-- This IS a LanguageMorphism L M because よ M L = Hom-contra L M
-- = LanguageMorphism L M.
------------------------------------------------------------------------

yoneda-forward :
  {L M : Lang} (c : (X : Lang) → よ L X → よ M X) →
  PresheafMorphism (よ L) (よ M) c →
  LanguageMorphism (witness-of L) (witness-of M)
yoneda-forward {L} c α = c L (id-morphism (witness-of L))

------------------------------------------------------------------------
-- 2. The Yoneda backward direction.
--
-- Given a language morphism f : L → M, produce the natural
-- transformation よ L ⇒ よ M by post-composition (the Y8
-- よ-presheaf-mor lift).
------------------------------------------------------------------------

yoneda-backward :
  {L M : Lang} (f : LanguageMorphism (witness-of L) (witness-of M)) →
  PresheafMorphism (よ L) (よ M) (よ-on-morphism f)
yoneda-backward = よ-presheaf-mor

------------------------------------------------------------------------
-- 3. Forward ∘ Backward = identity on Hom (up to _≈M_).
--
-- For any f : Hom L M,
--   yoneda-forward (yoneda-backward f) ≈M f.
--
-- Calculation:
--   yoneda-forward (よ-on-morphism f) (yoneda-backward f)
--     = yoneda-forward (よ-on-morphism f) (よ-presheaf-mor f)
--     = (よ-on-morphism f) L (id-morphism L)
--     = f ∘L (id-morphism L)
--     ≈M f                                [by ∘L-identityʳ]
------------------------------------------------------------------------

yoneda-forward-backward :
  {L M : Lang} (f : LanguageMorphism (witness-of L) (witness-of M)) →
  yoneda-forward (よ-on-morphism f) (yoneda-backward f) ≈M f
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
  {L M : Lang} (f : LanguageMorphism (witness-of L) (witness-of M)) →
  yoneda-forward (よ-on-morphism f) (yoneda-backward f) ≈M f
yoneda-reconstruction = yoneda-forward-backward

------------------------------------------------------------------------
-- 5. Worked example: Lojban's identity reconstructed.
--
-- The identity morphism id-Lojban : Lojban → Lojban is recoverable
-- from its Yoneda image via the reconstruction lemma.
------------------------------------------------------------------------

open import Substrate.Linguistic.Roster using (lojban)

reconstruction-id-lojban :
  yoneda-forward (よ-on-morphism (id-morphism (witness-of lojban))) (yoneda-backward (id-morphism (witness-of lojban)))
    ≈M id-morphism (witness-of lojban)
reconstruction-id-lojban = yoneda-reconstruction (id-morphism (witness-of lojban))

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
