------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.IsoTransport
--
-- Iso-transport infrastructure (K-shadows):
--   forward-ε     — compositional-to-perm sends S4C.ε ↦ ε.
--   embed-cong    — V₄ ≡ → embed ≈.
--   embed-S₃-cong — S₃.≈ → embed-S₃ ≈.
--   compositional-to-perm-cong — S4C.≈ → ≈.
--   forward-inv   — compositional-to-perm respects ⁻¹.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.IsoTransport where

open import Substrate.Axes using (Axis; act-axis; axis-of-v; v-of-axis)
import Substrate.Groups.V4 as V4
open V4 using (V₄; e)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4 as φ
open import Substrate.Groups.V4-Embedding using (embed; act-axis-id)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε; _≈_;
         ≈-refl; ≈-sym; ≈-trans;
         ·-cong)
open import Substrate.Foundation.Product using (_,_; proj₁)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.Groups.S4-Iso.Embedding
  using (embed-S₃; compositional-to-perm)
open import Substrate.Groups.S4-Iso.Foundation using (embed-S₃-ε)
open import Substrate.Groups.S4-Iso.ForwardHom using (forward-hom)

------------------------------------------------------------------------
-- forward-ε: compositional-to-perm preserves identity.
------------------------------------------------------------------------

forward-ε : compositional-to-perm S4C.ε ≈ ε
forward-ε x = trans (cong (act-axis e) (embed-S₃-ε x)) (act-axis-id x)

------------------------------------------------------------------------
-- embed-cong and embed-S₃-cong (private/public both useful).
------------------------------------------------------------------------

embed-cong : ∀ {v₁ v₂ : V₄} → v₁ ≡ v₂ → embed v₁ ≈ embed v₂
embed-cong refl x = refl

embed-S₃-cong : ∀ {s₁ s₂ : S₃.Carrier} → s₁ S₃.≈ s₂ →
                embed-S₃ s₁ ≈ embed-S₃ s₂
embed-S₃-cong {s₁} {s₂} s-eq x =
  cong axis-of-v
       (φ.act-cong {s₁ = s₁} {s₂ = s₂}
                    {v₁ = v-of-axis x} {v₂ = v-of-axis x}
                    s-eq refl)

------------------------------------------------------------------------
-- compositional-to-perm-cong: respects S4C._≈_.
------------------------------------------------------------------------

compositional-to-perm-cong :
  ∀ {s₁ s₂ : S4C.Carrier} → s₁ S4C.≈ s₂ →
  compositional-to-perm s₁ ≈ compositional-to-perm s₂
compositional-to-perm-cong {v₁ , sa} {v₂ , sb} (v-eq , s-eq) =
  ·-cong {σ₁ = embed v₁} {σ₂ = embed v₂}
          {τ₁ = embed-S₃ sa} {τ₂ = embed-S₃ sb}
          (embed-cong v-eq)
          (embed-S₃-cong {s₁ = sa} {s₂ = sb} s-eq)

------------------------------------------------------------------------
-- forward-inv: compositional-to-perm respects ⁻¹.
------------------------------------------------------------------------

open import Substrate.Algebra.SetoidGroup.Properties using (module Props)
open Props Permutation _≈_ S4.Symmetric-Group using (inverseˡ-unique)

forward-inv : ∀ (s : S4C.Carrier) →
              compositional-to-perm (s S4C.⁻¹) ≈ (compositional-to-perm s) ⁻¹
forward-inv s =
  inverseˡ-unique (compositional-to-perm (s S4C.⁻¹)) (compositional-to-perm s)
                  inverse-eq
  where
    M1 : Permutation
    M1 = compositional-to-perm (s S4C.⁻¹) · compositional-to-perm s
    M2 : Permutation
    M2 = compositional-to-perm ((s S4C.⁻¹) S4C.∙ s)
    M3 : Permutation
    M3 = compositional-to-perm S4C.ε

    eqA : M1 ≈ M2
    eqA = ≈-sym {σ = M2} {τ = M1} (forward-hom (s S4C.⁻¹) s)

    eqB : M2 ≈ M3
    eqB = compositional-to-perm-cong {s₁ = (s S4C.⁻¹) S4C.∙ s} {s₂ = S4C.ε}
                                       (S4C.inv-left s)

    eqC : M3 ≈ ε
    eqC = forward-ε

    inverse-eq : M1 ≈ ε
    inverse-eq = ≈-trans {σ = M1} {τ = M2} {ρ = ε} eqA
                  (≈-trans {σ = M2} {τ = M3} {ρ = ε} eqB eqC)
