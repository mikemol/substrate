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
-- ⟡odecode-B INTEGRATED: the graded object-code family C now carries the REAL
-- codes — every rung's object-code is a `TmDB` (the object syntax, PROVEN
-- Gödel-codeable in TmDBGodel.Properties). So O = Σ ℕ TmDB is a NON-TRIVIAL
-- self-constructed universe of de-Bruijn/SKI codes, and `decode` builds a genuine
-- code from a LehmerPath (each rung applies the accumulated code to a `var`
-- witness). The tower CONVENTION places Source at grade 1, Target at 2, Witness
-- at 3, the object at 4 (grade = the Σ index; the object at that grade is a TmDB).
-- NOTE (the C-must-be-uniform finding): the LehmerAlgebra.step field is
-- ∀{n}→ C n → Fin(suc n) → C(suc n), a GENERIC-n map, so C(suc n) must reduce for
-- variable n — hence C is realized through the UNIFORM code carrier TmDB, not a
-- finite per-grade case-split (which would leave C(suc n) stuck).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ObjectUniverse where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin; toℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold; fold-unique; base; step)
open import Substrate.Category.UniversalProperty.TmDBGodel using (TmDB; var; I; app)
open import Substrate.Category.UniversalProperty.Term using (UPTerm)
open import Substrate.Category.UniversalProperty.Category
  using (UPCategory; UPCategory-canonical)

------------------------------------------------------------------------
-- 1. The graded object-code family C : ℕ → Set — now the REAL codes (⟡odecode-B
--    integrated): every rung's object-code is a TmDB (the object syntax, PROVEN
--    Gödel-codeable, TmDBGodel.Properties.TmDB-Canonical). C is uniform (C(suc n)
--    must reduce for the generic-n step field — see the header finding), so the
--    grade lives in the Σ index, not in C's type; the tower CONVENTION places
--    Source at grade 1, Target at grade 2, Witness at grade 3, the object at 4.
------------------------------------------------------------------------

C : ℕ → Set
C _ = TmDB

------------------------------------------------------------------------
-- 2. The LehmerAlgebra: the tower structure-map. base = the grade-0 object (I);
--    step = "rung n+1 = rung n APPLIED TO a de-Bruijn witness `var i`" — the
--    witnessing choice i : Fin (suc n) becomes the de-Bruijn index of the new
--    rung's back-reference (the `witnessing` IS de-Bruijn referencing).
------------------------------------------------------------------------

O-alg : LehmerAlgebra C
O-alg = record { base = I ; step = λ {n} c i → app c (var (toℕ i)) }

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
