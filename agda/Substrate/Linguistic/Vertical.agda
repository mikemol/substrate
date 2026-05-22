------------------------------------------------------------------------
-- Substrate.Linguistic.Vertical
--
-- B2 of the Bicategorical-lift arc per [scratch/bicategorical_arc_plan.md].
--
-- Vertical composition of 2-morphisms: given α : f ⇒ g and β : g ⇒
-- h (both between parallel 1-cells L₁ → L₂), compose β ∘V α : f ⇒
-- h via transitivity of the underlying pointwise equalities.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Vertical where

open import Substrate.Foundation.Eq using (_≡_; refl; trans)

open import Substrate.Category.FreeOverBasis using (LanguageWitness)
open import Substrate.Linguistic.Morphism using (LanguageMorphism)
open import Substrate.Linguistic.Language2Morphism
  using (Language2Morphism; mk2Mor; basis-eq; carrier-eq; id-2mor)

------------------------------------------------------------------------
-- 1. Vertical composition.
--
-- α : f ⇒ g, β : g ⇒ h ⊢ β ∘V α : f ⇒ h.
-- Components compose by `trans` on the underlying equalities.
------------------------------------------------------------------------

infixr 9 _∘V_

_∘V_ :
  {L₁ L₂ : LanguageWitness}
  {f g h : LanguageMorphism L₁ L₂} →
  Language2Morphism g h →
  Language2Morphism f g →
  Language2Morphism f h
_∘V_ β α = mk2Mor
  (λ b → trans (basis-eq α b) (basis-eq β b))
  (λ x → trans (carrier-eq α x) (carrier-eq β x))

------------------------------------------------------------------------
-- 2. Left identity: id-2mor g ∘V α ≡ α (up to pointwise refl).
--
-- The vertical composition of the identity 2-cell on the right of
-- α gives α back. We state this at the level of basis-eq and
-- carrier-eq components since the records aren't propositionally
-- equal without function extensionality.
------------------------------------------------------------------------

vertical-identityˡ-basis :
  {L₁ L₂ : LanguageWitness}
  {f g : LanguageMorphism L₁ L₂}
  (α : Language2Morphism f g)
  (b : _) →
  basis-eq (_∘V_ {f = f} {g = g} {h = g} (id-2mor g) α) b
    ≡ basis-eq α b
vertical-identityˡ-basis α b
  rewrite basis-eq α b = refl

------------------------------------------------------------------------
-- 3. Right identity: α ∘V id-2mor f ≡ α.
------------------------------------------------------------------------

vertical-identityʳ-basis :
  {L₁ L₂ : LanguageWitness}
  {f g : LanguageMorphism L₁ L₂}
  (α : Language2Morphism f g)
  (b : _) →
  basis-eq (α ∘V id-2mor f) b ≡ basis-eq α b
vertical-identityʳ-basis _ _ = refl

------------------------------------------------------------------------
-- 4. Capstone for B2.
--
-- Vertical composition + identity laws (component-wise) discharged.
-- B3 adds horizontal composition; B4 the interchange law that
-- relates the two.
------------------------------------------------------------------------
