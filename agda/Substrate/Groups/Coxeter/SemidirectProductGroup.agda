------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SemidirectProductGroup
--
-- Generic combinator: takes two substrate-native SetoidGroups and an
-- action of the second on the first, produces the semidirect product
-- SetoidGroup-bundle N ⋊_φ H.
--
-- Phase-2 rewrite: parametric over Substrate.Algebra.SetoidGroup
-- (instead of stdlib Algebra.Bundles.Group). All stdlib imports
-- removed.
--
-- Carrier:    N.Carrier × H.Carrier
-- _≈_:        Pointwise N._≈_ H._≈_
-- _∙_:        (n₁, h₁) · (n₂, h₂) = (n₁ ∙ₙ act h₁ n₂, h₁ ∙ₕ h₂)
-- ε:          (ε_N, ε_H)
-- _⁻¹:        (n, h)⁻¹ = (act h⁻¹ n⁻¹, h⁻¹)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂; Σ)
open import Substrate.Algebra.SetoidGroup using (SetoidGroup)

module Substrate.Groups.Coxeter.SemidirectProductGroup
  (G-N : SetoidGroup)
  (G-H : SetoidGroup)
  where

private
  module N = SetoidGroup G-N
  module H = SetoidGroup G-H

------------------------------------------------------------------------
-- The action interface.
------------------------------------------------------------------------

module WithAction
  (act : H.Carrier → N.Carrier → N.Carrier)
  (act-cong :
    ∀ {h₁ h₂ n₁ n₂} →
    (h₁ H.≈ h₂) → (n₁ N.≈ n₂) → act h₁ n₁ N.≈ act h₂ n₂)
  (act-ε   : ∀ n → act H.ε n N.≈ n)
  (act-∙   : ∀ h₁ h₂ n → act (h₁ H.∙ h₂) n N.≈ act h₁ (act h₂ n))
  (act-hom : ∀ h n₁ n₂ →
    (act h (n₁ N.∙ n₂)) N.≈ ((act h n₁) N.∙ (act h n₂)))
  (act-ε-N : ∀ h → act h N.ε N.≈ N.ε)
  where

  ------------------------------------------------------------------
  -- 1. Carrier, _≈_, _∙_, ε, _⁻¹.
  ------------------------------------------------------------------

  Carrier : Set
  Carrier = N.Carrier × H.Carrier

  _≈_ : Carrier → Carrier → Set
  (n₁ , h₁) ≈ (n₂ , h₂) = (n₁ N.≈ n₂) × (h₁ H.≈ h₂)

  infixl 7 _∙_
  _∙_ : Carrier → Carrier → Carrier
  (n₁ , h₁) ∙ (n₂ , h₂) = (n₁ N.∙ act h₁ n₂) , (h₁ H.∙ h₂)

  ε : Carrier
  ε = N.ε , H.ε

  _⁻¹ : Carrier → Carrier
  (n , h) ⁻¹ = act (h H.⁻¹) (n N.⁻¹) , h H.⁻¹

  ------------------------------------------------------------------
  -- 2. ≈-equivalence.
  ------------------------------------------------------------------

  ≈-refl : (x : Carrier) → x ≈ x
  ≈-refl (n , h) = N.≈-refl n , H.≈-refl h

  ≈-sym : {x y : Carrier} → x ≈ y → y ≈ x
  ≈-sym (n-eq , h-eq) = N.≈-sym n-eq , H.≈-sym h-eq

  ≈-trans : {x y z : Carrier} → x ≈ y → y ≈ z → x ≈ z
  ≈-trans (n-eq₁ , h-eq₁) (n-eq₂ , h-eq₂) =
    N.≈-trans n-eq₁ n-eq₂ , H.≈-trans h-eq₁ h-eq₂

  ------------------------------------------------------------------
  -- 3. ∙-cong.
  ------------------------------------------------------------------

  ∙-cong :
    {a₁ a₂ b₁ b₂ : Carrier} → a₁ ≈ a₂ → b₁ ≈ b₂ → (a₁ ∙ b₁) ≈ (a₂ ∙ b₂)
  ∙-cong (n-eq₁ , h-eq₁) (n-eq₂ , h-eq₂) =
    N.∙-cong n-eq₁ (act-cong h-eq₁ n-eq₂) , H.∙-cong h-eq₁ h-eq₂

  ------------------------------------------------------------------
  -- 4. ∙-assoc.
  ------------------------------------------------------------------

  ∙-assoc : (a b c : Carrier) → ((a ∙ b) ∙ c) ≈ (a ∙ (b ∙ c))
  ∙-assoc (n₁ , h₁) (n₂ , h₂) (n₃ , h₃) =
    N.≈-trans
      (N.∙-assoc n₁ (act h₁ n₂) (act (h₁ H.∙ h₂) n₃))
      (N.≈-trans
        (N.∙-cong (N.≈-refl n₁)
                  (N.∙-cong (N.≈-refl (act h₁ n₂)) (act-∙ h₁ h₂ n₃)))
        (N.∙-cong (N.≈-refl n₁)
                  (N.≈-sym (act-hom h₁ n₂ (act h₂ n₃)))))
    ,
    H.∙-assoc h₁ h₂ h₃

  ------------------------------------------------------------------
  -- 5. ε identities.
  ------------------------------------------------------------------

  ε-left : (x : Carrier) → (ε ∙ x) ≈ x
  ε-left (n , h) =
    N.≈-trans (N.∙-cong (N.≈-refl N.ε) (act-ε n)) (N.ε-left n)
    ,
    H.ε-left h

  ε-right : (x : Carrier) → (x ∙ ε) ≈ x
  ε-right (n , h) =
    N.≈-trans (N.∙-cong (N.≈-refl n) (act-ε-N h)) (N.ε-right n)
    ,
    H.ε-right h

  ------------------------------------------------------------------
  -- 6. inverse laws.
  ------------------------------------------------------------------

  inv-left : (x : Carrier) → ((x ⁻¹) ∙ x) ≈ ε
  inv-left (n , h) =
    N.≈-trans (N.≈-sym (act-hom (h H.⁻¹) (n N.⁻¹) n))
    (N.≈-trans (act-cong (H.≈-refl (h H.⁻¹)) (N.inv-left n))
               (act-ε-N (h H.⁻¹)))
    ,
    H.inv-left h

  inv-right : (x : Carrier) → (x ∙ (x ⁻¹)) ≈ ε
  inv-right (n , h) =
    N.≈-trans (N.∙-cong (N.≈-refl n) (N.≈-sym (act-∙ h (h H.⁻¹) (n N.⁻¹))))
    (N.≈-trans (N.∙-cong (N.≈-refl n) (act-cong (H.inv-right h) (N.≈-refl (n N.⁻¹))))
    (N.≈-trans (N.∙-cong (N.≈-refl n) (act-ε (n N.⁻¹)))
               (N.inv-right n)))
    ,
    H.inv-right h

  ⁻¹-cong : {x y : Carrier} → x ≈ y → (x ⁻¹) ≈ (y ⁻¹)
  ⁻¹-cong (n-eq , h-eq) =
    act-cong (H.⁻¹-cong h-eq) (N.⁻¹-cong n-eq) , H.⁻¹-cong h-eq

  ------------------------------------------------------------------
  -- 7. Assemble the SetoidGroup.
  ------------------------------------------------------------------

  SetoidGroup-bundle : SetoidGroup
  SetoidGroup-bundle = record
    { Carrier   = Carrier
    ; _≈_       = _≈_
    ; _∙_       = _∙_
    ; ε         = ε
    ; _⁻¹       = _⁻¹
    ; ≈-refl    = ≈-refl
    ; ≈-sym     = ≈-sym
    ; ≈-trans   = ≈-trans
    ; ∙-assoc   = ∙-assoc
    ; ε-left    = ε-left
    ; ε-right   = ε-right
    ; inv-left  = inv-left
    ; inv-right = inv-right
    ; ∙-cong    = ∙-cong
    ; ⁻¹-cong   = ⁻¹-cong
    }

  -- Backward-compat alias.
  Group-bundle : SetoidGroup
  Group-bundle = SetoidGroup-bundle

  ------------------------------------------------------------------
  -- 8. Structural normality of N in N ⋊_φ H.
  ------------------------------------------------------------------

  N-normal-in-SP :
    (g : Carrier) (n : N.Carrier) →
    Σ N.Carrier (λ n' → ((g ∙ (n , H.ε)) ∙ (g ⁻¹)) ≈ (n' , H.ε))
  N-normal-in-SP (n₀ , h₀) n =
    (n₀ N.∙ act h₀ n) N.∙ (n₀ N.⁻¹) , (n-eq , h-eq)
    where
      h-eq : ((h₀ H.∙ H.ε) H.∙ (h₀ H.⁻¹)) H.≈ H.ε
      h-eq = H.≈-trans (H.∙-cong (H.ε-right h₀) (H.≈-refl (h₀ H.⁻¹)))
                       (H.inv-right h₀)

      collapse :
        act (h₀ H.∙ H.ε) (act (h₀ H.⁻¹) (n₀ N.⁻¹)) N.≈ (n₀ N.⁻¹)
      collapse =
        N.≈-trans (N.≈-sym (act-∙ (h₀ H.∙ H.ε) (h₀ H.⁻¹) (n₀ N.⁻¹)))
        (N.≈-trans (act-cong h-eq (N.≈-refl (n₀ N.⁻¹)))
                   (act-ε (n₀ N.⁻¹)))

      n-eq :
        ((n₀ N.∙ act h₀ n) N.∙
          act (h₀ H.∙ H.ε) (act (h₀ H.⁻¹) (n₀ N.⁻¹)))
        N.≈ ((n₀ N.∙ act h₀ n) N.∙ (n₀ N.⁻¹))
      n-eq = N.∙-cong (N.≈-refl (n₀ N.∙ act h₀ n)) collapse
