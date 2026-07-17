------------------------------------------------------------------------
-- Substrate.Linguistic.Interchange
--
-- B4 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- The bicategorical interchange law:
--
--   (β₁ ∘V α₁) ∘H (β₂ ∘V α₂) ≡ (β₁ ∘H β₂) ∘V (α₁ ∘H α₂)
--
-- For Language2Morphism, the law holds pointwise at every input;
-- the propositional-equality version at the record level requires
-- function extensionality. This slice provides:
--
--   1. The interchange-at-identity special case: when all four
--      input 2-cells are identity 2-cells, both sides reduce to
--      the identity 2-cell on the composed 1-cell (provable by
--      refl).
--   2. The pointwise statement at general 2-cells (not proven in
--      full; the proof is a chain-of-trans-and-cong manipulation
--      deferred per [[feedback-coalgebraic-not-consumer-driven]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Interchange where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.Compose using (_∘L_)
open import Substrate.Linguistic.IdMorphism using (id-morphism)
open import Substrate.Linguistic.Language2Morphism
  using (Language2Morphism; mk2Mor; basis-eq; carrier-eq; id-2mor)
open import Substrate.Linguistic.Vertical using (_∘V_)
open import Substrate.Linguistic.Horizontal using (_∘H_)

------------------------------------------------------------------------
-- 1. Interchange at identity 2-cells.
--
-- Take all four 2-cells as identity (id-2mor); both sides of the
-- interchange reduce to identity 2-cells on the composed 1-cells.
-- Pointwise refl at the basis-eq component.
------------------------------------------------------------------------

interchange-id-basis :
  {B₁ F₁ B₂ F₂ B₃ F₃ : Set}
  {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂} {L₃ : LanguageWitness B₃ F₃}
  (f : LanguageMorphism L₁ L₂) (h : LanguageMorphism L₂ L₃) →
  (b : _) →
  basis-eq
    ((id-2mor h ∘V id-2mor h) ∘H (id-2mor f ∘V id-2mor f)) b
    ≡
  basis-eq
    ((id-2mor h ∘H id-2mor f) ∘V (id-2mor h ∘H id-2mor f)) b
interchange-id-basis _ _ _ = refl

------------------------------------------------------------------------
-- 2. Pointwise interchange statement (general 2-cells).
--
-- Captured as a TYPE without proof; proving it requires
-- trans/cong-chain manipulation that's mechanical but lengthy.
-- Deferred for substrate-honesty.
------------------------------------------------------------------------

InterchangeStatement :
  {B₁ F₁ B₂ F₂ B₃ F₃ : Set}
  {L₁ : LanguageWitness B₁ F₁} {L₂ : LanguageWitness B₂ F₂} {L₃ : LanguageWitness B₃ F₃}
  -- Inner 2-cells at L₁ → L₂
  {f g h : LanguageMorphism L₁ L₂}
  -- Outer 2-cells at L₂ → L₃
  {f' g' h' : LanguageMorphism L₂ L₃}
  (α-in : Language2Morphism f g) (β-in : Language2Morphism g h)
  (α-out : Language2Morphism f' g') (β-out : Language2Morphism g' h') →
  Set
InterchangeStatement α-in β-in α-out β-out =
  ∀ b →
    basis-eq ((β-out ∘V α-out) ∘H (β-in ∘V α-in)) b
      ≡ basis-eq ((β-out ∘H β-in) ∘V (α-out ∘H α-in)) b

------------------------------------------------------------------------
-- 3. Capstone for B4.
--
-- Interchange at identity 2-cells is refl-provable; the general
-- pointwise interchange holds (and is the bicategorical coherence
-- law) but the full chain-equation proof is deferred. B5 builds
-- the BicategoryOfLanguages record using the interchange law as
-- one of its fields (instantiable with the partial discharge here).
------------------------------------------------------------------------
