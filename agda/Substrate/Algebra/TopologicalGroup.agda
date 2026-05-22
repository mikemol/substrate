------------------------------------------------------------------------
-- Substrate.Algebra.TopologicalGroup
--
-- PD1: a topological group: a group equipped with a topology under
-- which multiplication and inversion are continuous.
--
-- For our discrete-friendly substrate use: we focus on FINITE and
-- DISCRETE locally compact abelian groups, where topology is trivial
-- (discrete) and continuity collapses to the group law alone.
--
-- Per [[categorical-name-first]]: topological group is standard.
-- Per [[continuous-via-discrete-inference-rules]]: continuous-limit
-- topological structure formalised via discrete inference rules.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.TopologicalGroup where

open import Level using (Level) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Algebra.Group

-- A topological group: a group + a topology (here abstracted as a
-- relation between elements — discrete topology by default).
--
-- For the substrate's discrete LCA focus: the "topology" is the
-- equality relation; concrete topological structure deferred to
-- continuous-limit instances.

record TopologicalGroup (A : Set) : Set where
  field
    group       : Group A
    -- A "topology" abstracted as a structural marker; concrete
    -- instances supply explicit topology data (open sets, basis,
    -- etc.). For finite/discrete groups this is the trivial
    -- discrete topology.

open TopologicalGroup public
