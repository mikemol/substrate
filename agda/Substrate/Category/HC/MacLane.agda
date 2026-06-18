------------------------------------------------------------------------
-- Substrate.Category.HC.MacLane
--
-- HC8 of the higher-cat content arc per [scratch/up_topos_arc_plan.md].
--
-- Mac Lane coherence theorem UP: any two parallel composite-of-
-- associator-and-unitor-and-identity morphisms in a monoidal
-- category are equal (the "every diagram of associators and
-- unitors commutes" coherence theorem).
--
-- SCOPE (honest): `MacLane-UP` below is the sanctioned ⊤-PLACEHOLDER
-- (`HC.PlaceholderUP.placeholder`). The ABSTRACT theorem — "pentagon +
-- triangle ⟹ all such diagrams commute, for ANY monoidal category" — is
-- NOT proved here (it is the genuine coherence theorem, a free-monoidal-
-- category argument out of this slice's scope). What IS proved, CONCRETELY
-- and by refl, is the coherence of the substrate's actual monoidal
-- structure (the cross-carrier tensor ⊗ᴰ): pentagon + triangle + hexagon +
-- naturality all hold in `Algebra.Wedge.Monoidal` (with its own HONEST
-- SCOPE note on the --without-K morphism-equality level). So the realized
-- Mac Lane coherence lives THERE; this module only NAMES the abstract UP as
-- a placeholder pending the general theorem.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.HC.MacLane where

open import Substrate.Category.UniversalProperty using (UPArrow)
open import Substrate.Category.HC.PlaceholderUP using (placeholder)

MacLane-UP : UPArrow
MacLane-UP = placeholder
