------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Embedding.CongV
--
-- Defines: φ-cong-v
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.S4-Iso.Embedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Embedding.CongV where

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


φ-cong-v : (s₁ s₂ : S₃.Carrier) (v : V₄) → s₁ S₃.≈ s₂ →
           φ-Act.act s₁ v ≡ φ-Act.act s₂ v
φ-cong-v s₁ s₂ v eq = φ-ActCong.act-cong {s₁ = s₁} {s₂ = s₂} {v₁ = v} {v₂ = v} eq refl
