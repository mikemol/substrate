------------------------------------------------------------------------
-- Substrate.Category.Allegory.Policy.BasisShift
--
-- Defines: Transfers
--
-- THE POLICIES ARE STATED OVER AGDA SITES.  What do they say about the
-- PYTHON corpus?  Not "instantiate them at python sites" — the policy
-- terms are parameterized over Site/Name/Shape, so ANY type fits and
-- instantiation would prove nothing.  The question is whether each policy
-- COMMUTES with the translation, and the content is where it does not.
--
-- ⚑ A BASIS SHIFT IS A LAX SQUARE, NOT A RE-INSTANTIATION.  With τ the
-- translation relating an agda site to its python counterpart, a policy P
-- TRANSFERS when
--     τ ⨾ P-py  ⊆  P-agda ⨾ τ
-- — every python-side policy step, seen through τ, is matched by an
-- agda-side step.  `_⊆_` and not `_≈_` is the whole point: the square is
-- LAX, so a policy can transfer in one direction while the converse fails,
-- and THAT asymmetry is the measurement.  This is why the model had to be
-- an allegory rather than a topos: a functor between categories would
-- demand equality of composites, and there is none to be had here.
--
-- ⚑ MEASURED, NOT ASSUMED (2026-08-21, over 634 python files).  The three
-- constructs that BREAK the square are not the ones the agda policies BAN.
-- The banned ones are all present-but-repairable — `import X as Y` (56
-- sites for `store` alone, under SIX aliases: _store/_s/_cstore/_stb/
-- _st6/_sm), cross-module `_private` (`jea_pysim.py:33` importing
-- `_HAS_CST`).  Those are ordinary name-identity defects with the same
-- rename-at-source repair agda uses.  `__all__` (python's `public`) and
-- `from X import *` are at ZERO sites, so two of the five bans are
-- vacuous here.
--
-- What breaks the square is what agda CANNOT EXPRESS, and therefore never
-- had to ban:
--
--   getattr, 113 sites   — a runtime-constructed name.  P1-P5 presupposes
--                          a name a consumer WRITES and a definition
--                          CARRIES.  `getattr(o, s)` writes none, so the
--                          policy has no subject — not a hard check, an
--                          ABSENT one.  (jea_pyalg.py:331-501,
--                          query_registry.py:104-433, sql_lift.py:131-665)
--   module-scope mutation, 39 process-local caches in 23 files — a
--                          definition set that does not exist until the
--                          module RUNS (`query_registry.py:82` BUILDERS,
--                          mutated by `update` at import time).
--   function-scoped conditional imports, pervasive — normal python idiom
--                          for breaking cycles; in agda an import below a
--                          use is a DEFECT (`agda_defs --late-imports`).
--
-- ⚑⚑ SO THE RESIDUE IS NOT `state ∖ budget`.  Owed measures offenders
-- against a budget WITHIN a state space.  These three put the set of
-- definitions-in-scope OUTSIDE that space: it becomes a runtime quantity
-- rather than a syntactic one.  A ratchet cannot measure them, and saying
-- so is different from saying they comply.
--
-- ⟡policy-basis-shift: one lemma, one elaboration unit; no barrel
-- re-exports these siblings.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Allegory.Policy.BasisShift where

open import Substrate.Category.Allegory
open import Substrate.Category.Allegory.Policy.Corpus


-- τ relates an agda site to the python site it translates to.  A policy
-- transfers across τ when the lax square commutes: doing the python step
-- and translating is contained in translating and doing the agda step.
--
-- ⚑ THE CONTAINMENT DIRECTION IS THE CLAIM.  `⊆` says python-side
-- compliance is NO WEAKER than agda-side compliance seen through τ.  The
-- reverse containment would say the corpora impose the same discipline,
-- which is exactly what the getattr/mutation/late-import residue refutes.
Transfers : {ASite PSite : Set} → Corpus ASite → Corpus PSite
          → (τ : ASite → PSite → Set)
          → (P-agda : ASite → ASite → Set) (P-py : PSite → PSite → Set)
          → Set
Transfers _ _ τ P-agda P-py = (τ ⨾ P-py) ⊆ (P-agda ⨾ τ)
