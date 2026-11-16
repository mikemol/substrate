------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Embedding.S3ApplyInvR
--
-- Defines: s3-apply-inv-r
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.S4-Iso.Embedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Embedding.S3ApplyInvR where

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
open import Substrate.Groups.S4-Iso.Embedding.CongV


s3-apply-inv-r : (s : S₃.Carrier) (x : Axis) →
                 s3-apply s (s3-inv-apply s x) ≡ x
s3-apply-inv-r s x =
  cong-trans (λ y → axis-of-v (φ-Act.act s y))
             (v-of-axis-axis-of-v (φ-Act.act (s S₃.⁻¹) (v-of-axis x)))
  (sym-trans (cong axis-of-v (φ-ActDot.act-∙ s (s S₃.⁻¹) (v-of-axis x)))
  (cong-trans axis-of-v (φ-cong-v (s S₃.∙ s S₃.⁻¹) S₃.ε (v-of-axis x) (S₃.inv-right s))
  (cong-trans axis-of-v (φ-ActEpsilon.act-ε (v-of-axis x))
         (axis-of-v-v-of-axis x))))
