------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.SRecovers
--
-- ⟡s-recovers-discharge — the S₃ half of the composed-side roundtrip,
-- now PROVEN (was CompSideRoundtrip's remaining module parameter). With
-- VRecovers.v-recovers (the V₄ half) this closes ⟡full-s4-other-half:
-- the two-sided S₄ bijection TotalSpace ≃ tower-rung-3 is UNCONDITIONAL.
--
-- s-recovers : (v : V₄)(s : S₃.Carrier) →
--   proj₂ (perm-to-compositional (compositional-to-perm (v , s))) S₃.≈ s
--
-- The chain (all in-tree, no new obligations):
--   proj₂ (perm-to-compositional (embed v · embed-S₃ s))
--                                 = extract-s (s-for (embed v · embed-S₃ s))
--   (A) s-for (embed v · embed-S₃ s) ≈ embed-S₃ s
--        [ apply (s-for σ) x = act-axis (v-for σ) (act-axis v (apply (embed-S₃ s) x));
--          v-for σ ≡ v (v-recovers); act-axis v ∘ act-axis v = id (act-axis-involutive) ]
--   extract-s respects ≈ (EmbedS3Faithful.extract-s-cong) ⇒ ≡ extract-s (embed-S₃ s)
--   extract-s (embed-S₃ s) S₃.≈ s   (EmbedS3Faithful.extract-embed-roundtrip = R)
--
-- The atom is R (the roundtrip), which sidesteps the CanonicalFaithful
-- row-inj / (L) INJECTIVITY route. Co-apex: EmbedS3Faithful (R + embed-S₃
-- faithfulness), CanonicalFaithful (row-inj), VRecovers (the V₄ half),
-- and Codeword.LiveS4Bijection (the PARALLEL axis-selector S₄ bijection).
--
-- --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.SRecovers where

open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong; subst)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.ActAxis using (act-axis)
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.V4-Embedding using (embed; act-axis-involutive)
open import Substrate.Groups.SemidirectProduct using (s-for)
open import Substrate.Groups.S4-Iso.Embedding using (embed-S₃; compositional-to-perm)
open import Substrate.Groups.S4-Iso.Extract using (extract-s; perm-to-compositional)
open import Substrate.Groups.S4-Iso.EmbedS3Faithful using (extract-embed-roundtrip; extract-s-cong)
open import Substrate.Cocycles.V4Signature.VRecovers using (v-recovers)
import Substrate.Cocycles.V4Signature.CompSideRoundtripVDischarged as VD
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Groups.Symmetric.Eq Axis
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis

------------------------------------------------------------------------
-- (A) the Stab-side residue collapses: s-for (embed v · embed-S₃ s) ≈ embed-S₃ s.
------------------------------------------------------------------------

s-for-collapses :
  (v : V₄) (s : S₃.Carrier) →
  s-for (compositional-to-perm (v , s)) ≈ embed-S₃ s
s-for-collapses v s x =
  trans (cong (λ w → act-axis w (act-axis v (apply (embed-S₃ s) x)))
              (v-recovers v s))
        (act-axis-involutive v (apply (embed-S₃ s) x))

------------------------------------------------------------------------
-- s-recovers: PROVEN (was the CompSideRoundtrip module parameter).
------------------------------------------------------------------------

s-recovers :
  (v : V₄) (s : S₃.Carrier) →
  proj₂ (perm-to-compositional (compositional-to-perm (v , s))) S₃.≈ s
s-recovers v s =
  S₃.≈-trans
    {extract-s (s-for (compositional-to-perm (v , s)))}
    {extract-s (embed-S₃ s)} {s}
    (subst-≈ (extract-s-cong
                {s-for (compositional-to-perm (v , s))} {embed-S₃ s}
                (s-for-collapses v s)))
    (extract-embed-roundtrip s)
  where
    subst-≈ : {x y : S₃.Carrier} → x ≡ y → x S₃.≈ y
    subst-≈ {x} p = subst (λ z → x S₃.≈ z) p (S₃.≈-refl x)

------------------------------------------------------------------------
-- The composed-side roundtrip, now UNCONDITIONAL (both halves proven).
-- Instantiates CompSideRoundtripVDischarged's last parameter.
------------------------------------------------------------------------

comp-side-roundtrip :
  (c : _) →
  (proj₁ (perm-to-compositional (compositional-to-perm c)) ≡ proj₁ c)
  × (proj₂ (perm-to-compositional (compositional-to-perm c)) S₃.≈ proj₂ c)
comp-side-roundtrip = VD.comp-side-roundtrip-mod-s s-recovers
