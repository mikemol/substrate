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

open import Substrate.Foundation.Level using (0ℓ; suc)
open import Substrate.Foundation.Product using (∃; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; sym-trans)

open import Substrate.Axes using (Axis)
open import Substrate.Groups.V4 as V4 using (V₄; e; α; β; γ)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε; _≈_;
         ·-cong; ≈-refl; ≈-sym; ⁻¹-cong; inv-l)
  renaming (apply to applyₛ; invₐ to invₐₛ)
open import Substrate.Groups.V4-Embedding
  using (embed; embed-hom; V₄-image; act-axis-id)
open import Substrate.Groups.SemidirectProduct using (Stab)
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
  v , (λ x → sym-trans (σ≈τ x) (σ≈ev x))

V₄-image-ε : V₄-image ε
V₄-image-ε = e , (λ x → sym (act-axis-id x))

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
-- Stab(X) subgroup, parametric over the anchor axis X.
--
-- Stab(X) is a subgroup of S₄ for every X but is NOT normal (only
-- V₄-image is normal in S₄). The four X ∈ {D, C, S, W} instances are
-- specializations `Stab-Subgroup D` etc. — no separate definitions
-- per anchor.
------------------------------------------------------------------------

Stab-resp-≈ :
  ∀ {X σ τ} → σ ≈ τ → Stab X σ → Stab X τ
Stab-resp-≈ {X} σ≈τ σ-stab = sym-trans (σ≈τ X) σ-stab

Stab-ε : ∀ X → Stab X ε
Stab-ε X = refl

Stab-∙ :
  ∀ {X σ τ} → Stab X σ → Stab X τ → Stab X (σ · τ)
Stab-∙ {X} {σ} σ-stab τ-stab =
  trans (cong (applyₛ σ) τ-stab) σ-stab

Stab-⁻¹ :
  ∀ {X σ} → Stab X σ → Stab X (σ ⁻¹)
Stab-⁻¹ {X} {σ} σ-stab =
  sym-trans (cong (invₐₛ σ) σ-stab) (inv-l σ X)

Stab-Subgroup : Axis → S₄-Subgroup
Stab-Subgroup X = record
  { member        = Stab X
  ; member-resp-≈ = λ {σ} {τ} → Stab-resp-≈ {X} {σ} {τ}
  ; member-ε      = Stab-ε X
  ; member-∙      = λ {σ} {τ} → Stab-∙ {X} {σ} {τ}
  ; member-⁻¹     = λ {σ} → Stab-⁻¹ {X} {σ}
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. With both V_4-image-NormalSubgroup and Stab-Subgroup X in
--    place (for every X : Axis), the V_4 ⋊ Stab(X) ≅ S_4 picture has
--    full structural recognition. The quotient theorem
--    S_4 / V_4-image ≅ Stab(X) ≅ S_3 follows by:
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
--    - Substrate.Groups.SemidirectProduct (slice 3) — parametric Stab.
--    - Substrate.Groups.V4-Normality (slice 9) — V₄-normal,
--      the underlying conjugation-closure theorem.
------------------------------------------------------------------------
