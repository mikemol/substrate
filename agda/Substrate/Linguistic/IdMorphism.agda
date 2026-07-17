------------------------------------------------------------------------
-- Substrate.Linguistic.IdMorphism
--
-- Y2 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- The identity morphism for each LanguageWitness. basis-map = id,
-- carrier-map = id, η-coherence by refl. Every language has a
-- canonical self-morphism, which is the unit of the category-of-
-- languages.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.IdMorphism where

open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism; mkLangMor)

------------------------------------------------------------------------
-- 1. The identity morphism construction.
--
-- For any L, id-morphism L : LanguageMorphism L L. Both basis-map
-- and carrier-map are λ x → x; η-coherence holds by refl.
------------------------------------------------------------------------

id-morphism : {B F : Set} (L : LanguageWitness B F) → LanguageMorphism L L
id-morphism L = mkLangMor
  (λ b → b)
  (λ x → x)
  (λ _ → refl)

------------------------------------------------------------------------
-- 2. Concrete identity instances for the six witnesses.
--
-- Each language's self-morphism made available by name. Smoke
-- tests demonstrate the construction works on all six.
------------------------------------------------------------------------

open import Substrate.Lojban.AsFreeOverBasis using (lojban-witness)
open import Substrate.TokiPona.AsFreeOverBasis using (tokipona-witness)
open import Substrate.Solresol.Fragment using (solresol-witness)
open import Substrate.Kelen.Fragment using (kelen-witness)
open import Substrate.Lambda.Fragment using (lambda-witness)
open import Substrate.Invented.LieFragment using (lie-witness)

id-lojban : LanguageMorphism lojban-witness lojban-witness
id-lojban = id-morphism lojban-witness

id-tokipona : LanguageMorphism tokipona-witness tokipona-witness
id-tokipona = id-morphism tokipona-witness

id-solresol : LanguageMorphism solresol-witness solresol-witness
id-solresol = id-morphism solresol-witness

id-kelen : LanguageMorphism kelen-witness kelen-witness
id-kelen = id-morphism kelen-witness

id-lambda : LanguageMorphism lambda-witness lambda-witness
id-lambda = id-morphism lambda-witness

id-lie : LanguageMorphism lie-witness lie-witness
id-lie = id-morphism lie-witness

------------------------------------------------------------------------
-- 3. Capstone for Y2.
--
-- Identity morphisms exist for every language. Y4 will verify
-- they're the unit of composition (Y3).
------------------------------------------------------------------------
