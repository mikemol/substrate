------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Anchor
--
-- Anchor-parametric stab-from-selector. For each anchor X and each
-- Selector, picks the corresponding Stab(X) element via the parametric
-- orbit-key-to-stab-anchor. The X=D specialisation coincides with
-- stab-from-selector up to definitional reduction.
--
-- The C/S/W siblings of stab-from-selector-fixes-D close the partial
-- coset the detector surfaces on stem 'stab-from-selector-fixes'.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Codeword.LiveS4Bijection.Anchor where

open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Cocycles.V4Signature.S4Iso
  using (orbit-key-to-stab-anchor; orbit-key-to-stab-anchor-fixes)
open import Substrate.Cocycles.V4Signature.Codeword.Live
  using (Selector; sel-fft; sel-tft; sel-ftf; sel-ttf; sel-ftt; sel-ttt)
open import Substrate.Cocycles.V4Signature.OrbitKey.Type
open import Substrate.Cocycles.V4Signature.Pairing.Type
open import Substrate.Cocycles.V4Signature.Chirality.Type
open import Substrate.Cocycles.V4Signature.S4Iso.Anchor

------------------------------------------------------------------------
-- Selector → OrbitKey table.
------------------------------------------------------------------------

selector-to-orbit-key : Selector → OrbitKey
selector-to-orbit-key sel-fft = α-pair , even   -- stab-id
selector-to-orbit-key sel-tft = α-pair , odd    -- stab-sw
selector-to-orbit-key sel-ftf = β-pair , odd    -- stab-cs
selector-to-orbit-key sel-ttf = γ-pair , odd    -- stab-cw
selector-to-orbit-key sel-ftt = β-pair , even   -- stab-csw
selector-to-orbit-key sel-ttt = γ-pair , even   -- stab-cws

------------------------------------------------------------------------
-- Anchor-parametric construction and its fixing law.
------------------------------------------------------------------------

stab-from-selector-anchor : Axis → Selector → Permutation
stab-from-selector-anchor X sel =
  orbit-key-to-stab-anchor X (selector-to-orbit-key sel)

stab-from-selector-fixes-anchor :
  (X : Axis) (sel : Selector) →
  apply (stab-from-selector-anchor X sel) X ≡ X
stab-from-selector-fixes-anchor X sel =
  orbit-key-to-stab-anchor-fixes X (selector-to-orbit-key sel)

stab-from-selector-fixes-C :
  (sel : Selector) → apply (stab-from-selector-anchor C sel) C ≡ C
stab-from-selector-fixes-C = stab-from-selector-fixes-anchor C

stab-from-selector-fixes-S :
  (sel : Selector) → apply (stab-from-selector-anchor S sel) S ≡ S
stab-from-selector-fixes-S = stab-from-selector-fixes-anchor S

stab-from-selector-fixes-W :
  (sel : Selector) → apply (stab-from-selector-anchor W sel) W ≡ W
stab-from-selector-fixes-W = stab-from-selector-fixes-anchor W
