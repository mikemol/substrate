------------------------------------------------------------------------
-- Substrate.Linguistic.Compose
--
-- Y3 of the Yoneda-lift arc per [scratch/yoneda_lift_arc_plan.md].
--
-- Composition of LanguageMorphism. Given f : L₁ → L₂ and g : L₂ →
-- L₃, produce g ∘L f : L₁ → L₃ with basis-map and carrier-map
-- composed, and η-coherence derived from f's and g's η-coherence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Compose where

open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; cong)

open import Substrate.Category.FreeOverBasis using (LanguageWitness; η; structure)
open import Substrate.Linguistic.Morphism
  using (LanguageMorphism; mkLangMor;
         basis-map; carrier-map; η-coherence)

------------------------------------------------------------------------
-- 1. Composition operator.
--
-- g ∘L f reads "apply f first, then g" (standard categorical
-- convention). Basis-maps and carrier-maps compose function-wise;
-- η-coherence chains f's and g's coherences via trans + cong.
------------------------------------------------------------------------

infixr 9 _∘L_

_∘L_ :
  {L₁ L₂ L₃ : LanguageWitness} →
  LanguageMorphism L₂ L₃ →
  LanguageMorphism L₁ L₂ →
  LanguageMorphism L₁ L₃
_∘L_ {L₁} {L₂} {L₃} g f = mkLangMor
  (λ b → basis-map g (basis-map f b))
  (λ x → carrier-map g (carrier-map f x))
  coherent
  where
    coherent :
      (b : _) →
      carrier-map g (carrier-map f (η (structure L₁) b))
        ≡ η (structure L₃) (basis-map g (basis-map f b))
    coherent b =
      trans
        (cong (carrier-map g) (η-coherence f b))
        (η-coherence g (basis-map f b))

------------------------------------------------------------------------
-- 2. Capstone for Y3.
--
-- Composition is defined and produces a valid LanguageMorphism;
-- Y4 will verify the category laws (associativity, left/right
-- identity).
------------------------------------------------------------------------
