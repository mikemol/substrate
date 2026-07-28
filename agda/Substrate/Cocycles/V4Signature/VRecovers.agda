------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.VRecovers
--
-- ⟡v-recovers-discharge (the NEGLECTED V₄ half of the composed-side
-- roundtrip). Proves, UNCONDITIONALLY:
--
--   v-recovers : (v : V₄) (s : S₃.Carrier) →
--     proj₁ (perm-to-compositional (compositional-to-perm (v , s))) ≡ v
--
-- i.e. v-for (embed v · embed-S₃ s) ≡ v. This is one of the two module
-- parameters CompSideRoundtrip.agda abstracts over; discharging it (with the
-- S₃ half s-recovers) closes ⟡full-s4-other-half = the two-sided S₄ bijection.
--
-- The chain (all in-tree lemmas, no new math):
--   v-for σ                       = v-of-axis-anchor D (apply σ D)      [V.v-for]
--   v-of-axis-anchor D x          = v-of-axis x                          [V, D-case]
--   apply (embed v · embed-S₃ s) D = apply (embed v) (apply (embed-S₃ s) D)  [·]
--   apply (embed-S₃ s) D         = D                                    [embed-S₃-D]
--   apply (embed v) D            = act-axis v D                         [embed.apply = act-axis]
--   v-of-axis (act-axis v D)      = v                                    [v-of-axis-unique, sym]
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.VRecovers where

open import Substrate.Axes.VOfAxis
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)
open import Substrate.Axes.Axis using (Axis; D)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.V4-Embedding using (embed; v-of-axis)
open import Substrate.Groups.SemidirectProduct.V using (v-for; v-of-axis-unique)

import Substrate.Groups.S3 as S₃
open import Substrate.Groups.S4-Iso.Embedding using (embed-S₃; compositional-to-perm)
open import Substrate.Groups.S4-Iso.Extract using (perm-to-compositional)
open import Substrate.Groups.S4-Iso.ExtractCorrect using (embed-S₃-D)
open import Substrate.Foundation.Product using (proj₁; _,_)

------------------------------------------------------------------------
-- Step lemma: v-of-axis (act-axis v D) ≡ v.
-- Direct from v-of-axis-unique v (act-axis v D) refl : v ≡ v-of-axis (act-axis v D).
------------------------------------------------------------------------

v-of-axis-act-D : (v : V₄) → v-of-axis (act-axis v D) ≡ v
v-of-axis-act-D v = sym (v-of-axis-unique v (act-axis v D) refl)

------------------------------------------------------------------------
-- v-recovers. apply (embed v · embed-S₃ s) D reduces:
--   = apply (embed v) (apply (embed-S₃ s) D)   [· composition]
--   = apply (embed v) D                          [embed-S₃-D]
--   = act-axis v D                                [embed.apply ≐ act-axis, definitional]
-- and v-for = v-of-axis of that; then v-of-axis-act-D closes it.
------------------------------------------------------------------------

v-recovers :
  (v : V₄) (s : S₃.Carrier) →
  proj₁ (perm-to-compositional (compositional-to-perm (v , s))) ≡ v
v-recovers v s =
  trans (cong (λ x → v-of-axis (apply (embed v) x)) (embed-S₃-D s))
        (v-of-axis-act-D v)
