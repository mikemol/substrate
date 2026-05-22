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

open import Substrate.Axes using (act-axis; D)
open import Substrate.Groups.S4
  using (Permutation; _≈_; _·_)
  renaming (apply to applyₛ)
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

σ-live-σ-roundtrip :
  (σ : Permutation) →
  live-to-permutation (permutation-to-live σ) ≈ σ
σ-live-σ-roundtrip σ z =
  trans step1 (trans step2 (trans step3 (sym (factorisation σ z))))
  where
    a-σ = axis-of-v (v-for σ)
    sel-σ = selector-from-stab (s-for σ)

    step1 :
      applyₛ (live-to-permutation (permutation-to-live σ)) z
      ≡ applyₛ (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
    step1 = cong (λ p → applyₛ p z) (live-perm-axis-sel a-σ sel-σ)

    step2 :
      applyₛ (embed (v-of-axis a-σ) · stab-from-selector sel-σ) z
      ≡ applyₛ (embed (v-for σ) · stab-from-selector sel-σ) z
    step2 =
      cong (λ v → act-axis v (applyₛ (stab-from-selector sel-σ) z))
           (v-of-axis-axis-of-v-id (v-for σ))

    step3 :
      applyₛ (embed (v-for σ) · stab-from-selector sel-σ) z
      ≡ applyₛ (embed (v-for σ) · s-for σ) z
    step3 = cong (act-axis (v-for σ))
                 (stab-roundtrip (s-for σ) (s-for-fixes-anchor D σ) z)
