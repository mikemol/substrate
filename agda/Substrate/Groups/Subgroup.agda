------------------------------------------------------------------------
-- Substrate.Groups.Subgroup
--
-- Slice 12: Subgroup and NormalSubgroup record abstractions plus
-- their instances for V_4-image and Stab(D) inside S_4.
--
-- This module promotes the V_4 ⊳ S_4 claim from "exists a quantified
-- normality theorem" (slice 9) to "V_4-image IS a NormalSubgroup of
-- S_4-Group" — the catalog-load-bearing structural statement.
-- Unlocks the S_4 / V_4 ≅ S_3 quotient theorem (slice 13).
--
-- This slice specialises the Subgroup record to S_4 specifically
-- (rather than generalising over arbitrary Group bundles). The
-- generalisation is mechanical and deferred — Permutation has
-- enough Agda quirks (record-η, apply/invₐ inference) that the
-- specialised form lands cleanly while the general form needs
-- more scaffolding.
--
-- See: catalog/cocycles.md § CY-5 — V_4 ⋊ S_3 ≅ S_4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Subgroup where

open import Level using (0ℓ; suc)
open import Data.Product using (∃; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W; act-axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε; _≈_;
         ·-cong; ≈-refl; ≈-sym; ⁻¹-cong; inv-l)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; embed-hom; V₄-image)
open import Substrate.Groups.SemidirectProduct using (Stab-D)
open import Substrate.Groups.V4-Normality using (V₄-normal)

------------------------------------------------------------------------
-- Subgroup of S_4 (specialised).
------------------------------------------------------------------------

record S₄-Subgroup : Set₁ where
  field
    member        : Permutation → Set
    member-resp-≈ : {σ τ : Permutation} → σ ≈ τ → member σ → member τ
    member-ε      : member ε
    member-∙      : {σ τ : Permutation} → member σ → member τ → member (σ · τ)
    member-⁻¹     : {σ : Permutation} → member σ → member (σ ⁻¹)

------------------------------------------------------------------------
-- NormalSubgroup of S_4 (specialised).
------------------------------------------------------------------------

record S₄-NormalSubgroup : Set₁ where
  field
    subgroup : S₄-Subgroup
  open S₄-Subgroup subgroup public
  field
    member-normal :
      {g n : Permutation} → member n → member ((g · n) · (g ⁻¹))

------------------------------------------------------------------------
-- V_4-image instances.
------------------------------------------------------------------------

V₄-image-resp-≈ :
  {σ τ : Permutation} → σ ≈ τ → V₄-image σ → V₄-image τ
V₄-image-resp-≈ {σ} {τ} σ≈τ (v , σ≈ev) =
  v , (λ x → trans (sym (σ≈τ x)) (σ≈ev x))

V₄-image-ε : V₄-image ε
V₄-image-ε = e , (λ _ → refl)

embed-self-inv : (v : V₄) → (embed v) ⁻¹ ≈ embed v
embed-self-inv v _ = refl

V₄-image-∙ :
  {σ τ : Permutation} → V₄-image σ → V₄-image τ → V₄-image (σ · τ)
V₄-image-∙ {σ} {τ} (v₁ , σ≈ev₁) (v₂ , τ≈ev₂) =
  (v₁ V4.· v₂) , (λ x →
    trans (·-cong {σ} {embed v₁} {τ} {embed v₂} σ≈ev₁ τ≈ev₂ x)
          (sym (embed-hom v₁ v₂ x)))

V₄-image-⁻¹ :
  {σ : Permutation} → V₄-image σ → V₄-image (σ ⁻¹)
V₄-image-⁻¹ {σ} (v , σ≈ev) =
  v , (λ x → trans (⁻¹-cong {σ} {embed v} σ≈ev x) (embed-self-inv v x))

V₄-image-Subgroup : S₄-Subgroup
V₄-image-Subgroup = record
  { member        = V₄-image
  ; member-resp-≈ = λ {σ} {τ} → V₄-image-resp-≈ {σ} {τ}
  ; member-ε      = V₄-image-ε
  ; member-∙      = λ {σ} {τ} → V₄-image-∙ {σ} {τ}
  ; member-⁻¹     = λ {σ} → V₄-image-⁻¹ {σ}
  }

V₄-image-Normal-prop :
  {g n : Permutation} → V₄-image n → V₄-image ((g · n) · (g ⁻¹))
V₄-image-Normal-prop {g} {n} (v , n≈ev) =
  V₄-image-resp-≈ {(g · embed v) · (g ⁻¹)} {(g · n) · (g ⁻¹)}
    conj-≈ (V₄-normal g v)
  where
    inner : (g · embed v) ≈ (g · n)
    inner = ·-cong {g} {g} {embed v} {n} (≈-refl g)
                   (≈-sym {n} {embed v} n≈ev)

    conj-≈ :
      ((g · embed v) · (g ⁻¹)) ≈ ((g · n) · (g ⁻¹))
    conj-≈ = ·-cong {g · embed v} {g · n} {g ⁻¹} {g ⁻¹}
                    inner (≈-refl (g ⁻¹))

V₄-image-NormalSubgroup : S₄-NormalSubgroup
V₄-image-NormalSubgroup = record
  { subgroup      = V₄-image-Subgroup
  ; member-normal = λ {g} {n} → V₄-image-Normal-prop {g} {n}
  }

------------------------------------------------------------------------
-- Stab(D) instances. Stab(D) is a subgroup but NOT normal.
------------------------------------------------------------------------

Stab-D-resp-≈ :
  ∀ {σ τ} → σ ≈ τ → Stab-D σ → Stab-D τ
Stab-D-resp-≈ σ≈τ σ-stab = trans (sym (σ≈τ D)) σ-stab

Stab-D-ε : Stab-D ε
Stab-D-ε = refl

Stab-D-∙ :
  ∀ {σ τ} → Stab-D σ → Stab-D τ → Stab-D (σ · τ)
Stab-D-∙ {σ} σ-stab τ-stab =
  trans (cong (applyₛ σ) τ-stab) σ-stab

Stab-D-⁻¹ :
  ∀ {σ} → Stab-D σ → Stab-D (σ ⁻¹)
Stab-D-⁻¹ {σ} σ-stab =
  trans (sym (cong (invₐₛ σ) σ-stab)) (inv-l σ D)

Stab-D-Subgroup : S₄-Subgroup
Stab-D-Subgroup = record
  { member        = Stab-D
  ; member-resp-≈ = λ {σ} {τ} → Stab-D-resp-≈ {σ} {τ}
  ; member-ε      = Stab-D-ε
  ; member-∙      = λ {σ} {τ} → Stab-D-∙ {σ} {τ}
  ; member-⁻¹     = λ {σ} → Stab-D-⁻¹ {σ}
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. With both V_4-image-NormalSubgroup and Stab-D-Subgroup in place,
--    the V_4 ⋊ Stab(D) ≅ S_4 picture has full structural recognition.
--    The quotient theorem S_4 / V_4-image ≅ Stab(D) ≅ S_3 follows
--    by:
--      * defining the quotient group via the normal-subgroup
--        equivalence (σ₁ ∼ σ₂ iff σ₁⁻¹ · σ₂ ∈ V_4-image),
--      * showing the map σ ↦ s-for σ descends through the quotient
--        (which follows from V_4 normality + factorisation),
--      * exhibiting bijectivity of the descended map.
--    Deferred to slice 13.
--
-- 2. This module specialises to S_4. Generalising to arbitrary
--    Group bundles requires care with Agda's record-projection
--    reduction for Permutation (apply/invₐ inference); the
--    specialised form sidesteps that.
--
-- 3. Cross-references:
--    - Substrate.Groups.V4-Embedding (slice 2) — V_4-image,
--      embed-hom.
--    - Substrate.Groups.SemidirectProduct (slice 3) — Stab-D.
--    - Substrate.Groups.V4-Normality (slice 9) — V₄-normal,
--      the underlying conjugation-closure theorem.
------------------------------------------------------------------------
