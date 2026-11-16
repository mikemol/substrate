------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Skeleton
--
-- Defines: Skeleton
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Skeleton where

open import Substrate.Foundation.List
open import Substrate.Foundation.Product
open import Substrate.Lifecycle.Fragment.Signature


------------------------------------------------------------------------
-- THE SKELETON: the interned, SHARED structure — `IR`'s first carrier.
--
-- This is `_node ⋈ node_child`: a list of (node id, signature) pairs, where
-- the signature's `kids` already refer to other node ids. It is the part of
-- the promote that is genuinely a QUOTIENT — many observations map onto one
-- entry here, and that collapse is the point of an SPPF rather than a defect.
--
-- ⚑⚑ THE SKELETON ALONE IS NOT ENOUGH TO REBUILD THE SOURCE, AND THAT IS THE
-- WHOLE REASON `IR` HAS A SECOND CARRIER. `Reflection.agda` states the
-- consequence in operational terms: a reader that needs to tell one
-- occurrence of a subterm from another cannot do it from the skeleton, so a
-- drain licensed by "the structure is in the SPPF" would delete exactly what
-- that reader needs. The store has a live instance — `scope_fix` cannot
-- distinguish `Cyclic.Base 1` from `Cyclic.Base 2` from the projection alone,
-- and therefore pinned the drain floor at 0 indefinitely.
--
-- ⚑ MEASURED, and it is the sharpest single number in this arc:
-- `obs_node ⋈ _node` determines only **56.2%** of ekeys. Adding the child
-- list took the ambiguous set from 107 node_ids to **1**, and a re-measure
-- with the full `(node_id, ch)` pair reported **0 ambiguous, worst 0**. So
-- the residue is not a safety margin — without it, nearly half the source is
-- unrecoverable.
--
-- ⚑ NODE IDS ARE OPAQUE HERE, AND MUST STAY THAT WAY. In the store they are
-- minted from a non-transactional sequence: gaps are BY DESIGN, the claim
-- over-allocates (6,210 observations claiming 295 ids), and two concurrent
-- promoters formerly read `max(node_id)` and minted overlapping ids for
-- different signatures — silent corruption, not a conflict. Nothing may read
-- a node id as a count, a position, or an ordering. Treating `Id` as an
-- abstract set is what enforces that.
------------------------------------------------------------------------

module _ (Id : Set) where

  -- The interned nodes: an id paired with the signature it denotes.
  Skeleton : Set
  Skeleton = List (Id × NodeSig Id)
