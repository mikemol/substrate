------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.RotateCrumb
--
-- Defines: rotate-crumb
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.RotateCrumb where

open import Substrate.Pipeline.Brick.Witnessing
open import Substrate.Pipeline.Brick.Record
open import Substrate.Pipeline.Brick.Unit
open import Substrate.Pipeline.Brick.Type
open import Substrate.Foundation.Product
open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Bundle
open import Substrate.Algebra.GroupAction
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb
open import Substrate.Pipeline.Examples.RotateCrumb.V4Xor
open import Substrate.Pipeline.Examples.RotateCrumb.RotateCrumbType



rotate-crumb : Brick RotateCrumb-Type (Actionᴳ V₄-Group Crumb)
rotate-crumb = record
  { witnesses = D⇒S
  ; step      = λ ((c , g) , _) → v4-xor c g , tt
  }
