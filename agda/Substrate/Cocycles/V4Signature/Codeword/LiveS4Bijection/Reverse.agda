------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Reverse
--
-- Reverse round trip on the Live side (codeword level):
--
--   proj₁ (permutation-to-live (live-to-permutation lv)) ≡ proj₁ lv
--
-- Plus the helpers selector-from-stab-resp-≈ and s-for-of-live-perm-≈.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Reverse where

open import Substrate.Foundation.Product using (_,_; proj₁)
open import Substrate.Foundation.Eq
  using (_≡_; sym; trans; cong; cong₂; cong-trans)

open import Substrate.Axes.Axis using (Axis; D; C; S)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Groups.Symmetric.Permutation.Compose Axis using (_·_)
open import Substrate.Groups.V4-Embedding
  using (embed; act-axis-involutive)
open import Substrate.Groups.SemidirectProduct
  using (v-of-axis; v-of-axis-anchor-sends; v-for; s-for)
open import Substrate.Cocycles.V4Signature.Codeword
  using (Live)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; live-to-axis-selector; axis-selector-to-live)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4
  using (stab-from-selector; live-to-permutation)
open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Iso
  using (axis-of-v; axis-of-v-v-of-axis-id;
         classify-CS-to-selector; selector-from-stab;
         selector-stab-id; permutation-to-live)

open import Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Roundtrips
  using (stab-from-selector-fixes-D; axis-selector-roundtrip-cw)
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Axes.VOfAxis
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Cocycles.V4Signature.Codeword.Subtypes

------------------------------------------------------------------------
-- Helper: selector-from-stab respects pointwise equivalence on Stab(D).
------------------------------------------------------------------------

selector-from-stab-resp-≈ :
  (σ τ : Permutation) → σ ≈ τ →
  selector-from-stab σ ≡ selector-from-stab τ
selector-from-stab-resp-≈ σ τ σ≈τ =
  cong₂ classify-CS-to-selector (σ≈τ C) (σ≈τ S)

------------------------------------------------------------------------
-- Helper: s-for (embed v · stab-from-selector sel) ≈ stab-from-selector sel.
------------------------------------------------------------------------

s-for-of-live-perm-≈ :
  (a : Axis) (sel : Selector) →
  s-for (embed (v-of-axis a) · stab-from-selector sel)
  ≈ stab-from-selector sel
s-for-of-live-perm-≈ a sel z =
  trans
    (cong (λ v → act-axis v
                  (act-axis (v-of-axis a)
                    (apply (stab-from-selector sel) z)))
          v-for-σ'-eq)
    (act-axis-involutive (v-of-axis a)
                          (apply (stab-from-selector sel) z))
  where
    σ'D≡a : apply (embed (v-of-axis a) · stab-from-selector sel) D ≡ a
    σ'D≡a = trans
              (cong (act-axis (v-of-axis a))
                    (stab-from-selector-fixes-D sel))
              (v-of-axis-anchor-sends D a)

    v-for-σ'-eq :
      v-for (embed (v-of-axis a) · stab-from-selector sel)
      ≡ v-of-axis a
    v-for-σ'-eq = cong v-of-axis σ'D≡a

------------------------------------------------------------------------
-- The reverse round-trip at codeword level.
--
-- The `with live-to-axis-selector lv in p` commits to the decoded
-- (a, sel) so that `live-to-permutation lv` reduces to
-- `embed (v-of-axis a) · stab-from-selector sel = σ'`.
------------------------------------------------------------------------

live-σ-live-roundtrip :
  (lv : Live) →
  proj₁ (permutation-to-live (live-to-permutation lv))
  ≡ proj₁ lv
live-σ-live-roundtrip lv with live-to-axis-selector lv in p-decoded
... | a , sel =
  cong-trans (λ as → proj₁ (axis-selector-to-live as)) recovers
             cw-via-roundtrip
  where
    σ' : Permutation
    σ' = embed (v-of-axis a) · stab-from-selector sel

    σ'D≡a : apply σ' D ≡ a
    σ'D≡a = cong-trans (act-axis (v-of-axis a))
                       (stab-from-selector-fixes-D sel)
                       (v-of-axis-anchor-sends D a)

    v-for-σ'-eq : v-for σ' ≡ v-of-axis a
    v-for-σ'-eq = cong v-of-axis σ'D≡a

    axis-recovers : axis-of-v (v-for σ') ≡ a
    axis-recovers = cong-trans axis-of-v v-for-σ'-eq
                               (axis-of-v-v-of-axis-id a)

    selector-recovers : selector-from-stab (s-for σ') ≡ sel
    selector-recovers =
      trans (selector-from-stab-resp-≈ (s-for σ')
                                        (stab-from-selector sel)
                                        (s-for-of-live-perm-≈ a sel))
            (selector-stab-id sel)

    recovers :
      (axis-of-v (v-for σ') , selector-from-stab (s-for σ'))
      ≡ (a , sel)
    recovers = cong₂ _,_ axis-recovers selector-recovers

    cw-via-roundtrip : proj₁ (axis-selector-to-live (a , sel)) ≡ proj₁ lv
    cw-via-roundtrip =
      cong-trans (λ as → proj₁ (axis-selector-to-live as))
                 (sym p-decoded)
                 (axis-selector-roundtrip-cw lv)
