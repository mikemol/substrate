------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.Drains
--
-- Defines: promote-injective
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.Drains where

open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Drainable
open import Substrate.Lifecycle.Fragment
open import Substrate.Lifecycle.Fragment.IRInstance
open import Substrate.Lifecycle.Fragment.IsReflection
open import Substrate.Lifecycle.Fragment.Occurrence
open import Substrate.Lifecycle.Fragment.Skeleton
open import Substrate.WitnessTower.GradeMapInvariant
open import Substrate.Lifecycle.Reflection


------------------------------------------------------------------------
-- THE CONSUMER: draining the fragment loses nothing.
--
-- ⚑⚑⚑ THIS MODULE EXISTS BECAUSE A THEOREM NOTHING APPLIES IS AN ORPHANED
-- RUNG. `collapse_check` asks exactly one question of a new leaf — *"confirm
-- it is an intended capstone/leaf, NOT a built-then-orphaned rung"* — and it
-- is the right question: `IRRetraction` and `Lifecycle.Reflection` were each
-- proved, correct, and imported by nothing relevant, which is precisely how
-- two halves of one result sat unconnected in this tree. Adding a third
-- unconsumed structure would repeat the pattern rather than close it. So the
-- fan ends by USING the instance, not by stating it.
--
-- `drainable` is the general theorem (`Reflection project reconstruct →
-- project s₁ ≡ project s₂ → s₁ ≡ s₂`); this applies it at the fragment.
--
-- ⚑ WHAT IS AND IS NOT ESTABLISHED HERE, stated plainly because the
-- difference is what makes the drain safe rather than merely licensed:
--
--   IS   — GIVEN the round-trip, the promote is INJECTIVE on the fragment.
--          Two staged fragments with the same `(skeleton, residue)` are
--          equal, so deleting the staged copy cannot change what anything
--          reconstructs to.
--   NOT  — that the store's fold SATISFIES the round-trip. That is an
--          empirical property of a Python/SQL implementation and no Agda term
--          can establish it. The store checks it per core, by rebuilding and
--          comparing before any delete.
--   NOT  — anything about `unit_obs`, `unit_node`, or the interning tier.
--          `Staged` is `obs`/`edge` only, by construction.
--
-- ⚑⚑ AND THE VACUOUS CASE IS NOT EVIDENCE — a measured defect, not a
-- hypothetical. An empty core once satisfied the store's reflection check and
-- reported *"REFLECTS — 0 row(s) reconstructed exactly"*: **a core whose
-- events had not yet been written passed the gate that licenses deleting its
-- rows.** Injectivity holds vacuously on an empty fragment, so a consumer
-- must establish non-emptiness separately. This module proves a conditional;
-- it does not certify that the condition was met on any particular core.
------------------------------------------------------------------------

module _
  (Id : Set)
  (lower   : Staged Id → Skeleton Id)
  (capture : Staged Id → Residue Id)
  (extrude : Skeleton Id → Residue Id → Staged Id)
  (round-trip : (s : Staged Id) → extrude (lower s) (capture s) ≡ s)
  where

  open Promote Id lower capture extrude round-trip

  -- Draining loses nothing: the promote is injective on the fragment.
  promote-injective :
    (s₁ s₂ : Staged Id) → promote s₁ ≡ promote s₂ → s₁ ≡ s₂
  promote-injective =
    drainable (promote-Reflection Id lower capture extrude round-trip)
