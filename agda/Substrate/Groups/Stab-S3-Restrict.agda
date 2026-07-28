------------------------------------------------------------------------
-- Substrate.Groups.Stab-S3-Restrict
--
-- Slice 14b: bundle slice 14a's restrict-apply / restrict-invₐ into
-- a full SFinP.Permutation 3 record, with the inv-l / inv-r round-
-- trip proofs.
--
-- The proofs chain three pieces:
--   1. non-anchor-fin3-non-anchor: fin3-to-non-anchor ∘ non-anchor-
--      to-fin3 ≡ id (over non-anchor axes).
--   2. S_4's inv-l σ / inv-r σ.
--   3. non-anchor-to-fin3-irr: proof-irrelevance for the ≢-component
--      (16 cases: 12 refl + 4 ⊥-elim).
--
-- A helper `non-anchor-to-fin3-cong` combines axis-substitution +
-- proof-irrelevance: given x ≡ y and proofs of x ≢ anchor and y ≢
-- anchor, the two non-anchor-to-fin3 values agree.
--
-- See: Substrate.Groups.Stab-S3 (slice 14a) — parametric Stab +
--      bridges + restrict-apply/invₐ as functions.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Stab-S3-Restrict where

open import Substrate.Foundation.Level using (0ℓ)
open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; _≢_; refl; sym; trans; cong)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis using (_⁻¹)
open import Substrate.Groups.Symmetric.Identity Axis using (ε)
import Substrate.Groups.SFin.Permutation as SFinP
open import Substrate.Groups.Stab-S3
  using (Stab; stab-preserves-≢; Stab-inv;
         fin3-to-non-anchor; fin3-to-non-anchor-≢;
         non-anchor-to-fin3; non-anchor-fin3-non-anchor;
         fin3-non-anchor-fin3;
         restrict-apply; restrict-invₐ)

------------------------------------------------------------------------
-- Proof-irrelevance: non-anchor-to-fin3 doesn't depend on the proof
-- argument (for non-anchor x — the anchor-x case is vacuous via
-- ⊥-elim).
--
-- 16 cases: 4 anchor × 4 x. 12 refls + 4 ⊥-elim of (p₁ refl).
------------------------------------------------------------------------

non-anchor-to-fin3-irr :
  (anchor x : Axis) (p₁ p₂ : x ≢ anchor) →
  non-anchor-to-fin3 anchor x p₁ ≡ non-anchor-to-fin3 anchor x p₂
non-anchor-to-fin3-irr D D p₁ p₂ = ⊥-elim (p₁ refl)
non-anchor-to-fin3-irr D C _  _  = refl
non-anchor-to-fin3-irr D S _  _  = refl
non-anchor-to-fin3-irr D W _  _  = refl
non-anchor-to-fin3-irr C D _  _  = refl
non-anchor-to-fin3-irr C C p₁ p₂ = ⊥-elim (p₁ refl)
non-anchor-to-fin3-irr C S _  _  = refl
non-anchor-to-fin3-irr C W _  _  = refl
non-anchor-to-fin3-irr S D _  _  = refl
non-anchor-to-fin3-irr S C _  _  = refl
non-anchor-to-fin3-irr S S p₁ p₂ = ⊥-elim (p₁ refl)
non-anchor-to-fin3-irr S W _  _  = refl
non-anchor-to-fin3-irr W D _  _  = refl
non-anchor-to-fin3-irr W C _  _  = refl
non-anchor-to-fin3-irr W S _  _  = refl
non-anchor-to-fin3-irr W W p₁ p₂ = ⊥-elim (p₁ refl)

-- Combined cong-and-irrelevance helper: given x ≡ y, the
-- non-anchor-to-fin3 values agree regardless of proof choice.
non-anchor-to-fin3-cong :
  (anchor : Axis) {x y : Axis} →
  x ≡ y → (p₁ : x ≢ anchor) (p₂ : y ≢ anchor) →
  non-anchor-to-fin3 anchor x p₁ ≡ non-anchor-to-fin3 anchor y p₂
non-anchor-to-fin3-cong anchor refl p₁ p₂ =
  non-anchor-to-fin3-irr anchor _ p₁ p₂

------------------------------------------------------------------------
-- Round-trip proofs for restrict-apply / restrict-invₐ.
--
-- The chain (for inv-l, symmetric for inv-r):
--   restrict-invₐ (restrict-apply i)
--     = non-anchor-to-fin3 anchor (apply (σ⁻¹) (fin3-to-non-anchor anchor j)) p
--       where j = restrict-apply σ i.
--     ≡ non-anchor-to-fin3 anchor a (fin3-to-non-anchor-≢ anchor i)
--       by axis-substitution (fin3-non-anchor round-trip + inv-l σ)
--       and proof-irrelevance.
--     ≡ i  by fin3-non-anchor-fin3.
------------------------------------------------------------------------

restrict-inv-l :
  (anchor : Axis) (σ : Permutation) (σ-stab : Stab anchor σ) (i : Fin 3) →
  restrict-invₐ anchor σ σ-stab (restrict-apply anchor σ σ-stab i) ≡ i
restrict-inv-l anchor σ σ-stab i =
  trans (non-anchor-to-fin3-cong anchor σ⁻¹-fin3j σ⁻¹-fin3j-≢
                                  (fin3-to-non-anchor-≢ anchor i))
        (fin3-non-anchor-fin3 anchor i)
  where
    a : Axis
    a = fin3-to-non-anchor anchor i

    σa-≢ : apply σ a ≢ anchor
    σa-≢ = stab-preserves-≢ anchor σ σ-stab a (fin3-to-non-anchor-≢ anchor i)

    j : Fin 3
    j = restrict-apply anchor σ σ-stab i

    σ⁻¹-fin3j :
      apply (σ ⁻¹) (fin3-to-non-anchor anchor j) ≡ a
    σ⁻¹-fin3j =
      trans (cong (apply (σ ⁻¹))
                  (non-anchor-fin3-non-anchor anchor (apply σ a) σa-≢))
            (inv-l σ a)

    σ⁻¹-fin3j-≢ :
      apply (σ ⁻¹) (fin3-to-non-anchor anchor j) ≢ anchor
    σ⁻¹-fin3j-≢ =
      stab-preserves-≢ anchor (σ ⁻¹) (Stab-inv anchor σ σ-stab)
                       (fin3-to-non-anchor anchor j)
                       (fin3-to-non-anchor-≢ anchor j)

restrict-inv-r :
  (anchor : Axis) (σ : Permutation) (σ-stab : Stab anchor σ) (i : Fin 3) →
  restrict-apply anchor σ σ-stab (restrict-invₐ anchor σ σ-stab i) ≡ i
restrict-inv-r anchor σ σ-stab i =
  trans (non-anchor-to-fin3-cong anchor σ-fin3k σ-fin3k-≢
                                  (fin3-to-non-anchor-≢ anchor i))
        (fin3-non-anchor-fin3 anchor i)
  where
    a : Axis
    a = fin3-to-non-anchor anchor i

    σ⁻¹a-≢ : apply (σ ⁻¹) a ≢ anchor
    σ⁻¹a-≢ = stab-preserves-≢ anchor (σ ⁻¹) (Stab-inv anchor σ σ-stab) a
                              (fin3-to-non-anchor-≢ anchor i)

    k : Fin 3
    k = restrict-invₐ anchor σ σ-stab i

    σ-fin3k :
      apply σ (fin3-to-non-anchor anchor k) ≡ a
    σ-fin3k =
      trans (cong (apply σ)
                  (non-anchor-fin3-non-anchor anchor
                                              (apply (σ ⁻¹) a) σ⁻¹a-≢))
            (inv-r σ a)

    σ-fin3k-≢ :
      apply σ (fin3-to-non-anchor anchor k) ≢ anchor
    σ-fin3k-≢ =
      stab-preserves-≢ anchor σ σ-stab
                       (fin3-to-non-anchor anchor k)
                       (fin3-to-non-anchor-≢ anchor k)

------------------------------------------------------------------------
-- The bundled restrict map.
------------------------------------------------------------------------

restrict :
  (anchor : Axis) → Σ Permutation (Stab anchor) → SFinP.Permutation 3
restrict anchor (σ , σ-stab) = record
  { apply = restrict-apply anchor σ σ-stab
  ; invₐ  = restrict-invₐ anchor σ σ-stab
  ; inv-l = restrict-inv-l anchor σ σ-stab
  ; inv-r = restrict-inv-r anchor σ σ-stab
  }

------------------------------------------------------------------------
-- Notes
--
-- 1. The proof chains use `non-anchor-to-fin3-cong` (axis-substitution
--    + proof-irrelevance) to handle both:
--    - the axis equality (after the bridge round-trip + inv-l/inv-r σ),
--    - the proof-component difference (different ≢-anchor proofs
--      threaded through the chain).
--
-- 2. Slice 14c will define the reverse `extend` map (16-case axis
--    enumeration) and prove the cross round trips.
--
-- 3. Slice 14d will bundle restrict and extend as an Iso and add the
--    group homomorphism proofs (composition / identity / inverse
--    preserved).
--
-- All under `--safe --without-K`; no postulates.
------------------------------------------------------------------------
