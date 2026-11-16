------------------------------------------------------------------------
-- Substrate.Axes.Signature
--
-- Defines: Sig
-- ⟡cap-128-forcing: one lemma, one elaboration unit.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Axes.Signature where

open import Substrate.Foundation.Eq
open import Substrate.Foundation.Negation.Not
open import Substrate.Axes.Axis using (Axis)
open import Substrate.Axes.Opposite using (partner)


------------------------------------------------------------------------
-- A DCSW OPERATION SIGNATURE: a directed edge with a witness drawn from
-- the OPPOSITE pair.
--
-- ⚑ THIS IS `validate_signature` (`scratch/meta_protocol.py:74-87`) AS A
-- TYPE RATHER THAN A CHECK. There the constraint is enforced by raising:
--
--     opp, _ = opposite_pair(source, sink)
--     if witness not in opp:
--         raise ValueError(f"witness {witness} must be in the opposite pair …")
--
-- and `WitnessedOp.__post_init__` calls it, so a malformed op raises at
-- construction. Here the same fact is a FIELD: a `Sig` cannot be built
-- without the proof, so an invalid opcode does not typecheck. The Python
-- catches it at runtime; the type catches it at elaboration.
--
-- ⚑ THE WITNESS CONSTRAINT IS THREE NEGATIONS, NOT A SET MEMBERSHIP. The
-- opposite pair is exactly "neither endpoint, nor the endpoint's partner"
-- — so `w ≢ s`, `w ≢ t`, and `w ≢ partner s t` pin it to the one remaining
-- axis on the far side. Stating it this way needs no set type and no
-- decidable membership, which is what keeps this module `--safe` with no
-- imports beyond Eq and Not.
--
-- ⚑ AND THIS IS WHY A QUARTER OF THE SPACE IS UNREACHABLE. Four axes give
-- 4×3 = 12 directed edges and 2 remaining axes each, but only ONE of those
-- two is opposite — the other is the endpoint's own partner. So the naive
-- 4×3×2 = 24 and the constrained 24 coincide only because the constraint
-- picks exactly one of two: `D→C witnessed by S` and `D→C witnessed by W`
-- are BOTH legal (S and W are the α-opposite pair), while `D→S witnessed
-- by C` is legal and `D→S witnessed by W` is legal — but the pairing
-- differs. The unreachable quarter is the diagonal `w = partner s t`.
--
-- ⚑ THIS RECORD IS A FLAT SNAPSHOT, AND `w-opposite` IS THE DIAGONALIZATION
-- RATHER THAN A FOURTH NEGATION (user, 2026-08-07: *"that's the
-- diagonalization, and is already in-hand as the tower grows"*). Choosing an
-- EDGE out of four cells forces the complementary pair — 4 = 2 + 2, so there
-- is no second choice — and the matching is therefore PRODUCED by the ascent,
-- not consulted from below. `Axes.EdgePairing.edge-v₄` is that production, and
-- `Axes.PartnerIsEdgeV4` proves `partner s t ≡ act-axis (edge-v₄ s t) s` by
-- `refl`: the axis-level answer IS the group-level answer applied.
--
-- ⚑ AND THE MATCHING IS ALREADY A NAMED, PROVED DATUM ELSEWHERE.
-- `Cocycles.V4Signature.Pairing.Type` declares α-pair/β-pair/γ-pair with the
-- same partitions as `scratch/meta_protocol.py:29`, independently written;
-- `Pairing.Structural.Pairing↔V4-Nonzero` proves the bijection to V₄∖{e},
-- both round-trips. So `w-opposite` is a computed block membership, not an
-- obligation each construction site must discharge.
--
-- ⚑ `WitnessTower.Puncture` IS THE FIBRE MAP, NOT THE DERIVATION — and those
-- are different jobs (user, 2026-08-07). Its partition
-- `Fin (suc (suc k)) = {w} ⊎ punchIn w (Fin (suc k))` traces a cell's identity
-- ACROSS the ascent: `punchIn w` embeds rung-k cells into rung-(k+1) skipping
-- the witness, `punchOut` recovers them, so you can follow a point up the
-- tower. That is genuinely useful and genuinely used.
--
-- What it does NOT do is fix WHICH of the two remaining candidates the witness
-- must be. A research pass recommended instantiating it at k=1 to discharge the
-- negations, and I first recorded the reverse overcorrection — that Puncture was
-- mere reader-facing scaffolding. Both were wrong. It supplies `w ∉ {source,
-- sink}` and the fibre tracing; the block membership comes from V₄.
--
-- Kept as a record until the construction replaces it, so the type exists and
-- is honest about being provisional. It has ZERO importers today.
------------------------------------------------------------------------

record Sig : Set where
  constructor sig
  field
    source    : Axis
    sink      : Axis
    witness   : Axis
    distinct  : ¬ (source ≡ sink)
    w≢source  : ¬ (witness ≡ source)
    w≢sink    : ¬ (witness ≡ sink)
    -- the witness lies in the pair OPPOSITE {source, sink}: it is not the
    -- axis paired with `source` under the matching that pairs source↔sink.
    w-opposite : ¬ (witness ≡ partner source sink)
