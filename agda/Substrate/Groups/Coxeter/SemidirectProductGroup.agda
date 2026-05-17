------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.SemidirectProductGroup
--
-- Generic combinator: takes two stdlib Group bundles and an action
-- of the second on the first, produces the semidirect product Group
-- bundle N ⋊_φ H.
--
-- The action is a homomorphism φ : H → Aut(N), encoded here as a
-- function `act : H.Carrier → N.Carrier → N.Carrier` plus the action
-- axioms (compatibility with each group's structure).
--
-- Carrier:    N.Carrier × H.Carrier
-- _≈_:        Pointwise N._≈_ H._≈_
-- _∙_:        (n₁, h₁) · (n₂, h₂) = (n₁ ∙ₙ act h₁ n₂, h₁ ∙ₕ h₂)
-- ε:          (ε_N, ε_H)
-- _⁻¹:        (n, h)⁻¹ = (act h⁻¹ n⁻¹, h⁻¹)
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: this
-- shadow is the engine for S₃ = Z/3 ⋊ Z/2 and S₄ = V₄ ⋊ S₃, AND for
-- any future semidirect product in substrate (AGL towers, etc.).
--
-- NOTE on the Coxeter Core impossibility: SP at the Coxeter Core
-- level (Word + strict ++-assoc + Word-level normalize-distrib) fails
-- because act-hom is provable only up to normalize, not strictly.
-- The Group level (this module) sidesteps the issue: ≈-respecting
-- congruence is exactly what stdlib's Group expects.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Algebra.Bundles using (Group)
open import Algebra.Structures using (IsMagma; IsSemigroup; IsMonoid; IsGroup)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Level using (Level; _⊔_)
open import Relation.Binary using (IsEquivalence; Rel)

module Substrate.Groups.Coxeter.SemidirectProductGroup
  {cN ℓN cH ℓH : Level}
  (G-N : Group cN ℓN)
  (G-H : Group cH ℓH)
  where

private
  module N = Group G-N
  module H = Group G-H

------------------------------------------------------------------------
-- The action interface — passed as a sub-module's parameters.
------------------------------------------------------------------------

module WithAction
  (act : H.Carrier → N.Carrier → N.Carrier)
  -- Congruence: act respects ≈ in both arguments.
  (act-cong : ∀ {h₁ h₂ n₁ n₂} → h₁ H.≈ h₂ → n₁ N.≈ n₂ →
              act h₁ n₁ N.≈ act h₂ n₂)
  -- act of H's identity is identity on N.
  (act-ε : ∀ n → act H.ε n N.≈ n)
  -- act respects H's group operation: φ(h₁ ∙ h₂) = φ(h₁) ∘ φ(h₂).
  (act-∙ : ∀ h₁ h₂ n → act (h₁ H.∙ h₂) n N.≈ act h₁ (act h₂ n))
  -- φ(h) is a homomorphism of N: distributes over N's operation.
  (act-hom : ∀ h n₁ n₂ → act h (n₁ N.∙ n₂) N.≈ (act h n₁) N.∙ (act h n₂))
  -- φ(h) preserves N's identity.
  (act-ε-N : ∀ h → act h N.ε N.≈ N.ε)
  where

  ------------------------------------------------------------------
  -- 1. Carrier, _≈_, _∙_, ε, _⁻¹ for the semidirect product.
  ------------------------------------------------------------------

  Carrier : Set (cN ⊔ cH)
  Carrier = N.Carrier × H.Carrier

  _≈_ : Rel Carrier (ℓN ⊔ ℓH)
  (n₁ , h₁) ≈ (n₂ , h₂) = (n₁ N.≈ n₂) × (h₁ H.≈ h₂)

  infixl 7 _∙_
  _∙_ : Carrier → Carrier → Carrier
  (n₁ , h₁) ∙ (n₂ , h₂) = (n₁ N.∙ act h₁ n₂ , h₁ H.∙ h₂)

  ε : Carrier
  ε = (N.ε , H.ε)

  _⁻¹ : Carrier → Carrier
  (n , h) ⁻¹ = (act (h H.⁻¹) (n N.⁻¹) , h H.⁻¹)

  ------------------------------------------------------------------
  -- 2. ≈ is an equivalence (componentwise).
  ------------------------------------------------------------------

  ≈-refl : ∀ {x} → x ≈ x
  ≈-refl = N.refl , H.refl

  ≈-sym : ∀ {x y} → x ≈ y → y ≈ x
  ≈-sym (n-eq , h-eq) = N.sym n-eq , H.sym h-eq

  ≈-trans : ∀ {x y z} → x ≈ y → y ≈ z → x ≈ z
  ≈-trans (n-eq₁ , h-eq₁) (n-eq₂ , h-eq₂) =
    N.trans n-eq₁ n-eq₂ , H.trans h-eq₁ h-eq₂

  ≈-isEquivalence : IsEquivalence _≈_
  ≈-isEquivalence = record { refl = ≈-refl ; sym = ≈-sym ; trans = ≈-trans }

  ------------------------------------------------------------------
  -- 3. _∙_ is ≈-congruent.
  ------------------------------------------------------------------

  ∙-cong : ∀ {a₁ a₂ b₁ b₂} → a₁ ≈ a₂ → b₁ ≈ b₂ → (a₁ ∙ b₁) ≈ (a₂ ∙ b₂)
  ∙-cong (n-eq₁ , h-eq₁) (n-eq₂ , h-eq₂) =
    N.∙-cong n-eq₁ (act-cong h-eq₁ n-eq₂) , H.∙-cong h-eq₁ h-eq₂

  ------------------------------------------------------------------
  -- 4. ∙ is associative (componentwise; uses act-∙ + act-hom).
  ------------------------------------------------------------------

  ∙-assoc : ∀ a b c → ((a ∙ b) ∙ c) ≈ (a ∙ (b ∙ c))
  ∙-assoc (n₁ , h₁) (n₂ , h₂) (n₃ , h₃) =
    -- N-component:
    --   (n₁ ∙ₙ act h₁ n₂) ∙ₙ act (h₁ ∙ₕ h₂) n₃
    --   ≈ n₁ ∙ₙ (act h₁ n₂ ∙ₙ act (h₁ ∙ₕ h₂) n₃)  [N.assoc]
    --   ≈ n₁ ∙ₙ (act h₁ n₂ ∙ₙ act h₁ (act h₂ n₃)) [act-∙ via ∙-cong-right]
    --   ≈ n₁ ∙ₙ act h₁ (n₂ ∙ₙ act h₂ n₃)          [sym act-hom via ∙-cong-right]
    N.trans (N.assoc n₁ (act h₁ n₂) (act (h₁ H.∙ h₂) n₃))
    (N.trans (N.∙-cong N.refl (N.∙-cong N.refl (act-∙ h₁ h₂ n₃)))
             (N.∙-cong N.refl (N.sym (act-hom h₁ n₂ (act h₂ n₃)))))
    ,
    H.assoc h₁ h₂ h₃

  ------------------------------------------------------------------
  -- 5. ε is left/right identity.
  ------------------------------------------------------------------

  open import Algebra.Definitions using (LeftIdentity; RightIdentity; Identity;
                                          LeftInverse; RightInverse; Inverse;
                                          Congruent₁)

  ε-left : LeftIdentity _≈_ ε _∙_
  ε-left (n , h) =
    -- N-component: ε_N ∙ₙ act ε_H n ≈ ε_N ∙ₙ n ≈ n  (via act-ε, identityˡ)
    -- H-component: ε_H ∙ₕ h ≈ h                      (H.identityˡ)
    N.trans (N.∙-cong N.refl (act-ε n)) (proj₁ N.identity n)
    ,
    proj₁ H.identity h

  ε-right : RightIdentity _≈_ ε _∙_
  ε-right (n , h) =
    -- N-component: n ∙ₙ act h ε_N ≈ n ∙ₙ ε_N ≈ n   (via act-ε-N, identityʳ)
    -- H-component: h ∙ₕ ε_H ≈ h                     (H.identityʳ)
    N.trans (N.∙-cong N.refl (act-ε-N h)) (proj₂ N.identity n)
    ,
    proj₂ H.identity h

  ε-identity : Identity _≈_ ε _∙_
  ε-identity = ε-left , ε-right

  ------------------------------------------------------------------
  -- 6. ⁻¹ is left/right inverse.
  --
  -- (n, h)⁻¹ = (act h⁻¹ n⁻¹, h⁻¹). Verifications:
  --
  -- Left:  (act h⁻¹ n⁻¹, h⁻¹) ∙ (n, h)
  --   N-side: act h⁻¹ n⁻¹ ∙ₙ act h⁻¹ n
  --          ≈ act h⁻¹ (n⁻¹ ∙ₙ n)      [sym act-hom]
  --          ≈ act h⁻¹ ε_N              [act-cong + N.inv-left]
  --          ≈ ε_N                       [act-ε-N]
  --   H-side: h⁻¹ ∙ₕ h ≈ ε_H            [H.inv-left]
  --
  -- Right: (n, h) ∙ (act h⁻¹ n⁻¹, h⁻¹)
  --   N-side: n ∙ₙ act h (act h⁻¹ n⁻¹)
  --          ≈ n ∙ₙ act (h ∙ₕ h⁻¹) n⁻¹  [sym act-∙]
  --          ≈ n ∙ₙ act ε_H n⁻¹          [act-cong + H.inv-right]
  --          ≈ n ∙ₙ n⁻¹                  [act-ε]
  --          ≈ ε_N                       [N.inv-right]
  --   H-side: h ∙ₕ h⁻¹ ≈ ε_H            [H.inv-right]
  ------------------------------------------------------------------

  inv-left : LeftInverse _≈_ ε _⁻¹ _∙_
  inv-left (n , h) =
    N.trans (N.sym (act-hom (h H.⁻¹) (n N.⁻¹) n))
    (N.trans (act-cong H.refl (proj₁ N.inverse n))
             (act-ε-N (h H.⁻¹)))
    ,
    proj₁ H.inverse h

  inv-right : RightInverse _≈_ ε _⁻¹ _∙_
  inv-right (n , h) =
    N.trans (N.∙-cong N.refl (N.sym (act-∙ h (h H.⁻¹) (n N.⁻¹))))
    (N.trans (N.∙-cong N.refl (act-cong (proj₂ H.inverse h) N.refl))
    (N.trans (N.∙-cong N.refl (act-ε (n N.⁻¹)))
             (proj₂ N.inverse n)))
    ,
    proj₂ H.inverse h

  inv-inverse : Inverse _≈_ ε _⁻¹ _∙_
  inv-inverse = inv-left , inv-right

  ⁻¹-cong : Congruent₁ _≈_ _⁻¹
  ⁻¹-cong (n-eq , h-eq) =
    act-cong (H.⁻¹-cong h-eq) (N.⁻¹-cong n-eq)
    ,
    H.⁻¹-cong h-eq

  ------------------------------------------------------------------
  -- 7. Assemble the Group bundle.
  ------------------------------------------------------------------

  isMagma : IsMagma _≈_ _∙_
  isMagma = record { isEquivalence = ≈-isEquivalence ; ∙-cong = ∙-cong }

  isSemigroup : IsSemigroup _≈_ _∙_
  isSemigroup = record { isMagma = isMagma ; assoc = ∙-assoc }

  isMonoid : IsMonoid _≈_ _∙_ ε
  isMonoid = record { isSemigroup = isSemigroup ; identity = ε-identity }

  isGroup : IsGroup _≈_ _∙_ ε _⁻¹
  isGroup = record
    { isMonoid = isMonoid
    ; inverse  = inv-inverse
    ; ⁻¹-cong  = ⁻¹-cong
    }

  Group-bundle : Group (cN ⊔ cH) (ℓN ⊔ ℓH)
  Group-bundle = record
    { Carrier = Carrier
    ; _≈_     = _≈_
    ; _∙_     = _∙_
    ; ε       = ε
    ; _⁻¹     = _⁻¹
    ; isGroup = isGroup
    }

  ------------------------------------------------------------------
  -- 8. Structural normality of N in N ⋊_φ H.
  --
  -- For any g : Carrier and n : N.Carrier, conjugation of the
  -- N-injected element (n, ε_H) by g is again an N-injected
  -- element (n', ε_H). This is the structural-compositional content
  -- of "N ⊳ N ⋊_φ H" — proven by direct computation from the SP
  -- axioms, no enumeration required.
  --
  -- Witness: n' = (n₀ N.∙ act h₀ n) N.∙ n₀ N.⁻¹ where g = (n₀, h₀).
  --
  -- This is the load-bearing structural lemma that lets downstream
  -- consumers prove V₄-normal in S₄ compositionally, replacing the
  -- predicate-based proof in Substrate.Groups.V4-Normality.
  ------------------------------------------------------------------

  open import Data.Product using (Σ)

  N-normal-in-SP : ∀ (g : Carrier) (n : N.Carrier) →
    Σ N.Carrier (λ n' → ((g ∙ (n , H.ε)) ∙ (g ⁻¹)) ≈ (n' , H.ε))
  N-normal-in-SP (n₀ , h₀) n =
    (n₀ N.∙ act h₀ n) N.∙ n₀ N.⁻¹ , (n-eq , h-eq)
    where
      h-eq : ((h₀ H.∙ H.ε) H.∙ (h₀ H.⁻¹)) H.≈ H.ε
      h-eq = H.trans (H.∙-cong (proj₂ H.identity h₀) H.refl)
                     (proj₂ H.inverse h₀)

      -- act (h₀ H.∙ H.ε) (act h₀⁻¹ n₀⁻¹) ≈ n₀⁻¹ via:
      --   sym act-∙ → act-cong (using h-eq) → act-ε.
      collapse :
        act (h₀ H.∙ H.ε) (act (h₀ H.⁻¹) (n₀ N.⁻¹)) N.≈ (n₀ N.⁻¹)
      collapse =
        N.trans (N.sym (act-∙ (h₀ H.∙ H.ε) (h₀ H.⁻¹) (n₀ N.⁻¹)))
        (N.trans (act-cong h-eq N.refl)
                 (act-ε (n₀ N.⁻¹)))

      n-eq : ((n₀ N.∙ act h₀ n) N.∙ act (h₀ H.∙ H.ε) (act (h₀ H.⁻¹) (n₀ N.⁻¹)))
           N.≈ ((n₀ N.∙ act h₀ n) N.∙ n₀ N.⁻¹)
      n-eq = N.∙-cong N.refl collapse
