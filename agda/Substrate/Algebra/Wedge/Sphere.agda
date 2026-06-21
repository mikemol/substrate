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
--    engine is PROVE-OR-CORRECT, never dead-ends. · ✅ PROVED in `Wedge.Adjunction`:
--    the hom-iso Wedge≅Term + triangle-as-witness (a = recon q b r), and the
--    `FreeForgetful` module makes keep/forget the Free⊣Forgetful SPLIT IDEMPOTENT
--    (`split-Canonical`, the apex), the residue = the adjoint comparison (z = the
--    iso corner), `divide` total ⟹ no dead-end. Non-vacuous at ℕ div-mod.
-- 2. graded-GF(2) is NON-CANCELLING — with the F₂ⁿ-graded topology distinct
--    derivations don't XOR-cancel (cancellation is ungraded-projection-only;
--    "GF(2) cancels derivations" was the ungraded mistake). · ✅ PROVED in
--    `CayleyDickson.Grade.popcount-or-and`: popcount(i∨j)+popcount(i∧j) =
--    popcount i+popcount j, so the cancellation defect is EXACTLY the overlap
--    popcount(i∧j) — zero iff disjoint supports. The full F₂ⁿ index retains the
--    overlap (∨-anf: OR=XOR⊕AND); only the popcount (ungraded) projection loses it.
-- 3. Morton ≅ Cayley-Dickson via the COCYCLE — Morton(untwisted)/Hilbert(twisted)
--    = trivial/nontrivial 2-cocycle on F₂ⁿ = CD level; ladder graded loss
--    (ℂ comm→ℍ noncomm→𝕆 nonassoc) = the commute-edge grade. · LADDER COMPLETE,
--    every rung machine-checked in `CayleyDickson.CommuteEdge` + `.CayleyDickson`:
--    ℂ commutes (`mul-comm-ℂ`) → ℍ does NOT (`mul-noncomm-ℍ`, i·j=k≠−k=j·i) → 𝕆
--    NOT assoc (`mul-nonassoc-𝕆`, (ij)l≠i(jl)) → 𝕊 zero divisors (`zd-value-0`).
--    ✅ PROVED in `CayleyDickson.Cocycle`: the GENERIC PRODUCT LAW `prod` —
--    eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j} for ALL n (the F₂ⁿ index→basis map `e`, the index
--    XOR `zipWith _xor_`, and the explicit recursive 2-cochain `ε`). The basis
--    product lands on the XOR'd index (the Morton/Z-order grading) carrying the
--    sign-cocycle ε. Morton = the TRIVIAL cochain (ε ≡ false, pure XOR); CD = this
--    NONTRIVIAL ε, noncommutativity = `mul-noncomm-ℍ`, strict-2-cocycle failure =
--    the 𝕆 associator (`mul-nonassoc-𝕆`). The CD doubling generator is
--    Algebra.CayleyDickson (same step as the nedge Evidence carrier-doubling).
-- 4. the TWO GRADINGS coincide(or not) — ANF degree (OR=XOR⊕AND) vs F₂ⁿ-index
--    (Morton/CD). · ✅ PROVED in `CayleyDickson.Grade`: they DON'T coincide, they
--    are BRIDGED. The F₂ⁿ index is `Wedge.VecGraded.vec-graded Bool` (grade =
--    LENGTH = the ambient F₂ⁿ dimension); `popcount` is the orthogonal ANF-DEGREE
--    grading (Hamming weight) on the same carrier. The two index-PRODUCTS (CD/Morton
--    XOR vs ANF/Reed-Muller OR-union) are bridged at the index by `∨-anf`
--    (OR=XOR⊕AND) and at the degree by `popcount-or-and` (inclusion-exclusion).
-- 5. nilpotent-not-annihilating ⟹ NO DEAD-END — residues nilpotent (graded
--    correction), never annihilating; "kill" can't happen (intuitionistic;
--    deformation tracked). ties #1. · partly built (CrossMul coherence =
--    cross-term nilpotency degree).
-- 6. the semiring VM PLACES ITSELF via the gauge — one tensor over a chosen
--    semiring = the job gauge (Bool route / GF(2) compute / ℕ count / tropical
--    cost). · ✅ PROVED — Semiring.Contraction.contract (the tensor ⊕ᵢ aᵢ⊗bᵢ,
--    Semiring a REAL parameter) reads ALL FOUR gauges by refl: ℕ→11, Bool→true,
--    tropical→fin 4, F₂→𝟘. (Stale: the 4 gauges ARE in Semiring.Instances —
--    incl. ℕ∞ tropical — and Semiring.SPPF.inside is a prior consumer; the
--    "never instantiated / tropical not built" reading was outdated.)
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
import Substrate.Algebra.CayleyDickson.Cocycle as Cocycle
import Substrate.Algebra.CayleyDickson.Grade as Grade

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
cell-cocycle   = Cocycle.prod                -- C3: eᵢ·eⱼ ≈# ε(i,j)·e_{i⊕j} ∀n
cell-grade     = Grade.∨-anf                 -- C4/C2: OR=XOR⊕AND (two index-products)
cell-incl-excl = Grade.popcount-or-and       -- C2: degree defect = the AND overlap
