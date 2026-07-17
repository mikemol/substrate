------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.Pretopology
--
-- UP15 of the UP-topos arc per [scratch/up_topos_arc_plan.md].
--
-- A Grothendieck pretopology on UPCategory: an assignment to each
-- object U : O of a set of UPCovers (the "designated covers") closed
-- under stability + transitivity + identity.
--
-- ⟡ta-upterm: objects are the Set₀ alphabet O; homs are UPTerm O Hom.
-- (O, Hom) enter via the enclosing section.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.Pretopology where

open import Substrate.Category.UniversalProperty.Coverage using (UPCover)

module _ (O : Set) (Hom : O → O → Set) where

  ------------------------------------------------------------------------
  -- 1. Pretopology record.
  ------------------------------------------------------------------------

  -- ⟡set1-paydown: every field is Set-valued — the `designated : … → Set`
  -- family AND the three bare `_-axiom-stated : Set` placeholders (each a
  -- carrier-shaped `: Set` field).  Lifting all four to module parameters lands
  -- UPPretopology in Set (was Set₃); the record names the shape via its
  -- parameters (nothing constructs or quantifies over it — the sole consumer,
  -- Phase2, only re-exports the name).
  module _
    (designated : (U : O) (I : Set) → UPCover O Hom U I → Set)
    (identity-axiom-stated     : Set)
    (stability-axiom-stated    : Set)
    (transitivity-axiom-stated : Set)
    where
    record UPPretopology : Set where

------------------------------------------------------------------------
-- 2. Capstone for UP15.
--
-- UP16 supplies the axiom statements explicitly; UP17 the discrete
-- pretopology (everything is a cover); UP18-UP20 saturation +
-- concrete instances + capstone.
------------------------------------------------------------------------
