------------------------------------------------------------------------
-- Substrate.Lifecycle.Reflection
--
-- Defines: Reflection
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Reflection where

open import Substrate.Foundation.Eq


------------------------------------------------------------------------
-- A REFLECTION: a staging tier is drainable exactly when it is
-- RECONSTRUCTIBLE from what replaced it.
--
-- ⚑ THE LICENSE TO DELETE IS A ROUND-TRIP, NOT A BELIEF (user, 2026-08-07:
-- *"between the reverse index and the SPPF, the event tier should be
-- reconstructible; it's a reflection"*). The event tier is not storage to
-- compress — it is a BUFFER, and a buffer drains once its content exists
-- elsewhere in recoverable form. What makes that safe is not "the projection
-- probably suffices" but a CONSTRUCTION: rebuild the record, compare, delete
-- only on equality.
--
--     project    : Staged → Durable      the SPPF + reverse index
--     reconstruct : Durable → Staged     the reflection back
--     round-trip  : reconstruct (project s) ≡ s
--
-- ⚑ WITHOUT THE ROUND-TRIP THE DRAIN IS A GUESS, AND ONE ALREADY KNOWN TO BE
-- WRONG. `scope_fix` reads the event tier BECAUSE the projection alone is
-- unsound: `_node` keys on `sym ‖ child-syms`, so one module applied twice
-- collapses to a single node and the two applications become
-- indistinguishable (its docstring measures 16,842 of 350,827 slots packed
-- that way). A drain licensed by "the structure is in the SPPF" would delete
-- exactly what that reader needs.
--
-- ⚑ THE REVERSE INDEX IS THE RESIDUE THAT UNDOES THE COLLAPSE. Interning is
-- `recon`: the node is the base, the OCCURRENCE is what was quotiented away.
-- Carrying `node → [(core, local)]` restores it, so two applications land on
-- one `_node` and two occurrence entries. This is `intern_signature`'s
-- `⟨CARRIER⟩`/`unhold_path` at the TIER level — converge the key, keep the
-- path back, never a lossy erase.
--
-- ⚑ AND THE STAGES NEED NO SHARED TRANSACTION. `project` and `reconstruct`
-- are separate; the drain is licensed by a per-core equality that can be
-- checked long after the projection ran. A core that fails to reconstruct
-- does not drain — the failure is a FINDING, surfaced at the check, rather
-- than corruption discovered by a reader months later.
------------------------------------------------------------------------

record Reflection {S D : Set} (project : S → D) (reconstruct : D → S) : Set where
  constructor reflection
  field
    round-trip : (s : S) → reconstruct (project s) ≡ s
