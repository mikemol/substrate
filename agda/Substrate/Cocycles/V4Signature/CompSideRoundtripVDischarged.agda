------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.CompSideRoundtripVDischarged
--
-- Crosslink: instantiates CompSideRoundtrip with the V₄ half (v-recovers)
-- DISCHARGED by the now-proven VRecovers.v-recovers, leaving ONLY the S₃ half
-- (s-recovers) as a parameter. So the composed-side roundtrip — hence the
-- two-sided S₄ bijection (⟡full-s4-other-half) — was blocked on exactly
-- ONE remaining obligation: embed-S₃ faithfulness (⟡embed-s3-*).
--
-- ⟡NOW DISCHARGED: s-recovers is PROVEN in Cocycles.V4Signature.SRecovers
-- (via Substrate.Groups.S4-Iso.EmbedS3Faithful's roundtrip atom
-- `extract-embed-roundtrip` + `embed-S₃-faithful`). SRecovers instantiates
-- THIS module's `comp-side-roundtrip-mod-s` with the proven s-recovers, so
-- SRecovers.comp-side-roundtrip is the UNCONDITIONAL two-sided S₄ bijection.
--
-- Before: CompSideRoundtrip abstracted over TWO obligations (v-recovers,
-- s-recovers). Then one theorem, one parameter (here). Now: both theorems.
-- This module remains the V₄-half crosslink in the import graph; SRecovers
-- is the S₃-half discharge.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.CompSideRoundtripVDischarged where

open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Groups.V4.Bijection using (V₄)
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.S4-Iso.Extract   using (perm-to-compositional)
open import Substrate.Groups.S4-Iso.Embedding using (compositional-to-perm)
open import Substrate.Foundation.Product using (proj₁; proj₂; _,_; _×_)

open import Substrate.Cocycles.V4Signature.VRecovers using (v-recovers)
import Substrate.Cocycles.V4Signature.CompSideRoundtrip as CSR

------------------------------------------------------------------------
-- With v-recovers discharged, comp-side-roundtrip needs only s-recovers.
------------------------------------------------------------------------

module _
  (s-recovers :
     (v : V₄) (s : S₃.Carrier) →
     proj₂ (perm-to-compositional (compositional-to-perm (v , s))) S₃.≈ s)
  where

  -- The composed-side roundtrip, now with the V₄ half PROVEN (not assumed).
  comp-side-roundtrip-mod-s :
    (c : _) →
    (proj₁ (perm-to-compositional (compositional-to-perm c)) ≡ proj₁ c)
    × (proj₂ (perm-to-compositional (compositional-to-perm c)) S₃.≈ proj₂ c)
  comp-side-roundtrip-mod-s = CSR.comp-side-roundtrip v-recovers s-recovers
