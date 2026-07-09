------------------------------------------------------------------------
-- Substrate.Algebra.SetoidGroup.Properties
--
-- Derived properties of a SetoidGroup: inverse uniqueness, inverse
-- involution, etc. Substrate-native replacement for stdlib's
-- Algebra.Properties.Group.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.SetoidGroup.Properties where

open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

module Props (Carrier : Set) (_≈_ : Carrier → Carrier → Set)
             (G : SetoidGroup Carrier _≈_) where
  open SetoidGroup G

  ------------------------------------------------------------------
  -- inverseˡ-unique : if x ∙ y ≈ ε then x ≈ y ⁻¹.
  ------------------------------------------------------------------

  inverseˡ-unique :
    (x y : Carrier) → (x ∙ y) ≈ ε → x ≈ (y ⁻¹)
  inverseˡ-unique x y x∙y≈ε =
    let step1 : x ≈ (x ∙ ε)
        step1 = ≈-sym (ε-right x)
        step2 : (x ∙ ε) ≈ (x ∙ (y ∙ (y ⁻¹)))
        step2 = ∙-cong (≈-refl x) (≈-sym (inv-right y))
        step3 : (x ∙ (y ∙ (y ⁻¹))) ≈ ((x ∙ y) ∙ (y ⁻¹))
        step3 = ≈-sym (∙-assoc x y (y ⁻¹))
        step4 : ((x ∙ y) ∙ (y ⁻¹)) ≈ (ε ∙ (y ⁻¹))
        step4 = ∙-cong x∙y≈ε (≈-refl (y ⁻¹))
        step5 : (ε ∙ (y ⁻¹)) ≈ (y ⁻¹)
        step5 = ε-left (y ⁻¹)
    in ≈-trans step1
       (≈-trans step2
       (≈-trans step3
       (≈-trans step4 step5)))

  ------------------------------------------------------------------
  -- inverseʳ-unique : if x ∙ y ≈ ε then y ≈ x ⁻¹.
  ------------------------------------------------------------------

  inverseʳ-unique :
    (x y : Carrier) → (x ∙ y) ≈ ε → y ≈ (x ⁻¹)
  inverseʳ-unique x y x∙y≈ε =
    let step1 : y ≈ (ε ∙ y)
        step1 = ≈-sym (ε-left y)
        step2 : (ε ∙ y) ≈ (((x ⁻¹) ∙ x) ∙ y)
        step2 = ∙-cong (≈-sym (inv-left x)) (≈-refl y)
        step3 : (((x ⁻¹) ∙ x) ∙ y) ≈ ((x ⁻¹) ∙ (x ∙ y))
        step3 = ∙-assoc (x ⁻¹) x y
        step4 : ((x ⁻¹) ∙ (x ∙ y)) ≈ ((x ⁻¹) ∙ ε)
        step4 = ∙-cong (≈-refl (x ⁻¹)) x∙y≈ε
        step5 : ((x ⁻¹) ∙ ε) ≈ (x ⁻¹)
        step5 = ε-right (x ⁻¹)
    in ≈-trans step1
       (≈-trans step2
       (≈-trans step3
       (≈-trans step4 step5)))
