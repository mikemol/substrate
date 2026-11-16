------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Embedding.CompositionalToPerm
--
-- Defines: compositional-to-perm
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Groups.S4-Iso.Embedding; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Embedding.CompositionalToPerm where

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
open import Substrate.Groups.V4-Embedding
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Permutation.Compose Axis
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.SymTrans
open import Substrate.Foundation.Eq.CongTrans
open import Substrate.Groups.S4-Iso.Embedding.EmbedS3
open import Substrate.Foundation.Product



------------------------------------------------------------------------
-- compositional-to-perm: forward direction of the iso.
------------------------------------------------------------------------

compositional-to-perm : S4C.Carrier → Permutation
compositional-to-perm (v , s) = embed v · embed-S₃ s
