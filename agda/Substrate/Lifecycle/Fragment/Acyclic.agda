------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Acyclic
--
-- Defines: IsForest
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Acyclic where

open import Substrate.Foundation.Eq
open import Substrate.Algebra.Wedge.AxisWord.PackedNode


------------------------------------------------------------------------
-- THE ACYCLICITY PRECONDITION: at most one parent per child.
--
-- ⚑⚑ THIS IS THE HYPOTHESIS THE HEIGHT COMPUTATION SILENTLY DEPENDS ON, and
-- it is worth stating because the store's version has NO GUARD. `q_obs_height`
-- is a recursive CTE with no visited set and no depth cap; on a cyclic input
-- its `ht` would keep incrementing and it would not terminate. Nothing in the
-- schema constrains the edge relation to be acyclic — there is no CHECK, no
-- trigger, and no foreign key that could express it.
--
-- What makes it safe is a MEASUREMENT, and until this arc that measurement
-- had only ever been taken on the sandbox (184,232 child slots), while four
-- separate sites quoted it as a corpus fact. Measured now on the LIVE store,
-- full corpus:
--
--     total = 123,901,156 · post_order = 123,901,156 · max_parents = 1
--
-- ⚑ `max_parents = 1` IS STRONGER THAN ACYCLICITY AND THAT IS THE USEFUL
-- PART. A DAG is acyclic and can still have a node with two parents; here no
-- node does, so each core is a FOREST OF TREES. Consequences the fold relies
-- on, none of which follow from acyclicity alone: `height` is total and
-- single-valued (no need for `max` over several paths to be well-defined);
-- levels partition the observations; and a child's id is needed by exactly
-- one parent, so a level's statement has no intra-level dependency.
--
-- ⚑ NOTE THE DIRECTION OF THE SHARING. The INPUT is a forest — no sharing,
-- one parent each. The OUTPUT is a DAG — interning collapses structurally
-- identical subtrees, so a node may be reached from many parents. Sharing is
-- created BY the fold; it is not present in what the fold reads. Confusing
-- the two is easy because both are called "the SPPF", and it matters here:
-- the acyclicity hypothesis is about the INPUT only.
--
-- ⚑ STATED AS A HYPOTHESIS RATHER THAN PROVED, and that is not a weakness to
-- apologise for: the property is about a database's contents, so no Agda term
-- could establish it. What a proof CAN do is make the dependence explicit, so
-- that a future store violating it fails to satisfy this record instead of
-- silently non-terminating a CTE.
------------------------------------------------------------------------

module _ (Node : Set) (parentOf : Node → Node → Set) where

  -- Every child has at most one parent: the forest condition.
  IsForest : Set
  IsForest = (child p q : Node) → parentOf p child → parentOf q child → p ≡ q
