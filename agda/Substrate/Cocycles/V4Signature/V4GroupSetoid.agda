------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.V4GroupSetoid
--
-- V₄'s group structure presented as a Setoid (the Gauge of the
-- CY-5 cocycle). Just the to-setoid forgetful applied to V₄-Group.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.V4GroupSetoid where

open import Substrate.Groups.V4.Bundle using (V₄-Group)
open import Substrate.Algebra.Group.ToSetoid using (to-setoid)

V₄-Group-Setoid = to-setoid V₄-Group
