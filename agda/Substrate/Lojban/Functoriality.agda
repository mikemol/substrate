------------------------------------------------------------------------
-- Substrate.Lojban.Functoriality
--
-- L7 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Grothendieck coherence ([[feedback-grothendieck-coherence-rule]])
-- packaged as the half of the arc's entailment that ranges over
-- Selbri / Bridi / Cmavo. The L8 sibling slice closes the other
-- half (LojbanWord as a monoid homomorphism into semantics).
--
-- The entailment claim ([[project-linguistic-rosetta-arc]] §"Entailment"):
--
--   NAryMorphism(Selbri) × CoxeterWordAlgebra(LojbanWord)
--     ⊢ ∀ (e : LojbanFragment). WellTyped e × Functorial ⟦ e ⟧
--
-- This module discharges the "Functorial" conjunct:
--
--   (Fun-id)      interpret (bridi-postcompose id b) ≡ interpret b
--   (Fun-compose) interpret (bridi-postcompose (g ∘ f) b)
--                   ≡ interpret (bridi-postcompose g (bridi-postcompose f b))
--   (Cmavo-id)    apply-cmavo identity-cmavo respects interpret
--   (Cmavo-comp)  apply-cmavo (cw₂ ∘-cmavo cw₁) respects the chained
--                   application
--
-- All four are pointwise refl in the current minimal Sem universe;
-- L7's job is to give them functorial names so L9/L10 consumers can
-- cite the theorem rather than re-deriving it per use.
--
-- Per [[feedback-universal-property-discipline]]: this is the
-- universal-property side; instances cite it instead of unfolding.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Functoriality where

open import Substrate.Foundation.Nat using (ℕ)
open import Level using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong)

open import Substrate.Lojban.PlaceStructure
  using (Selbri; apply; selbri-postcompose;
         selbri-postcompose-id; selbri-postcompose-compose)
open import Substrate.Lojban.Bridi
  using (Bridi; mkBridi; selbri; args;
         bridi-postcompose; interpret; interpret-postcompose)
open import Substrate.Lojban.Cmavo
  using (CmavoWrapper; sem-op; apply-cmavo; identity-cmavo;
         _∘-cmavo_; interpret-apply-cmavo;
         apply-cmavo-compose)

private
  variable
    ℓA ℓB ℓC ℓD : Level
    n : ℕ

------------------------------------------------------------------------
-- 1. Functor laws for bridi-postcompose (identity).
--
-- Post-composing a bridi with the identity preserves its semantic
-- interpretation.
------------------------------------------------------------------------

bridi-postcompose-respects-id :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (b : Bridi n Sumti Sem) →
  interpret (bridi-postcompose (λ x → x) b) ≡ interpret b
bridi-postcompose-respects-id _ = refl

------------------------------------------------------------------------
-- 2. Functor laws for bridi-postcompose (composition).
--
-- Post-composing with (g ∘ f) gives the same interpretation as
-- first post-composing with f then with g.
------------------------------------------------------------------------

bridi-postcompose-respects-compose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} {Sem'' : Set ℓD} →
  (f : Sem → Sem') (g : Sem' → Sem'') (b : Bridi n Sumti Sem) →
  interpret (bridi-postcompose (λ x → g (f x)) b)
    ≡ interpret (bridi-postcompose g (bridi-postcompose f b))
bridi-postcompose-respects-compose _ _ _ = refl

------------------------------------------------------------------------
-- 3. Cmavo identity coherence.
--
-- The identity cmavo is the unit of cmavo composition under
-- interpretation.
------------------------------------------------------------------------

cmavo-id-coherent :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (b : Bridi n Sumti Sem) →
  interpret (apply-cmavo identity-cmavo b) ≡ interpret b
cmavo-id-coherent _ = refl

------------------------------------------------------------------------
-- 4. Cmavo composition coherence.
--
-- Applying cw₂ after cw₁ is equivalent to applying the composed
-- wrapper (cw₂ ∘-cmavo cw₁). This is the [[feedback-grothendieck-
-- coherence-rule]] obligation for the cmavo layer.
------------------------------------------------------------------------

cmavo-compose-coherent :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (cw₂ cw₁ : CmavoWrapper Sumti Sem) (b : Bridi n Sumti Sem) →
  interpret (apply-cmavo cw₂ (apply-cmavo cw₁ b))
    ≡ interpret (apply-cmavo (cw₂ ∘-cmavo cw₁) b)
cmavo-compose-coherent _ _ _ = refl

------------------------------------------------------------------------
-- 5. The packaged "Functor on Sem" record.
--
-- A bundle of the four coherences for export to L9/L10. Downstream
-- consumers can pattern-match this record rather than citing the
-- individual lemmas.
------------------------------------------------------------------------

-- Note: fun-compose is bundled at endomorphism level (Sem → Sem)
-- to keep the record fit in Set (ℓA ⊔ ℓB). The stronger
-- heterogeneous-codomain statement remains available as the
-- standalone lemma `bridi-postcompose-respects-compose` above.

record BridiFunctoriality
  {ℓA ℓB : Level} (Sumti : Set ℓA) (Sem : Set ℓB) : Set (ℓA ⊔ ℓB) where
  field
    fun-id :
      {n : ℕ} (b : Bridi n Sumti Sem) →
      interpret (bridi-postcompose (λ x → x) b) ≡ interpret b
    fun-compose :
      {n : ℕ} (f g : Sem → Sem) (b : Bridi n Sumti Sem) →
      interpret (bridi-postcompose (λ x → g (f x)) b)
        ≡ interpret (bridi-postcompose g (bridi-postcompose f b))
    cmavo-id :
      {n : ℕ} (b : Bridi n Sumti Sem) →
      interpret (apply-cmavo identity-cmavo b) ≡ interpret b
    cmavo-compose :
      {n : ℕ} (cw₂ cw₁ : CmavoWrapper Sumti Sem) (b : Bridi n Sumti Sem) →
      interpret (apply-cmavo cw₂ (apply-cmavo cw₁ b))
        ≡ interpret (apply-cmavo (cw₂ ∘-cmavo cw₁) b)

------------------------------------------------------------------------
-- 6. Canonical instance.
--
-- The lemmas above instantiate the record automatically — no
-- per-Sumti or per-Sem proof obligation is needed; the laws are
-- structural, holding for any choice of carrier.
------------------------------------------------------------------------

canonical-functoriality :
  {ℓA ℓB : Level} {Sumti : Set ℓA} {Sem : Set ℓB} →
  BridiFunctoriality Sumti Sem
canonical-functoriality = record
  { fun-id        = bridi-postcompose-respects-id
  ; fun-compose   = bridi-postcompose-respects-compose
  ; cmavo-id      = cmavo-id-coherent
  ; cmavo-compose = cmavo-compose-coherent
  }
