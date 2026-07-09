------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4IsTorsor
--
-- V₄ is a torsor over itself: free transitive action with no
-- canonical baseline. Bundles V4-acts-on-itself + freeness +
-- transitivity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4IsTorsor where

open import Substrate.Cocycle using (IsTorsor)
open import Substrate.Groups.V4 using (V₄)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Cocycles.V4Signature.V4GroupSetoid  using (V₄-Group-Setoid)
open import Substrate.Cocycles.V4Signature.V4ActsOnItself using (V4-acts-on-itself)
open import Substrate.Cocycles.V4Signature.V4LeftCancel   using (V4-left-cancel)
open import Substrate.Cocycles.V4Signature.V4Transitive   using (V4-transitive)

V4-is-torsor : IsTorsor V₄ _≡_ V₄-Group-Setoid V₄
V4-is-torsor = record
  { action     = V4-acts-on-itself
  ; free       = V4-left-cancel
  ; transitive = V4-transitive
  }
