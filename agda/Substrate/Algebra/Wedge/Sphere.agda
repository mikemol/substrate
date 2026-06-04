------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Sphere
--
-- THE COMMUTING SPHERE — the in-code index of the wedge/shape arc, carrying
-- the conjecture ledger NEXT TO the proofs so the conjectures cannot be lost.
-- Full prose: scratch/commuting_sphere.md. Durable ledger:
-- memory project_commuting_sphere.md. Proven arc: project_wedge_pentagon_sphere.
--
-- This module PROVES nothing new. It (a) name-references the proven cells
-- below — so if any is renamed or removed, this index fails to typecheck
-- (a live index, not stale prose) — and (b) records, as clearly-marked
-- CONJECTURES, the open cells that motivate the next phase. The conjectures
-- are PROSE, not Agda claims (comments-don't-overclaim); this module imports
-- only proven cells and carries zero postulates.
--
-- ====================================================================
-- CONJECTURE LEDGER  (NOT PROVEN — the part that must not be lost)
-- Each: statement · status · prove-or-correct path · home.
--
-- 1. KEYSTONE — r<b-residue = the precise Free⊣Forgetful ADJOINT correction;
--    a refutation (r≠0) hands back exactly what to adjoin ⟹ the metaphor→proof
--    engine is PROVE-OR-CORRECT, never dead-ends. · conjecture · `a = recon q b r`
--    is the adjunction triangle; show the certified (sharp) residue = the
--    adjoint comparison. · home: Wedge + Category.FreeUniversalProperty. FIRST.
-- 2. graded-GF(2) is NON-CANCELLING — with the F₂ⁿ-graded topology distinct
--    derivations don't XOR-cancel (cancellation is ungraded-projection-only;
--    "GF(2) cancels derivations" was the ungraded mistake). · conjecture ·
--    home: new graded-GF(2) carrier; relates Category.GradedMonoid.
-- 3. Morton ≅ Cayley-Dickson via the COCYCLE — Morton(untwisted)/Hilbert(twisted)
--    = trivial/nontrivial 2-cocycle on F₂ⁿ = CD level; ladder graded loss
--    (ℂ comm→ℍ noncomm→𝕆 nonassoc) = the commute-edge grade. · conjecture ·
--    home: Cayley-Dickson NOT in substrate (build); Substrate.Cocycle partial.
-- 4. the TWO GRADINGS coincide(or not) — ANF degree (OR=XOR⊕AND) vs F₂ⁿ-index
--    (Morton/CD). · conjecture · home: new.
-- 5. nilpotent-not-annihilating ⟹ NO DEAD-END — residues nilpotent (graded
--    correction), never annihilating; "kill" can't happen (intuitionistic;
--    deformation tracked). ties #1. · partly built (CrossMul coherence =
--    cross-term nilpotency degree).
-- 6. the semiring VM PLACES ITSELF via TROPICAL — one tensor over a chosen
--    semiring = the job gauge (Bool route / GF(2) compute / ℕ count / tropical
--    cost); same double category over (min,+) = VERIFIED fabric placement;
--    square = legal-fusion. · conjecture · home: Algebra.Semiring EXISTS BUT
--    NEVER INSTANTIATED (the consumer that measures it); tropical NOT built.
-- 7. wedge = CONSTRUCTIVE BOUNDARY OPERATOR — partial COMMUTativity = structural
--    partition (commutes/doesn't) in one domain; wedge traces its edge (sharp
--    r<b, graded by nilpotency, recursive via orbit; shape = edge-record). ·
--    wedge/trace/shape built; "edge=grade=cocycle" is the conjecture.
-- 8. Curry-Howard VM — bivalent SPPF (3 DOF: composition/grouping/growth) =
--    proof = program = trace = layout; Morton=tree-walk-while-commutes,
--    Hilbert=ordered packing, crossover AT the grade boundary chosen by the
--    tropical/cost instance (recursive fixpoint). · framing.
--
-- NEXT BUILD (gated on this ledger): prove #1, then make Semiring a real
-- parameter of the wedge/tensor engine (#6 — unifies Bool/GF(2)/tropical).
-- ====================================================================
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Sphere where

import Substrate.Algebra.Wedge as W
import Substrate.Algebra.Wedge.Shape as Shape
import Substrate.Algebra.Wedge.Shape.Double as Double
import Substrate.Algebra.Wedge.Shape.Twist as Twist
import Substrate.Algebra.Wedge.Shape.Register as Reg
import Substrate.Algebra.Wedge.Shape.Register.FromTrace as FromTrace
import Substrate.Algebra.Wedge.Monoidal as Mon
import Substrate.Algebra.Wedge.Registry as Registry
import Substrate.Algebra.F2.Linear.BilinearFromImages as Bilin

------------------------------------------------------------------------
-- Live references to the proven cells. Renaming/removing any breaks this
-- index — the sphere stays honest about what is actually proven.
------------------------------------------------------------------------

cell-wedge     = W.DivStr                    -- the wedge core
cell-shape     = Shape.shape                 -- carrier-free spine
cell-square    = Double.square               -- the double-category 2-cell
cell-twist     = Twist.twist                 -- companion/conjoint = trace/Bézout
cell-sound     = Reg.idx-inj                 -- interned heap: address ⟹ value
cell-intern    = FromTrace.intern-trace      -- suffix-shared SPPF via the trace
cell-hexagon   = Mon.hexagon                 -- symmetric-monoidal coherence
cell-roots     = Registry.objects            -- the founded roots
cell-gf2       = Bilin.bilinear-from-images  -- the GF(2) carrier (free bilinear)
