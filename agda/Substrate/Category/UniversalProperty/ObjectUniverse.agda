------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ObjectUniverse
--
-- ⟡odecode-A-tower-O — Phase A of ⟡ta-upterm-O-decode: the self-constructed
-- Set₀ OBJECT UNIVERSE O for the UP-topos, built as the WITNESS TOWER.
--
-- The reframe (user, 2026-07-16): an object IS a witness-tower path. Source =
-- rung 1, Target = rung 2 (witnessing the Source→Target edge), Witness = rung 3
-- (witnessing the edge), and the element-of-O = rung 4, witnessing the first
-- three. This is realized by the tower's PROVEN free construction — the
-- `LehmerAlgebra`/`fold`/`fold-unique` catamorphism (OrientationUniversal.agda):
--   * decode        = fold O-alg          (the object at each grade)
--   * decode-unique = fold-unique O-alg   (∃!-witnessing, as a THEOREM — ZERO new
--                                          proof; the ∃! is the record's own lemma)
--   * O := Σ ℕ C                          (the flat total-space, Set₀; grade = proj₁)
--   * O-category = UPCategory-canonical O Hom   (O inhabits the topos object slot)
--
-- PHASE A stubs the graded object-code family C to ⊤ at every rung — this
-- proves the tower-rung O inhabits the UP-topos (the skeleton compiles + the
-- fold/uniqueness/category all instantiate). PHASE B (⟡odecode-B-godel) swaps
-- the ⊤ stubs for the real codes:
--     grade 1 ↦ SourceCode ·  grade 2 ↦ TargetCode ·  grade 3 ↦ WitnessCode ·
--     grade 4+ ↦ OCode (the de-Bruijn/Gödel object codes).
-- NOTE: the LehmerAlgebra.step field is ∀{n}→ C n → Fin(suc n) → C(suc n), a
-- GENERIC-n map, so C(suc n) must reduce for variable n — Phase B realizes the
-- per-grade codes through a uniform code carrier, not a finite case-split (which
-- would leave C(suc n) stuck). Here C _ = ⊤ (uniform) is the honest stub.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ObjectUniverse where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique; base; step)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Category
  using (UPCategory; UPCategory-canonical)

------------------------------------------------------------------------
-- 1. The graded object-code family C : ℕ → Set (Phase A: uniform ⊤ stub).
--    See the header for the intended per-grade code structure (Phase B).
------------------------------------------------------------------------

C : ℕ → Set
C _ = ⊤

------------------------------------------------------------------------
-- 2. The LehmerAlgebra: the tower structure-map. base = the grade-0 object,
--    step = "rung n+1 from rung n + a witnessing choice". (Phase A: ⊤/tt.)
------------------------------------------------------------------------

O-alg : LehmerAlgebra C
O-alg = record { base = tt ; step = λ _ _ → tt }

------------------------------------------------------------------------
-- 3. decode = the fold; decode-unique = the fold's universal property.
--    The object at grade n is the fold image of a LehmerPath n. Uniqueness
--    (∃!-witnessing) is fold-unique O-alg VERBATIM — no new proof obligation.
------------------------------------------------------------------------

decode : ∀ {n} → LehmerPath n → C n
decode = fold O-alg

decode-unique :
  (g : ∀ {n} → LehmerPath n → C n) →
  (g start ≡ base O-alg) →
  (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) → g (l ◂ p) ≡ step O-alg (g l) p) →
  ∀ {n} (l : LehmerPath n) → g l ≡ decode l
decode-unique = fold-unique O-alg

------------------------------------------------------------------------
-- 4. O := Σ ℕ C — the FLAT total-space, Set₀; grade recoverable via proj₁.
--    An object is `(n , decode l)` — a point of the object-tower total space.
------------------------------------------------------------------------

O : Set
O = Σ ℕ C

object : ∀ {n} → LehmerPath n → O
object {n} l = n , decode l

------------------------------------------------------------------------
-- 5. O inhabits the UP-topos object slot: the canonical category at O.
--    Hom stays an abstract parameter (the topos always ranged over (O, Hom));
--    Phase A's payoff is that O is now a CONCRETE Set₀ built as the tower,
--    plugged directly into UPCategory-canonical (Obj : Set accepts Σ ℕ C).
------------------------------------------------------------------------

module _ (Hom : O → O → Set) where

  O-category : UPCategory O (UPTerm O Hom)
  O-category = UPCategory-canonical O Hom
