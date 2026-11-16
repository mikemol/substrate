------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment
--
-- Defines: ObsRow, EdgeRow, Staged
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.List
open import Substrate.Foundation.Maybe


------------------------------------------------------------------------
-- THE FRAGMENT: `obs` and `edge` for ONE core. NOT the staged tier.
--
-- ⚑⚑ THE SCOPE LIMIT IS IN THE TYPE, NOT IN A COMMENT, AND THAT IS THE
-- WHOLE REASON THIS MODULE EXISTS. `reconstruct.py`'s own docstring says it:
-- *"the event tier is ten relations, of which this checks one … The
-- tier-level predicate does not exist yet."* So a `Reflection` claimed for
-- `Staged = the event tier` would be FALSE, and false in the direction that
-- licenses deleting rows nothing can rebuild. Naming the fragment as its own
-- carrier makes the unproved part unstatable rather than merely unstated.
--
-- ⚑ WHAT IS DELIBERATELY EXCLUDED, each with its reason:
--   · `unit_obs`  — no residue exists for it at all.
--   · `unit_node` — SET-valued `(unit_id, node_id)`, so a unit holding the
--     same node twice records ONE row. The multiplicity is quotiented away
--     and NOTHING restores it: unlike the occurrence collapse, this one has
--     no `obs_node` to undo it. An honest reflection cannot include it.
--   · `terms` / `path_seg` / `path_text` — the interning tier, which has no
--     `reflects_*` predicate and is a DECLARATION defect (F10's tier
--     misclassification), not a proof obligation.
--
-- ⚑ IDENTIFIERS ARE ABSTRACT, AND THAT IS A MEASURED CORRECTION. The store
-- spells every id `TEXT` (`schema.py --ddl`), not an integer — `ekey` is
-- base64 of a JSON document, `core_id` a base64 relpath. An outside model of
-- this schema proposed `bigint` throughout; under that reading the round-trip
-- is trivial and WRONG, because the byte-level rendering is what conjunct (2)
-- of the drain licence actually compares. Parameterizing over the id type
-- keeps this module from depending on either spelling.
------------------------------------------------------------------------

module _ (Id : Set) where

  -- ⚑ NAMED `ObsRow`/`EdgeRow`, NOT `Obs`/`Edge` — CAUGHT BY A GATE, NOT
  -- FORESEEN. `check_sumtype_ratchet` flagged `Obs` as a NEW duplicate against
  -- `Substrate.Category.UniversalProperty.DiagonalDoFComputable.Obs`. The two
  -- model unrelated things, so it is a name clash rather than a real
  -- duplicate — but the census keys on the NAME and cannot tell those apart,
  -- and a NEW key blocks 27 unrelated paydowns from recording. `…Row` also
  -- says the true thing: these are RELATION ROWS, not abstract observations.

  -- One observation: a position in a core, carrying its event key.
  -- `local_id` is ℕ; the store spells it INTEGER and dense per core.
  record ObsRow : Set where
    constructor obsRow
    field
      local : ℕ
      ekey  : Id

  -- One ordered parent→child edge. `ord` is dense 0..n-1 per parent —
  -- ⚑ ENFORCED, not merely measured: `ix_edge_pk` is UNIQUE on
  -- (core_id, plid, ord). That is stronger than the comment-level claim
  -- this plan started from, and it is the property the child-list encoding
  -- depends on.
  record EdgeRow : Set where
    constructor edgeRow
    field
      plid : ℕ
      ord  : ℕ
      clid : ℕ

  -- The staged side of the reflection, for ONE core.
  record Staged : Set where
    constructor staged
    field
      obss  : List ObsRow
      edges : List EdgeRow
