------------------------------------------------------------------------
-- Substrate.WitnessTower.SnVersusTwoPow
--
-- ◆AI-1 — the FIRST Agda counterpart to a pure-Python N-sweep claim
-- (s4_structure.py:sn_cayley_dickson_table, catalog claim
-- K-cayley-dickson-level4). The Python explored |Sₙ| vs 2ⁿ across n and
-- found a "disappear/reappear at later N" phenomenon that no Agda file
-- captured. This file captures it.
--
-- |Sₙ| = factorial n (WitnessTower.Enumerate: |perms n| ≡ factorial n, the
-- tower's own count). The sweep, and its common structure:
--
--   n:            0   1   2   3   4    5
--   |Sₙ|:         1   1   2   6   24   120
--   2ⁿ:           1   2   4   8   16   32
--   fits 2ⁿ?      y   y   y   y   NO   NO      ← CROSSOVER at n=4
--   ceil-exp k:   0   0   1   3   5    7       ← smallest k with 2ᵏ ≥ |Sₙ|
--   2ᵏ ∸ |Sₙ|:    0   0   0   2   8    8       ← COMPLEMENT: 8 at n=4 AND n=5
--
-- TWO facts, stated honestly (not conflated, per the audit):
--
--   (A) THE CROSSOVER (a monotone break): |Sₙ| ≤ 2ⁿ for n ≤ 3, but |S₄| > 2⁴.
--       The symmetric group first outgrows the n-cube at n = 4. So a
--       structure that embeds Sₙ ⊂ 2ⁿ "disappears" at n = 4 — it cannot,
--       there is no room.
--
--   (B) THE COMPLEMENT-8 REAPPEARANCE (the invariant under the crossover):
--       the gap to the CEILING power of 2 is 8 at BOTH n = 4 (32 ∸ 24) and
--       n = 5 (128 ∸ 120) — but at DIFFERENT ceiling exponents (5 and 7).
--       The dim-4 Hodge closure "24 + 8 = 32 = 2⁵" is the n = 4 instance; the
--       n = 5 complement-8 (120 + 8 = 128 = 2⁷) is arithmetically the same
--       gap at a different exponent, NOT the same Hodge-dim-4 construction.
--
-- The common structure the disappear/reappear instantiates: the gap
-- `2^(ceil-exp n) ∸ factorial n` — the ceiling-complement. The "reappearance"
-- is that this gap takes value 8 at two consecutive n; the "different
-- character" is that the ceiling exponent is not n and jumps (5 → 7). This
-- file records the ceiling exponents as data and proves the complement values,
-- so the phenomenon is a checked fact, not a Python-only observation.
--
-- --safe --without-K. Verified on Agda 2.8.0.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SnVersusTwoPow where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _^_; _∸_; _+_)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (factorial)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (_<ᵇ_)

------------------------------------------------------------------------
-- 0. |Sₙ| is the tower's own count: factorial n = |perms n|. (Named here so
--    the sweep reads as "|Sₙ| vs 2ⁿ", tying to WitnessTower.Enumerate's
--    perms-length : |perms n| ≡ factorial n.)
------------------------------------------------------------------------

|S| : ℕ → ℕ
|S| n = factorial n

------------------------------------------------------------------------
-- 1. THE TABLE (values, checked). |Sₙ| and 2ⁿ for n = 0..5.
------------------------------------------------------------------------

|S|-0 : |S| 0 ≡ 1     ; |S|-0 = refl
|S|-1 : |S| 1 ≡ 1     ; |S|-1 = refl
|S|-2 : |S| 2 ≡ 2     ; |S|-2 = refl
|S|-3 : |S| 3 ≡ 6     ; |S|-3 = refl
|S|-4 : |S| 4 ≡ 24    ; |S|-4 = refl
|S|-5 : |S| 5 ≡ 120   ; |S|-5 = refl

2^4≡16 : 2 ^ 4 ≡ 16   ; 2^4≡16 = refl
2^5≡32 : 2 ^ 5 ≡ 32   ; 2^5≡32 = refl
2^7≡128 : 2 ^ 7 ≡ 128 ; 2^7≡128 = refl

------------------------------------------------------------------------
-- 2. (A) THE CROSSOVER. |Sₙ| fits inside 2ⁿ for n ≤ 3 and NOT for n = 4.
--        Stated with the boolean strict-less (computes by refl).
--        fits n = (|Sₙ| <ᵇ 2ⁿ)  — strictly-less is the honest "room" test
--        (|S₃| = 6 < 8 = 2³ has room; |S₄| = 24 has none, 2⁴ = 16 < 24).
------------------------------------------------------------------------

fits : ℕ → Bool
fits n = |S| n <ᵇ (2 ^ n)

fits-1 : fits 1 ≡ true   ; fits-1 = refl   -- 1 < 2
fits-2 : fits 2 ≡ true   ; fits-2 = refl   -- 2 < 4
fits-3 : fits 3 ≡ true   ; fits-3 = refl   -- 6 < 8
fits-4 : fits 4 ≡ false  ; fits-4 = refl   -- 24 ≮ 16 : the crossover

-- The crossover as the positive fact: at n = 4, 2⁴ is strictly BELOW |S₄|.
-- The symmetric group has outgrown the n-cube.
crossover-at-4 : (2 ^ 4) <ᵇ |S| 4 ≡ true
crossover-at-4 = refl

------------------------------------------------------------------------
-- 3. THE CEILING EXPONENT, as an EXTRUSION (not a data table). Per the
--    substrate's extruder idiom (Algebra.R.Trace.ExtruderFix: "an extruder is
--    the minimal M satisfying control C = MINIMISATION = the μ-operator = a
--    FIXED POINT; search = recursion; the search terminates at the least fixed
--    point"), "smallest k with 2ᵏ ≥ |Sₙ|" is EXTRUDED by a μ-search step, not
--    exhibited as a hardcoded family or a Σ-witness that names the answer. The
--    step k ↦ (2ᵏ ≥ |Sₙ| ? stop k : search (suc k)) has the ceiling exponent
--    as its least fixed point; the table values 0,0,1,3,5,7 come OUT of the
--    search by refl. (Bounded by fuel to stay --safe; 2ᵏ outgrows any m, so
--    fuel |Sₙ|+1 always suffices to reach the fixpoint.)
------------------------------------------------------------------------

-- the μ / extrusion step: from candidate k, if 2ᵏ still below m, search suc k;
-- else 2ᵏ ≥ m and k is the least dominating exponent (μ terminates — the fixpoint).
μsearch : (fuel m k : ℕ) → ℕ
μsearch zero    m k = k
μsearch (suc f) m k with (2 ^ k) <ᵇ m
... | true  = μsearch f m (suc k)     -- 2ᵏ < m: not yet dominating, extrude further
... | false = k                        -- 2ᵏ ≥ m: least fixed point reached

-- ceil-exp EXTRUDED: minimise from k = 0. The value is the search's fixpoint,
-- not a datum. (Same name as before so §4 downstream is unchanged.)
ceil-exp : ℕ → ℕ
ceil-exp n = μsearch (suc (|S| n)) (|S| n) 0

-- the extruded values (these are search OUTPUTS, checked, not asserted data):
ceil-exp-0 : ceil-exp 0 ≡ 0 ; ceil-exp-0 = refl
ceil-exp-2 : ceil-exp 2 ≡ 1 ; ceil-exp-2 = refl
ceil-exp-3 : ceil-exp 3 ≡ 3 ; ceil-exp-3 = refl
ceil-exp-4 : ceil-exp 4 ≡ 5 ; ceil-exp-4 = refl
ceil-exp-5 : ceil-exp 5 ≡ 7 ; ceil-exp-5 = refl

-- lower pin at n = 4, 5 (the interesting rungs): 2^(k-1) is strictly below |Sₙ|.
ceil-pin-4 : (2 ^ 4) <ᵇ |S| 4 ≡ true   ; ceil-pin-4 = refl   -- 16 < 24, k=5 so k-1=4
ceil-pin-5 : (2 ^ 6) <ᵇ |S| 5 ≡ true   ; ceil-pin-5 = refl   -- 64 < 120, k=7 so k-1=6

------------------------------------------------------------------------
-- 4. (B) THE COMPLEMENT and its REAPPEARANCE. complement n = 2^(ceil-exp n)
--        ∸ |Sₙ|, the gap to the ceiling power of 2. Values 0,0,0,2,8,8.
------------------------------------------------------------------------

complement : ℕ → ℕ
complement n = (2 ^ ceil-exp n) ∸ |S| n

complement-0 : complement 0 ≡ 0 ; complement-0 = refl
complement-1 : complement 1 ≡ 0 ; complement-1 = refl
complement-2 : complement 2 ≡ 0 ; complement-2 = refl
complement-3 : complement 3 ≡ 2 ; complement-3 = refl
complement-4 : complement 4 ≡ 8 ; complement-4 = refl   -- 32 ∸ 24  (the dim-4 Hodge 8)
complement-5 : complement 5 ≡ 8 ; complement-5 = refl   -- 128 ∸ 120 (8 again, exponent 7)

-- THE REAPPEARANCE, as one equation: the complement is 8 at n = 4 and n = 5.
complement-8-reappears : complement 4 ≡ complement 5
complement-8-reappears = refl

-- ...but at DIFFERENT ceiling exponents (5 vs 7): the reappearance is
-- arithmetic, NOT the same construction. This inequality of exponents is the
-- "different character" the audit insisted on — the n=4 Hodge-dim-4 closure
-- does not itself recur; only the gap value does.
ceil-exp-differs : (ceil-exp 4 <ᵇ ceil-exp 5) ≡ true
ceil-exp-differs = refl   -- 5 < 7

------------------------------------------------------------------------
-- CO-APEX 1 (tight): |Sₙ| IS the tower's own count. WitnessTower.Enumerate
-- proves perms-length : lengthL (perms n) ≡ factorial n — the enumeration of
-- Sₙ by the witnessing-insertion step has length n!. So "|S| n" here is not a
-- free-standing factorial; it is literally |perms n|, the tower count. This
-- re-export makes the sweep's left column a fact ABOUT the tower.
------------------------------------------------------------------------

open import Substrate.WitnessTower.Enumerate using (perms; perms-length; lengthL)

-- |Sₙ| = |perms n|: the sweep's left column is the tower's enumeration length.
|S|-is-tower-count : (n : ℕ) → lengthL (perms n) ≡ |S| n
|S|-is-tower-count = perms-length

------------------------------------------------------------------------
-- CO-APEX 2 (loose — honestly scoped). The n = 4 row (|S₄| = 24, complement
-- = 8, ceiling 2⁵ = 32) is the ARITHMETIC SHADOW of the codeword
-- decomposition: Cocycles.V4Signature.Codeword.Subtypes defines
--   Reserved = Σ Codeword IsReserved            (comment: 8)
--   Live     = Σ Codeword (¬ IsReserved)         (comment: 24)
-- over the RM(1,4) code (WitnessTower.Codeword: dimension 5, 2⁵ = 32
-- codewords). So 24 + 8 = 32 is Live + Reserved = all-codewords at n = 4.
--
-- HONEST BOUNDARY: the cardinalities 24 and 8 are stated in COMMENTS on those
-- Σ-types. UPDATE (◆AI-1b''/1d discharged): |Reserved| ≡ 8 IS now a term —
-- CodewordCountTies.reserved-exactly-8 (via Reserved ≅ Vec Bool 3, card-VecBool
-- 3), and the ambient |Codeword| ≡ 32 is codeword-ambient-32. So this co-apex is
-- MOSTLY tight now: complement 4 = 8 = the proved Reserved count, and 32 = the
-- proved ambient. The ONE remaining piece is |Live| ≡ 24 as a term (it follows
-- as 32 ∸ 8 but is not yet wired) — the honest residual, ◆AI-1b'''' below. The
-- ceiling-complement at n = 5 has NO such codeword home (the dim-4 code is
-- n = 4-specific): that is the whole content of "reappears with different
-- character" — now itself tightened by the RM(1,4)→RM(1,6) tie (◆AI-1c').
------------------------------------------------------------------------

-- The arithmetic identity the codeword decomposition would realise at n = 4:
-- Live(24) + Reserved(8) = 32 = 2⁵. Stated as pure ℕ (the shadow); the
-- codeword-side proof of the counts is ◆AI-1b.
codeword-closure-4 : |S| 4 + complement 4 ≡ 2 ^ 5
codeword-closure-4 = refl   -- 24 + 8 ≡ 32

------------------------------------------------------------------------
-- CO-APEX 3 (the surfaced gap, CORRECTED TWICE). "Leave ceil-exp as-is" was a
-- banked verdict with no probe run; the first fix (a Σ-witness `Σ k. property
-- k`) was STILL the wrong idiom — it names the answer and bolts minimality on,
-- and it introduces a Set-valued Σ (the set1 flavour the substrate pays down,
-- cf. ExtruderObsCoalg's ⟡set1-paydown: "carriers are module params, never
-- fields; drop Set₁ to Set").
--
-- The substrate does NOT use the Σ-witness idiom for "least k with a property".
-- The extrusion / inductive-tower machinery is the pattern: ExtruderFix — "an
-- extruder is the minimal M satisfying control C = MINIMISATION = the
-- μ-operator = a FIXED POINT; search = recursion; the search terminates at the
-- least fixed point." So the ceiling exponent is EXTRUDED (§3 above: ceil-exp =
-- μsearch, the least fixed point of the domination step), not witnessed. The
-- values fall OUT of the search.
--
-- Dominates below is the STOPPING PREDICATE of that extruder (the control C):
-- 2ᵏ ≥ m is exactly where μsearch halts. It is the extruder's control, not a
-- Σ-witness's payload.
------------------------------------------------------------------------

-- the extruder's control / stopping predicate: 2ᵏ ≥ m (where μsearch halts).
Dominates : ℕ → ℕ → Set
Dominates m k = ((2 ^ k) <ᵇ m) ≡ false     -- 2ᵏ ≥ m (μsearch's halt condition)

-- the extruded ceiling satisfies its own control at the fixpoint:
ceil-halts-4 : Dominates (|S| 4) (ceil-exp 4)   ; ceil-halts-4 = refl   -- 2⁵ ≥ 24
ceil-halts-5 : Dominates (|S| 5) (ceil-exp 5)   ; ceil-halts-5 = refl   -- 2⁷ ≥ 120

-- minimality: the exponent one below does NOT satisfy the control (the search
-- had not yet halted there) — so the extruded k is the LEAST fixed point.
ceil-minimal-4 : ((2 ^ 4) <ᵇ |S| 4) ≡ true   ; ceil-minimal-4 = refl   -- 16 < 24
ceil-minimal-5 : ((2 ^ 6) <ᵇ |S| 5) ≡ true   ; ceil-minimal-5 = refl   -- 64 < 120

------------------------------------------------------------------------
-- CO-APEX 4 (the remaining one — found by structure-probe, per ◆AI-D1: the
-- "2ⁿ column" is not bare arithmetic, it has a tower home). This claim IS
-- catalog K-cayley-dickson-level4 (concept C-cayley-dickson-seam), and the
-- Cayley-Dickson construction is exactly the 2ⁿ side:
--   Algebra.CayleyDickson.Carrier : ℕ → Set, Carrier (suc n) = Carrier n ×
--   Carrier n — "Carrier n = the 2ⁿ-dimensional algebra", the DOUBLING tower
--   ("a GENERATOR; like Free, like unfold, it runs forever" — same extrusion
--   idiom as ceil-exp's μsearch). Its basis is indexed by Vec Bool n
--   (Algebra.CayleyDickson.Cocycle.e : Vec Bool n → Carrier n), whose
--   cardinality is 2ⁿ. So AI-1's `2 ^ n` is the Cayley-Dickson basis-index
--   count — the doubling-tower dimension, not free-standing arithmetic.
--
-- DEEPER LINK (why this co-apex matters beyond the count): Cocycle.ε :
--   Vec Bool n → Vec Bool n → Bool is the CAYLEY-DICKSON SIGN COCYCLE
--   (eᵢ·eⱼ = ε(i,j)·e_{i⊕j}, true = −1). That is the SAME sign/cocycle shape
--   as this session's TowerCocycleGraded / sign-stab arc, on the 2ⁿ side. The
--   |Sₙ|-vs-2ⁿ sweep thus sits between two sign-carrying towers: the
--   permutation tower (|Sₙ|, sign = stab parity) and the Cayley-Dickson
--   doubling tower (2ⁿ, sign = ε cocycle). The n=4 seam (24+8=32) is where
--   they meet.
--
-- HONEST SCOPE (◆AI-D1): the count |Vec Bool n| ≡ 2ⁿ is NOW a proved term —
-- WitnessTower.VecBoolCardinality.card-VecBool (◆AI-1d discharged). So co-apex
-- 4 is upgraded: 2ⁿ IS the cardinality of the Cayley-Dickson basis-index type
-- Vec Bool n, as a theorem, not a bare literal. What remains a POINTER (not yet
-- a single refl) is only the identification of THIS file's `2 ^ n` occurrences
-- with `lengthL (allVB n)` at the use sites; card-VecBool supplies the bridge.
------------------------------------------------------------------------

-- (No term asserted inline here — Carrier/e/ε are cited structurally above. The
-- tight cardinality |Vec Bool n| ≡ 2ⁿ IS built: VecBoolCardinality.card-VecBool
-- (◆AI-1d discharged), and wired as SnVersusTwoPowTowers.Ⓣ₂-rung-count. So the
-- `2 ^ n` right column is the proved CD basis-index cardinality, not pending.)
