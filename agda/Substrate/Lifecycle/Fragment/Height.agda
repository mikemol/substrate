------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Height
--
-- Defines: ChildBelow
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Height where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Algebra.Wedge.AxisWord.PackedNode
open import Substrate.Category.CentralizerDescent.Tree


------------------------------------------------------------------------
-- THE WELL-FOUNDED MEASURE: a child is strictly BELOW its parent.
--
-- ⚑⚑ HEIGHT IS THE MEASURE; POST-ORDER IS A DIFFERENT, STRONGER FACT. The
-- two are easy to conflate because the store satisfies both, but they are not
-- the same statement and only one of them is the fold's actual requirement:
--
--   · HEIGHT   — `height (clid e) < height (plid e)`. This is what makes the
--     level schedule sound: `pack_level` at height k reads its children's ids
--     out of `obs_node`, so every child must already be numbered, and
--     ascending height gives exactly that. Levels are internally independent,
--     which is why each is ONE set-based statement.
--   · POST-ORDER — `clid < plid` on the raw `local_id`s. A fact about the
--     INGEST's numbering, not about the term structure. The Python fold
--     exploits it to visit children before parents in a single ascending pass,
--     avoiding both recursion and a height computation.
--
-- Post-order implies a height ordering; height does NOT imply post-order. So
-- height is the WEAKER and more primitive hypothesis, and is what this module
-- states. Recording post-order separately keeps the SQL path from silently
-- depending on a property only the Python path needs.
--
-- ⚑ THIS IS A PARAMETER, NOT A COMPUTATION, AND DELIBERATELY SO. `height` in
-- the store is computed by a recursive CTE from the leaves upward; importing
-- that computation here would re-derive a quantity the store already owns
-- (and would trip the rederive ratchet). What the proof needs is only the
-- ORDERING PROPERTY, so that is what is assumed — the honest conditional.
--
-- ⚑⚑ AND THE PROPERTY IS NOW CORPUS-VERIFIED, WHICH IT WAS NOT WHEN THIS
-- MODULE WAS PLANNED. Measured on the live store over the FULL corpus:
--
--     total = 123,901,156 · post_order = 123,901,156 · max_parents = 1
--
-- i.e. every one of 123.9M edges satisfies `clid < plid`, with zero
-- exceptions — the stronger post-order fact, at 699x the scale of the
-- 177,370-edge sandbox sample that four files still quote as if it were the
-- corpus. The hypothesis below is therefore DISCHARGED WITH A WITNESS rather
-- than merely hoped for. It stays a hypothesis in the Agda because a proof
-- must not depend on a database measurement; the witness belongs in the
-- record, not in the type.
------------------------------------------------------------------------

module _ (Node : Set) (height : Node → ℕ) where

  -- The fold's requirement, as a relation on one parent/child pair.
  ChildBelow : Node → Node → Set
  ChildBelow child parent = height child < height parent
