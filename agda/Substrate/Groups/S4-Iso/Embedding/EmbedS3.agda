------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Embedding.EmbedS3
--
-- Defines: embed-S₃
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.S4-Iso.Embedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Embedding.EmbedS3 where

open import Substrate.Axes.Axis
open import Substrate.Axes.VOfAxis
open import Substrate.Axes.AxisOfV
open import Substrate.Axes.AxisRoundtrip
open import Substrate.Axes.V4Roundtrip
open import Substrate.Groups.V4.Bijection.V4
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Actions.S3-on-V4.Dispatch.Act as φ-Act
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActCong as φ-ActCong
import Substrate.Groups.Actions.S3-on-V4.Composition.ActDot as φ-ActDot
import Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilon as φ-ActEpsilon
import Substrate.Groups.Actions.S3-on-V4.HomSwaps.ActHom as φ-ActHom
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Groups.S4-Iso.Embedding.S3Apply
open import Substrate.Groups.S4-Iso.Embedding.S3InvApply
open import Substrate.Groups.S4-Iso.Embedding.S3ApplyInvR
open import Substrate.Groups.S4-Iso.Embedding.S3InvApplyL



------------------------------------------------------------------------
-- embed-S₃: S₃ → Permutation Axis.
------------------------------------------------------------------------

embed-S₃ : S₃.Carrier → Permutation
embed-S₃ s = record
  { apply = s3-apply s
  ; invₐ  = s3-inv-apply s
  ; inv-l = s3-inv-apply-l s
  ; inv-r = s3-apply-inv-r s
  }
