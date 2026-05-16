------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3-Hom
--
-- Slice 14e: group-homomorphism properties for the restrict side of
-- the Stab(anchor) ≅ S_3 iso. Shows restrict preserves identity,
-- composition, and inverse.
--
-- The three homomorphism lemmas (all stated pointwise):
--
--   restrict-hom-ε   : restrict anchor (ε , Stab-ε anchor) ≈ SFin.ε
--   restrict-hom-∙   : restrict anchor (σ₁·σ₂ , Stab-∙ p₁ p₂) ≈
--                       restrict anchor (σ₁,p₁) SFin.·
--                       restrict anchor (σ₂,p₂)
--   restrict-hom-⁻¹  : restrict anchor (σ⁻¹ , Stab-inv p) ≈
--                       (restrict anchor (σ,p)) SFin.⁻¹
--
-- For ⁻¹ the equation is refl by definition: both sides are
-- restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i, since
-- restrict-invₐ unfolds to restrict-apply (σ⁻¹) (Stab-inv ...).
--
-- For ε and ∙ the chain uses non-anchor-to-fin3-cong + the bridge
-- round-trips from slice 14a, in the same shape as slices 14b/14d.
--
-- Side parametric closure laws (added here):
--   Stab-ε : (anchor : Axis) → Stab anchor ε  (refl, ε.apply = id)
--   Stab-∙ : (anchor : Axis) {σ τ} → Stab σ → Stab τ → Stab (σ · τ)
--
-- The extend-side homomorphism (extend-hom-ε / ∙ / ⁻¹) is deferred
-- to slice 14f if needed; the symmetry suggests the same structure.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3-Hom where

open import Level using (0ℓ)
open import Data.Nat using (ℕ; zero; suc)
open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 as S4
  using (Permutation; _·_; _⁻¹; ε)
  renaming (apply to applyₛ; invₐ to invₐₛ)
import Substrate.Groups.SFin as SFin
open import Substrate.Groups.Stab-S3
  using (Stab; Stab-inv;
         fin3-to-non-anchor; fin3-to-non-anchor-≢;
         non-anchor-to-fin3; non-anchor-fin3-non-anchor;
         fin3-non-anchor-fin3; stab-preserves-≢)
open import Substrate.Groups.Stab-S3-Restrict
  using (non-anchor-to-fin3-cong; restrict)

------------------------------------------------------------------------
-- Parametric closure laws for Stab anchor (identity and composition).
------------------------------------------------------------------------

Stab-ε : (anchor : Axis) → Stab anchor ε
Stab-ε anchor = refl

Stab-∙ :
  (anchor : Axis) {σ τ : Permutation} →
  Stab anchor σ → Stab anchor τ →
  Stab anchor (σ · τ)
Stab-∙ anchor {σ} {τ} σ-stab τ-stab =
  trans (cong (applyₛ σ) τ-stab) σ-stab

------------------------------------------------------------------------
-- restrict-hom-ε: restrict preserves the identity.
--
-- LHS reduces to non-anchor-to-fin3 anchor (fin3-to-non-anchor anchor
-- i) (some stab-preserves-≢ proof) — since applyₛ ε x = x. The
-- chain: bridge proof-difference via non-anchor-to-fin3-cong (with
-- refl on the axis component), then close via fin3-non-anchor-fin3.
------------------------------------------------------------------------

restrict-hom-ε :
  (anchor : Axis) (i : Fin 3) →
  SFin.apply (restrict anchor (ε , Stab-ε anchor)) i ≡ SFin.apply SFin.ε i
restrict-hom-ε anchor i =
  trans (non-anchor-to-fin3-cong anchor refl _
          (fin3-to-non-anchor-≢ anchor i))
        (fin3-non-anchor-fin3 anchor i)

------------------------------------------------------------------------
-- restrict-hom-∙: restrict preserves composition.
--
-- LHS:
--   non-anchor-to-fin3 anchor (applyₛ σ₁ (applyₛ σ₂ X)) (proof_L)
-- RHS:
--   non-anchor-to-fin3 anchor (applyₛ σ₁ (fin3-to-non-anchor anchor
--                              (restrict-apply anchor σ₂ p₂ i)))
--                              (proof_R)
-- where X = fin3-to-non-anchor anchor i.
--
-- The two axis-expressions agree after rewriting via
-- non-anchor-fin3-non-anchor anchor (applyₛ σ₂ X) (the stab-preserves-≢
-- proof restrict-apply uses internally). cong (applyₛ σ₁) lifts to
-- the σ₁-applied form; sym reverses the direction; then
-- non-anchor-to-fin3-cong handles the proof-component difference.
------------------------------------------------------------------------

restrict-hom-∙ :
  (anchor : Axis) {σ₁ σ₂ : Permutation}
  (p₁ : Stab anchor σ₁) (p₂ : Stab anchor σ₂) (i : Fin 3) →
  SFin.apply (restrict anchor
               (σ₁ · σ₂ , Stab-∙ anchor {σ₁} {σ₂} p₁ p₂)) i
  ≡ SFin.apply (restrict anchor (σ₁ , p₁) SFin.·
                restrict anchor (σ₂ , p₂)) i
restrict-hom-∙ anchor {σ₁} {σ₂} p₁ p₂ i =
  non-anchor-to-fin3-cong anchor axis-eq _ _
  where
    X : Axis
    X = fin3-to-non-anchor anchor i

    σ₂X-≢ : applyₛ σ₂ X ≢ anchor
    σ₂X-≢ = stab-preserves-≢ anchor σ₂ p₂ X (fin3-to-non-anchor-≢ anchor i)

    axis-eq :
      applyₛ σ₁ (applyₛ σ₂ X)
      ≡ applyₛ σ₁ (fin3-to-non-anchor anchor
                    (non-anchor-to-fin3 anchor (applyₛ σ₂ X) σ₂X-≢))
    axis-eq =
      cong (applyₛ σ₁) (sym (non-anchor-fin3-non-anchor anchor (applyₛ σ₂ X) σ₂X-≢))

------------------------------------------------------------------------
-- restrict-hom-⁻¹: restrict preserves inverse — by definition.
--
-- Both sides are restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i:
--   LHS  = restrict anchor (σ ⁻¹ , Stab-inv anchor σ p)'s apply at i
--        = restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i.
--   RHS  = SFin.apply ((restrict anchor (σ,p)) SFin.⁻¹) i
--        = SFin.invₐ (restrict anchor (σ,p)) i
--        = restrict-invₐ anchor σ p i
--        = restrict-apply anchor (σ ⁻¹) (Stab-inv anchor σ p) i.
-- refl.
------------------------------------------------------------------------

restrict-hom-⁻¹ :
  (anchor : Axis) {σ : Permutation} (p : Stab anchor σ) (i : Fin 3) →
  SFin.apply (restrict anchor (σ ⁻¹ , Stab-inv anchor σ p)) i
  ≡ SFin.apply ((restrict anchor (σ , p)) SFin.⁻¹) i
restrict-hom-⁻¹ anchor p i = refl

------------------------------------------------------------------------
-- Notes
--
-- 1. With ε, ∙, ⁻¹ all preserved, restrict is a group homomorphism
--    from the (informal) Stab(anchor)-group into SFin.S-Group 3.
--    Combined with slice 14d's bijection, this means Stab(anchor) ≅
--    S_3 AS GROUPS, not just as sets.
--
-- 2. To package as a stdlib `IsGroupIsomorphism`, we'd need to
--    construct Stab(anchor) as a stdlib Group bundle (Carrier = Σ
--    Permutation (Stab anchor); operations from slice 12's Subgroup
--    closure laws, generalised to anchor). That's the slice 14f
--    move if downstream theorems require the bundle. The pointwise
--    homomorphism lemmas here are the structural content.
--
-- 3. The extend-side homomorphism (extend-hom-ε / ∙ / ⁻¹) follows
--    the same shape and is symmetric; deferred to slice 14g if
--    needed.
--
-- 4. Cross-references:
--    * Slice 14a: parametric Stab, Stab-inv, bridges.
--    * Slice 14b: restrict bundle + non-anchor-to-fin3-cong.
--    * Slice 14d: set-bijection iso.
------------------------------------------------------------------------
