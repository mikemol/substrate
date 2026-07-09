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
open import Substrate.Axes using (Axis; D; C; S; W)

-- Inherit all symmetric-group machinery via the Axis instance.
open import Substrate.Groups.Symmetric Axis public

-- Alias the bundled SetoidGroup as S₄-Group for backwards
-- compatibility with downstream importers.
S₄-Group : SetoidGroup Permutation _≈_
S₄-Group = Symmetric-Group
