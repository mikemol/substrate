------------------------------------------------------------------------
-- Substrate.Lifecycle.Fragment.IRInstance
--
-- Defines: Promote
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Fragment.IRInstance where

open import Substrate.Algebra.Quotient.IRRetraction
open import Substrate.Foundation.Eq
open import Substrate.Lifecycle.Fragment
open import Substrate.Lifecycle.Fragment.Occurrence
open import Substrate.Lifecycle.Fragment.Skeleton
open import Substrate.WitnessTower.GradeMapInvariant


------------------------------------------------------------------------
-- THE PROMOTE AS AN IR-RETRACTION — the instantiation, not a new theory.
--
-- ⚑⚑⚑ THIS MODULE EXISTS TO *APPLY* AN EXISTING GENERATOR, AND FINDING IT
-- WAS THE REAL WORK. `Substrate.Algebra.Quotient.IRRetraction.IR` was built
-- for the jea IR→source extruder — a different arc, a different corpus, its
-- round-trip validated on 133/133 real modules — and it is parameterized over
-- exactly the three carriers and three maps this problem has:
--
--     lower   : Source → Skeleton      the interning (the SHARED quotient)
--     capture : Source → Residue       the per-occurrence cofactor
--     extrude : Skeleton → Residue → Source
--     round-trip : extrude (lower s) (capture s) ≡ s
--
-- Its `Repr = Skeleton × Residue`, its `decompose`/`recon`, and its
-- `ir-Canonical = split-Canonical recon decompose recon-decompose` are all
-- already proved. Nothing here re-derives them.
--
-- ⚑ AND THE APEX GATE CONFIRMS THIS IS THE RIGHT SHAPE RATHER THAN MERELY A
-- CONVENIENT ONE. `law_motif_apex --check` reports its recognised motifs as
-- `[idempotent, involution, retraction/section]` — so retraction/section is
-- an EXISTING law-motif with an existing parametric apex, and these instances
-- join it instead of founding a new cluster that would block until an apex
-- was built. The gate wanted a parametric apex; `IR` is that apex.
--
-- ⚑⚑ `project` IS NOT A FUNCTION OF THE STAGED INPUT ALONE, AND THIS
-- SIGNATURE SAYS SO. The store's fold depends on allocator state: node ids
-- are minted per run, so a second promote over a DIFFERENT set of live cores
-- restarts the numbering and a signature can receive an id that already
-- denotes something else — *"silent corruption, not a conflict"*. Threading
-- the maps as PARAMETERS (rather than defining them here) is what keeps that
-- dependence visible: an instantiation must supply a specific allocator's
-- behaviour, and two allocators give two instances, as they should.
--
-- ⚑ THE ROUND-TRIP IS THE HYPOTHESIS, NOT THE CONCLUSION — the honest
-- conditional, and the same stance `IRRetraction` itself takes (*"here it
-- enters as the section/retraction HYPOTHESIS … given it, this module DERIVES
-- the Canonical"*). In the store it is checked empirically, per core, by
-- rebuilding and comparing before any delete: *"Nothing is deleted on the
-- strength of an argument."* What this module buys is that the obligation is
-- now NAMED and TYPED, so `drainable` can consume it.
--
-- ⚑⚑ THE `open` IS NOT `public`, AND THE GATE IS WHY — CAUGHT, NOT
-- ANTICIPATED. The first draft of this module wrote `open IR … public` and
-- `check_public_ratchet` refused it as NEW key #34, naming this exact file.
-- A wholesale re-export COPIES the whole upstream API into this core and
-- transitively into every consumer's — the mechanism the cap ratchet exists
-- to bound, so the two gates are one policy seen from two ends. The
-- prescribed paydown is to bind at the OWNER, which is what the explicit
-- definitions below do: each names one thing this module genuinely provides.
------------------------------------------------------------------------

module Promote
  (Id : Set)
  (lower   : Staged Id → Skeleton Id)
  (capture : Staged Id → Residue Id)
  (extrude : Skeleton Id → Residue Id → Staged Id)
  (round-trip : (s : Staged Id) → extrude (lower s) (capture s) ≡ s)
  where

  open IR (Staged Id) (Skeleton Id) (Residue Id) lower capture extrude round-trip

  -- The durable representation: skeleton (shared) × residue (per-occurrence).
  Durable : Set
  Durable = Repr

  -- `project` — the promote, as one map.
  promote : Staged Id → Durable
  promote = decompose

  -- `reconstruct` — the rebuild, from BOTH factors.
  rebuild : Durable → Staged Id
  rebuild = recon

  -- The retraction, definitionally the supplied round-trip.
  rebuild-promote : (s : Staged Id) → rebuild (promote s) ≡ s
  rebuild-promote = recon-decompose
