{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.MuRegistryEntry — ⟡mu-registry-entry: add
-- the μ initial-algebra backing (mu-backed, ADD 170) to the UP Registry, using the
-- substrate's own downstream idiom (`verdict-registry = bias-coeq-backed ∷ registry`,
-- Registry's coverage note). The entry COMPILING is the certification: mu-backed is a
-- genuine, non-vacuous universal-property solver — the typechecker is the gate.
--
-- mu-backed was in the Registry's "PROVED-BUT-NOT-YET-REGISTERED (NOT debt)" bucket
-- (the trace-fold initial-algebra UP); this module moves it to REGISTERED. It is
-- concrete over ℕ-div (no parameter), so — unlike the ν (which needs a WedgeCoalg) —
-- it cons's directly onto the list.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.MuRegistryEntry where

open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Category.UniversalProperty.Vacuity using (Vacuous)
open import Substrate.Category.UniversalProperty.Backed using (BackedUP; arrow; backed-non-vacuous)
open import Substrate.Category.UniversalProperty.Registry using (registry)
open import Substrate.Category.UniversalProperty.MuBacked using (mu-backed)

------------------------------------------------------------------------
-- THE EXTENDED REGISTRY: mu-backed consed onto the seed registry. Compiling this
-- List BackedUP IS the registration — mu-backed conforms (existence + non-vacuity
-- forced by typing, backed-non-vacuous holds for any BackedUP so no vacuous entry
-- could appear).
------------------------------------------------------------------------
mu-registry : List BackedUP
mu-registry = mu-backed ∷ registry

-- the new entry is non-vacuous — FORCED by typing (as for every registry member).
mu-entry-non-vacuous : ¬ Vacuous (arrow mu-backed)
mu-entry-non-vacuous = backed-non-vacuous mu-backed

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out): the μ initial-algebra (Trace, the fold half) is now
-- a REGISTERED universal property — mu-backed ∷ registry compiles, so the trace-fold
-- solver is certified genuine + non-vacuous BY TYPING, joining eq/Z3/Z5/CRT on the
-- substrate's conformance checklist. This moves μ from "PROVED-BUT-NOT-YET-REGISTERED"
-- (Registry's own bucket) to REGISTERED, via the substrate's downstream cons idiom
-- (like verdict-registry). The either/or "proved vs registered" dissolves: registration
-- IS the proof re-presented as a compiling list entry — the typechecker is the gate,
-- not a grep. With 169/170, μ and ν are both backed; the ν's Registry entry still awaits
-- a concrete WedgeCoalg ℕ-div (⟡nu-registry-entry), so μ leads its dual onto the list.
------------------------------------------------------------------------
