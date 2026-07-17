------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Powerset
--
-- UP35 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- The powerset object 𝒫(X) in a topos: the exponential Ω^X.
-- Substrate-honest signature.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Powerset where


------------------------------------------------------------------------
-- 1. Powerset signature.
--
-- Given a presheaf P, the powerset 𝒫(P) is the presheaf whose
-- U-sections are "Ω-valued maps from P(U)". Concrete construction
-- = exponential Ω^P.
------------------------------------------------------------------------

-- ⟡rc-deletes (⟡rerank2-floor-dissolve): the `PowersetType` signature-stub
-- (uninhabited, unconsumed Set₁ obligation surface) is DELETED — dead
-- scaffolding for a deferred exponential Ω^P, not a fiber-family holder.

------------------------------------------------------------------------
-- 2. Capstone for UP35.
--
-- Powerset signature lands. UP36 supplies the geometric-morphism
-- record.
------------------------------------------------------------------------
