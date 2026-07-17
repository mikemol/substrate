------------------------------------------------------------------------
-- Substrate.Linguistic.YonedaNatural
--
-- B7 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Shows that Y8's `よ-presheaf-mor f` produces a NATURAL
-- transformation for every language morphism f : L → M.
--
-- Naturality at the component level says: for any g : X → Y and
-- h : Hom(Y, L),
--   yoneda-mor-component f X (h ∘L g) ≡ (yoneda-mor-component f Y h) ∘L g
--
-- Where yoneda-mor-component f Y h = f ∘L h. So:
--   LHS: f ∘L (h ∘L g)
--   RHS: (f ∘L h) ∘L g
-- Equal up to associativity of ∘L.
--
-- The PROPOSITIONAL equality requires the η-coherence proofs in
-- the two sides to match. Since substrate's ∘L is associative
-- definitionally on basis-map / carrier-map (they're both function
-- composition), but the η-coherence is a constructed trans+cong
-- chain that differs, full propositional equality requires either
-- proof-irrelevance on η-coherence or to state up to _≈M_.
--
-- This slice states naturality up to _≈M_ (the bicategorical-
-- friendly form), which closes the Y9 reverse-direction
-- deferral in B8.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.YonedaNatural where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Linguistic.Roster using (Lang; witness-of)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.CategoryLaws
  using (_≈M_; ∘L-assoc)
open import Substrate.Linguistic.YonedaEmbedding using (よ)

------------------------------------------------------------------------
-- 1. The Yoneda morphism's component.
--
-- For f : L → M, the component at X is post-composition by f.
------------------------------------------------------------------------

yoneda-component :
  {L M : Lang}
  (f : LanguageMorphism (witness-of L) (witness-of M))
  (X : Lang) →
  よ L X → よ M X
yoneda-component f X h = f ∘L h

------------------------------------------------------------------------
-- 2. Naturality up to _≈M_.
--
-- For g : X → Y and h : Hom(Y, L),
--   yoneda-component f X (h ∘L g) ≈M yoneda-component f Y h ∘L g
-- i.e., f ∘L (h ∘L g) ≈M (f ∘L h) ∘L g
-- which is the associativity law from Y4 (∘L-assoc), in reverse.
------------------------------------------------------------------------

open import Substrate.Linguistic.CategoryLaws using (basis-≈; carrier-≈)

yoneda-naturality-≈M :
  {L M : Lang}
  (f : LanguageMorphism (witness-of L) (witness-of M))
  {X Y : Lang}
  (g : LanguageMorphism (witness-of X) (witness-of Y))
  (h : よ L Y) →
  yoneda-component f X (h ∘L g) ≈M yoneda-component f Y h ∘L g
yoneda-naturality-≈M f g h = record
  { basis-≈   = λ _ → refl
  ; carrier-≈ = λ _ → refl
  }

------------------------------------------------------------------------
-- 3. Capstone for B7.
--
-- The Yoneda backward map produces naturally-transforming
-- presheaf morphisms (up to _≈M_). B8 uses this to close the
-- Y9 reverse-direction deferral: starting from a natural
-- α : よ L ⇒ よ M, recover the language morphism L → M whose
-- yoneda-backward equals α.
------------------------------------------------------------------------
