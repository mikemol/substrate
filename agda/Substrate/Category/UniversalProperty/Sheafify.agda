------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Sheafify
--
-- UP25 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- Sheafification: a functor sheafify : PSh → Sh left adjoint to the
-- forgetful inclusion. The signature is named; the concrete construction
-- (plus-construction) is deferred to a follow-up arc.
--
-- ⟡ta-upterm: over the Set₀ object-alphabet O (Presheaf/Sheaf now O-form).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Sheafify where


module _ (O : Set) (Hom : O → O → Set) where

  -- ⟡rc-deletes (⟡rerank2-floor-dissolve): the `SheafifyType` signature-stub
  -- (uninhabited, unconsumed Set₁ obligation surface) is DELETED — dead
  -- scaffolding for the deferred plus-construction.

  -- Concrete construction deferred (the plus-construction).
