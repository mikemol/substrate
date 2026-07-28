------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Forward
--
-- Forward round trip on the Permutation side:
--
--   live-to-permutation (permutation-to-live σ) ≈ σ
--
-- Proof chain:
--   live-to-permutation (axis-selector-to-live (axis-of-v (v-for σ),
--                                               selector-from-stab (s-for σ)))
--   ≡ embed (v-of-axis (axis-of-v (v-for σ))) ·
--     stab-from-selector (selector-from-stab (s-for σ))
--                                        [live-perm-axis-sel]
--   ≡ embed (v-for σ) ·
--     stab-from-selector (selector-from-stab (s-for σ))
--                                        [v-of-axis-axis-of-v-id]
--   ≈ embed (v-for σ) · s-for σ          [stab-roundtrip on s-for σ]
--   ≈ σ                                  [factorisation]
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Forward where

open import Substrate.Foundation.Eq using (_≡_; sym; trans; cong)

open import Substrate.Axes.Axis
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.V4-Embedding using (embed)
open import Substrate.Groups.SemidirectProduct
  using (v-of-axis; v-for; s-for; s-for-fixes-anchor; factorisation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (stab-from-selector; live-to-permutation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
  using (axis-of-v; v-of-axis-axis-of-v-id;
         selector-from-stab; permutation-to-live)

open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Roundtrips
  using (live-perm-axis-sel; stab-roundtrip)
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Axes.VOfAxis
open import Substrate.Groups.SemidirectProduct.Factorisation

σ-live-σ-roundtrip :
  (σ : Permutation) →
  live-to-permutation (permutation-to-live σ) ≈ σ
σ-live-σ-roundtrip σ z =
  trans step1 (trans step2 (trans step3 (sym (factorisation σ z))))
  where
    a-σ = axis-of-v (v-for σ)
    sel-σ = selector-from-stab (s-for σ)

    step1 :
      apply (live-to-permutation (permutation-to-live σ)) z
      ≡ apply (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
    step1 = cong (λ p → apply p z) (live-perm-axis-sel a-σ sel-σ)

    step2 :
      apply (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
      ≡ apply (embed (v-for σ) · stab-from-selector sel-σ) z
    step2 =
      cong (λ v → act-axis v (apply (stab-from-selector sel-σ) z))
           (v-of-axis-axis-of-v-id (v-for σ))

    step3 :
      apply (embed (v-for σ) · stab-from-selector sel-σ) z
      ≡ apply (embed (v-for σ) · s-for σ) z
    step3 = cong (act-axis (v-for σ))
                 (stab-roundtrip (s-for σ) (s-for-fixes-anchor D σ) z)
