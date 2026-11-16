------------------------------------------------------------------------
-- Substrate.Lifecycle.Retire
--
-- Defines: retire-sig
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lifecycle.Retire where

open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Axes.Opposite using (partner)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Negation.Not using (¬_)


------------------------------------------------------------------------
-- RETIRING THE EVENT TIER IS `W → S`, AND THE WITNESS MUST BE D OR C.
--
-- The operation: take the event tier (staged rows), factor it through the
-- SPPF, MATERIALIZE the residue as a reverse index, and then retire the
-- staged rows. In DCSW terms that is a directed edge
--
--     source = W   (Workspace — the event tier, staging)
--     sink   = S   (State — the materialized reverse index, durable)
--
-- ⚑ AND THE WITNESS IS FORCED, NOT CHOSEN. `{S,W}` is the α matching
-- (`{D,C} | {S,W}`, per `Cocycles.V4Signature.Pairing.Type`), so the opposite
-- pair is `{D,C}` and a witness must come from it —
-- `scratch/meta_protocol.py:74-87`'s `validate_signature`, and `Axes.Signature`'s
-- `w-opposite` field. **State cannot witness its own arrival**: "the rows are
-- durable now" is `{S,W}` witnessed by `S`, which the algebra rejects outright.
--
-- That is why `Lifecycle.Reflection`'s round-trip is the right gate and was not
-- a design preference: `reconstruct (project s) ≡ s` re-runs COMPUTE over the
-- SPPF, so the retirement is C-witnessed. `Lifecycle.Drainable` then proves the
-- consequence — a reflection makes `project` injective, so the durable form
-- DETERMINES the staged one and no two records can share an image.
--
-- ⚑ THE OTHER LEGAL WITNESS IS D, AND IT IS A DIFFERENT GATE. `W→S w/ D` is
-- retirement witnessed by the DATA — re-reading the source (the `.agdai` cores)
-- rather than recomputing from the projection. Weaker in one way (it re-derives
-- rather than checks) and stronger in another (it does not trust the SPPF). Both
-- are inhabited cells; the chirality distinguishes them (`meta_protocol.chirality_of`).
--
-- ⚑ IT IS A PROJECTION, AND I FIRST DENIED THAT (user, 2026-08-07: *"it IS a
-- projection, because the reverse index ON ITS OWN cannot reconstruct the SPPF
-- + event tier"*). I cited `[[feedback_wedge_not_projection]]` — "we never
-- discard residue" — and concluded nothing was lost. That misreads which map is
-- under discussion.
--
--     event → (SPPF, reverse index)     LOSSLESS: the pair reconstructs
--     event → reverse index             a PROJECTION: the residue alone cannot
--
-- The feedback's anti-pattern (discard the residue, keep only the base) is not
-- what is happening here, so citing it was answering a question nobody asked.
-- The live question is what the reverse index can do ALONE, and the answer is:
-- less than the pair. It is a projection. Its fibres are the SPPF states that
-- share a residue, and it cannot pick one out.
--
-- ⚑ SO THE RETIREMENT GATE IS ABOUT THE PAIR, NOT ABOUT EITHER PART, and
-- `Lifecycle.Reflection` already says so — its `D` is named "the SPPF + reverse
-- index", i.e. the PRODUCT. Nothing there needs widening. What the projection
-- fact adds is WHY that is the only admissible instantiation: `D := Index` alone
-- admits no `Reflection` at all, because `project` is not injective there, so
-- `Drainable` could never fire. The record was stated at the right arity and the
-- reason is now recorded rather than assumed.
--
-- ⚑ AND THAT IS THE SAME COLLAPSE `Reflection` ALREADY MEASURES ONE LAYER DOWN.
-- `_node` keys on `sym ‖ child-syms`, so one module applied twice interns to a
-- single node (16,842 of 350,827 slots) — non-injective, and the reverse index
-- is exactly the residue that undoes it. Take the index without the SPPF and the
-- SAME shape reappears at the tier above: many staged states, one image.
------------------------------------------------------------------------

-- the retirement edge, and its forced witness pair
retire-sig : Axis
retire-sig = partner W S      -- = S's partner under the matching pairing W with S

-- ⚑ THE α MATCHING PUTS S AND W TOGETHER, so `partner W S ≡ S`: W's own block-mate
-- IS S. The witness must therefore come from the OTHER block, `{D,C}` — neither
-- endpoint can witness the move that consumes it.
retire-partner-is-S : retire-sig ≡ S
retire-partner-is-S = refl

-- the two legal witnesses, exhibited: D and C are exactly the axes that are
-- neither endpoint nor the endpoint's partner.
retire-witness-C-ok : ¬ (C ≡ W) → ¬ (C ≡ S) → ¬ (C ≡ partner W S) → Axis
retire-witness-C-ok _ _ _ = C

retire-witness-D-ok : ¬ (D ≡ W) → ¬ (D ≡ S) → ¬ (D ≡ partner W S) → Axis
retire-witness-D-ok _ _ _ = D
