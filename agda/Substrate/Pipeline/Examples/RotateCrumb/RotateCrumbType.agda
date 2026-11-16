------------------------------------------------------------------------
-- Substrate.Pipeline.Examples.RotateCrumb.RotateCrumbType
--
-- Defines: RotateCrumb-Type
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Pipeline.Examples.RotateCrumb; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Substrate.Pipeline.Examples.RotateCrumb.RotateCrumbType where

open import Substrate.Pipeline.Brick.Unit
open import Substrate.Pipeline.Brick.Type
open import Substrate.Foundation.Product
open import Substrate.Pipeline.Brick
open import Substrate.Groups.V4.Bijection.V4
open import Substrate.Foundation.Eq
open import Substrate.Pipeline.Examples.RotateCrumb.Crumb



-- ⟡set1-paydown: BrickType edges are now type indices — moved into the annotation; body is the tag.
RotateCrumb-Type : BrickType (Crumb × V₄) Crumb ⊤ ⊤
RotateCrumb-Type = record {}
