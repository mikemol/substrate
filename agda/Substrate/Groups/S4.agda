------------------------------------------------------------------------
-- Substrate.Groups.S4
--
-- The symmetric group S_4 — bijections of the 4-element AXES set.
-- Thin adapter over Substrate.Groups.Symmetric instantiated at Axis.
--
-- All operations (_·_, ε, _⁻¹), equivalence (_≈_), congruences,
-- group axioms, and the stdlib Group bundle are inherited from
-- Symmetric. The only S₄-specific content is the alias S₄-Group
-- for the bundled Group record, preserving the name downstream
-- modules import.
--
-- Per [[feedback-v4-typeclass-architecture]]: zero duplicated
-- machinery. New symmetric groups (over different carriers) live in
-- Substrate.Groups.SFin (over Fin n) or instantiate Symmetric
-- directly.
--
-- See: catalog/cocycles.md § CY-5 — S_4 ≅ V_4 ⋊ S_3 identification.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4 where

open import Algebra.Bundles using (Group)
open import Level using (0ℓ)

open import Substrate.Axes using (Axis; D; C; S; W)

-- Inherit all symmetric-group machinery: Permutation, _≈_, _·_, ε,
-- _⁻¹, ≈-{refl,sym,trans}, ·-{assoc,cong}, ε-{left,right},
-- inv-{left,right}, ⁻¹-cong, isMagma/Semigroup/Monoid/Group,
-- Symmetric-Group, σ-injective.
open import Substrate.Groups.Symmetric Axis public

-- Alias the bundled Group as S₄-Group for backwards compatibility.
S₄-Group : Group 0ℓ 0ℓ
S₄-Group = Symmetric-Group
