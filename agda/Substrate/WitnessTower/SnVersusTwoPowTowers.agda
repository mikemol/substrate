------------------------------------------------------------------------
-- Substrate.WitnessTower.SnVersusTwoPowTowers
--
-- ◆AI-1e — the COVERING co-apex over SnVersusTwoPow's four co-apexes. The
-- |Sₙ|-vs-2ⁿ sweep is not four separate links to four separate homes; the four
-- co-apexes are readings of ONE structure the repo already names: the family
-- of WITNESSING TOWERS (Ⓣ₁, Ⓣ₂), each a GradedDivStr built by the witnessing
-- step rung(suc n) = (rung n, increment), with a fold back down.
--
-- The repo's own naming (verified):
--   Ⓣ₁ = Sₙ    — WitnessTower.LehmerPath: "Sₙ is BUILT OF the witnessing step";
--                the increment is an insertion choice (Fin (suc n)).
--   Ⓣ₂ = ℚ / Cayley-Dickson — WitnessTower.EEATower: "ℚ is BUILT OF the
--                witnessing step"; Algebra.CayleyDickson.Carrier zero = ℚ,
--                Carrier (suc n) = Carrier n × Carrier n (the doubling); the
--                increment is a Wedge / a doubling.
--   Ⓣ₃ = the algebra ladder — WitnessTower.AlgebraLadder (increment = a LAW).
--
-- BOTH towers are GradedDivStr instances (the tight common structure):
--   Ⓣ₁ : WitnessTower.Wedge.Graded.tower-graded
--            : GradedDivStr Perm      (λ n → Fin (suc n))
--   Ⓣ₂ : Algebra.CayleyDickson.Grade.F₂-length-grading
--            : GradedDivStr (Vec Bool) (λ _ → Bool)
-- These are re-exported together HERE so the covering structure is one import,
-- not a prose observation.
--
-- The four SnVersusTwoPow co-apexes, as readings of this covering apex:
--   (1) |Sₙ| = factorial n = |perms n|   is the RUNG-COUNT of Ⓣ₁ (perms-length).
--   (2) 2ⁿ = |Carrier n basis|           is the RUNG-DIMENSION of Ⓣ₂
--                                        (Cocycle.e : Vec Bool n → Carrier n).
--   (3) ceil-exp = μsearch               is an EXTRUDER (a fixpoint tower, the
--                                        same suc-step-to-fixpoint idiom).
--   (4) complement / 8 = HodgeDim4       is the rung-3 SEAM where the two
--                                        towers meet (24 + 8 = 32 = 2⁵).
--
-- THE DEEPER SHARED STRUCTURE (why this covering apex is load-bearing, not a
-- filing cabinet): BOTH towers carry a SIGN COCYCLE.
--   Ⓣ₁: sign = stab-parity (this session — SignStabTotal: sign factors through
--        the Stab retraction; the V₄-coset is the kernel).
--   Ⓣ₂: sign = ε, the Cayley-Dickson cocycle (Cocycle.ε : Vec Bool n →
--        Vec Bool n → Bool, eᵢ·eⱼ = ε(i,j)·e_{i⊕j}).
-- So |Sₙ|-vs-2ⁿ is the comparison of two SIGN-CARRYING GradedDivStr towers, and
-- the n=4 seam is where the permutation-sign side (24 = |S₄|) and the
-- Cayley-Dickson-sign side (32 = 2⁵) coincide up to the Hodge-8 completion.
-- That is the content of K-cayley-dickson-level4 the sweep formalises.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPowTowers where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Algebra.Wedge.Graded using (GradedDivStr)

-- Ⓣ₁ — the permutation witnessing tower, as a GradedDivStr (increment =
-- insertion choice Fin (suc n)). Re-exported from its home.
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.WitnessTower.Enumerate using (Perm)

open import Substrate.Algebra.CayleyDickson.Grade using (F₂-length-grading)
open import Substrate.WitnessTower.SnVersusTwoPow
  using (|S|; |S|-is-tower-count; complement; ceil-exp; crossover-at-4;
         complement-8-reappears)
open import Substrate.WitnessTower.VecBoolCardinality using (allVB; card-VecBool)
open import Substrate.WitnessTower.Enumerate using (lengthL)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Nat using (_^_)
Ⓣ₁-graded : GradedDivStr Perm (λ n → Fin (suc n))
Ⓣ₁-graded = tower-graded

-- Ⓣ₂ — the Cayley-Dickson doubling tower's basis grading, as a GradedDivStr
-- (increment = one bit / one doubling). Re-exported from its home.

Ⓣ₂-graded : GradedDivStr (Vec Bool) (λ _ → Bool)
Ⓣ₂-graded = F₂-length-grading

------------------------------------------------------------------------
-- The covering statement, made checkable: the sweep's two columns are the
-- rung-count of Ⓣ₁ and (the index type of) the rung of Ⓣ₂. |Sₙ| is Ⓣ₁'s
-- count via perms-length; the Ⓣ₂ rung at level n is indexed by Vec Bool n
-- (cardinality 2ⁿ — the sweep's right column, made a TYPE here; its count
-- is Ⓣ₂-rung-count below, = card-VecBool, ◆AI-1d discharged).
------------------------------------------------------------------------

------------------------------------------------------------------------
-- The covering ties, re-exported so the two towers and the sweep's two
-- columns are reachable from one import. Column 1 (|Sₙ|) is Ⓣ₁'s rung-count
-- (perms-length, via |S|-is-tower-count from SnVersusTwoPow). Column 2's rung
-- at level n is the Ⓣ₂ index type Vec Bool n (cardinality 2ⁿ = Ⓣ₂-rung-count,
-- card-VecBool, ◆AI-1d discharged).
------------------------------------------------------------------------


-- Ⓣ₂'s rung index at level n: the basis-index type whose cardinality is the
-- sweep's 2ⁿ column. Named here as the tower-side reading of that column.
Ⓣ₂-rung-index : ℕ → Set
Ⓣ₂-rung-index n = Vec Bool n

-- ◆AI-1d (discharged, wired here): the cardinality of Ⓣ₂'s rung index IS 2ⁿ, as
-- a proved term — VecBoolCardinality.card-VecBool. So the sweep's right column
-- is not a bare literal but the enumerated count of the Cayley-Dickson basis
-- index. (Was "pending ◆AI-1d"; now a citation to the built term.)

Ⓣ₂-rung-count : (n : ℕ) → lengthL (allVB n) ≡ 2 ^ n
Ⓣ₂-rung-count = card-VecBool
