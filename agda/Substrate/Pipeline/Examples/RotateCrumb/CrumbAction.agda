------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.CrumbAction
--
-- Defines: crumb-action
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.CrumbAction where

open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Groups.V4.Operations
open import Substrate.Groups.V4.Bundle
open import Substrate.Algebra.GroupAction
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb
open import Substrate.Pipeline.Examples.RotateCrumb.V4Xor
open import Substrate.Pipeline.Examples.RotateCrumb.ActId
open import Substrate.Pipeline.Examples.RotateCrumb.ActDot



crumb-action : Actionᴳ V₄-Group Crumb
crumb-action = record
  { act    = λ g c → v4-xor c g
  ; act-id = act-idᶜ
  ; act-∙  = act-∙ᶜ
  }
