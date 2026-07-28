------------------------------------------------------------------------
-- Substrate.Groups.S4
--
-- The symmetric group S_4 — bijections of the 4-element AXES set.
-- Thin adapter over Substrate.Groups.Symmetric instantiated at Axis.
--
-- All operations (_·_, ε, _⁻¹), equivalence (_≈_), congruences,
-- group axioms, and the substrate-native SetoidGroup bundle are
-- inherited from Symmetric.
--
-- See: catalog/cocycles.md § CY-5 — S_4 ≅ V_4 ⋊ S_3 identification.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4 where

open import Substrate.Algebra.SetoidGroup using (SetoidGroup)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)

-- Inherit all symmetric-group machinery via the Axis instance.
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.Symmetric.Eq Axis using (_≈_)
open import Substrate.Groups.Symmetric.Identity Axis using (ε)
open import Substrate.Groups.Symmetric.Permutation.Inverse Axis using (_⁻¹)
open import Substrate.Groups.Symmetric.Group Axis using (Symmetric-Group)
-- Alias the bundled SetoidGroup as S₄-Group for backwards
-- compatibility with downstream importers.
S₄-Group : SetoidGroup Permutation _≈_
S₄-Group = Symmetric-Group
