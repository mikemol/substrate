------------------------------------------------------------------------
-- Substrate.Logic.Evidence.DualRail
--
-- NEDGE OVER AN ARBITRARY CARRIER — not hardwired to Bool.
--
-- (user, 2026-06-12) "I want Nedge to not be based over Bool, but over an arbitrary
-- compatible carrier (Real, Complex, or whatever the CD generator is). It feels
-- almost stateful." It IS: the dual-rail carrier `EvCarrier C = C × C` is one
-- doubling, and nesting it is the state. The current `Verdict.Evidence` is the
-- `C = Bool` instance frozen in place; here the carrier is a parameter.
--
-- WHAT A "COMPATIBLE CARRIER" NEEDS — two pieces, both held by ℝ/ℂ/ℚ/CD:
--   (1) an INVOLUTION `neg : C → C` for the el-atlas §5 chart involutions
--       (negPos/negNeg/negBoth, the V₄, the rail-swap). Bool's `not`; ℝ/ℚ's
--       negate; ℂ/CD's conjugate. The V₄ laws hold GENERICALLY for any involution
--       — `Verdict.Phase.negBoth-invol` was never about Bool, it is that generic
--       fact at C = Bool.
--   (2) a SEMIRING `(add, mul)` for the connectives ∧E/∨E/⊗E/⊕E.
--
-- The connectives are NOT a lattice and do NOT use min/max (a correction — the user
-- caught this: min/max TRUNCATE, and never-discard-residue forbids that as the
-- generalization). Bool's ∧/∨ are the Boolean SEMIRING's × and +; the connectives
-- act rail-wise with the carrier's OWN ×,+ — `⊗E` = ×-both, `⊕E` = +-both,
-- `∧E` = ⟨×,+⟩, `∨E` = ⟨+,×⟩. ℝ/ℂ/ℚ/CD all have ×,+, so the connectives generalize
-- to them with no order and no truncation. (min/max is only the TROPICAL semiring —
-- one gauge of commuting-sphere #6 "Bool / GF(2) / ℕ / tropical", and the lossy one;
-- Verdict.agda already says the continuous lift is log-PRODUCT / log-sum-exp, not
-- min/max.) Both layers are below: `DualRail` (involutions) and `Connectives`.
--
-- THE UNIFICATION (the "stateful" feeling, made precise). One dual-rail step over
-- C is `C × C` — which is exactly the Cayley–Dickson carrier doubling
-- (`Algebra.CayleyDickson.Carrier (suc n) = Carrier n × Carrier n`). So:
--   Nedge dual-rail  ≡  CD carrier-doubling      (`cd-doubling-is-dualrail`, refl)
-- and iterating Nedge from C = ℚ IS the CD tower ℂ, ℍ, 𝕆, 𝕊, … — Nedge's negNeg
-- (negate the second rail) is the CD conjugation's outer move. Same generator;
-- Nedge takes the involution/lattice face, CD adds the twisted product.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.DualRail where

open import Substrate.Foundation.Nat     using (ℕ; suc)
open import Substrate.Foundation.Bool    using (Bool; true; false; not; _∧_; _∨_)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq      using (_≡_; refl; cong; cong₂)

open import Substrate.Algebra.CayleyDickson using (Carrier)
open import Substrate.Algebra.Q     using (ℚ)
open import Substrate.Algebra.Q.Add using (_+ℚ_)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)

------------------------------------------------------------------------
-- The dual-rail carrier, parametric in the underlying carrier C.
------------------------------------------------------------------------

EvCarrier : Set → Set
EvCarrier C = C × C   -- ⟨ positive rail , negative rail ⟩

------------------------------------------------------------------------
-- The Nedge structure over C, parametric in C's involution `neg` (and its
-- involutivity proof). All four chart involutions + the rail-swap, and the V₄
-- laws — generic.
------------------------------------------------------------------------

module DualRail {C : Set} (neg : C → C) (neg² : (x : C) → neg (neg x) ≡ x) where

  Evidence : Set
  Evidence = EvCarrier C

  posR negR : Evidence → C
  posR = proj₁    -- E⁺
  negR = proj₂    -- E⁻

  -- the chart involutions (el-atlas §5): each negates a rail with C's involution.
  negPos negNeg negBoth swapE : Evidence → Evidence
  negPos  (p , n) = neg p , n
  negNeg  (p , n) = p , neg n
  negBoth (p , n) = neg p , neg n
  swapE   (p , n) = n , p          -- the rail-swap (S5); needs no C-structure

  -- the V₄ involution laws — GENERIC over any involution `neg`.
  negPos-invol : (e : Evidence) → negPos (negPos e) ≡ e
  negPos-invol (p , n) = cong (_, n) (neg² p)

  negNeg-invol : (e : Evidence) → negNeg (negNeg e) ≡ e
  negNeg-invol (p , n) = cong (p ,_) (neg² n)

  negBoth-invol : (e : Evidence) → negBoth (negBoth e) ≡ e
  negBoth-invol (p , n) = cong₂ _,_ (neg² p) (neg² n)

  swapE-invol : (e : Evidence) → swapE (swapE e) ≡ e
  swapE-invol (p , n) = refl

  -- the Klein four-group composition negPos ∘ negNeg = negBoth (commuting).
  negPos∘negNeg : (e : Evidence) → negPos (negNeg e) ≡ negBoth e
  negPos∘negNeg (p , n) = refl

  negNeg∘negPos : (e : Evidence) → negNeg (negPos e) ≡ negBoth e
  negNeg∘negPos (p , n) = refl

------------------------------------------------------------------------
-- Instance 1 — Bool. Recovers exactly the original Belnap `Verdict.Evidence`
-- involutions; `Verdict.Phase.negBoth-invol` is this generic law at C = Bool.
------------------------------------------------------------------------

not-invol : (b : Bool) → not (not b) ≡ b
not-invol true  = refl
not-invol false = refl

module BoolNedge = DualRail not not-invol

------------------------------------------------------------------------
-- The unification: a dual-rail step over `Carrier n` IS the Cayley–Dickson
-- doubling `Carrier (suc n)` — definitionally (the "stateful" doubling the user
-- felt). Iterating Nedge from C = ℚ = `Carrier 0` walks the CD tower ℂ/ℍ/𝕆/𝕊/….
------------------------------------------------------------------------

cd-doubling-is-dualrail : (n : ℕ) → Carrier (suc n) ≡ EvCarrier (Carrier n)
cd-doubling-is-dualrail n = refl

------------------------------------------------------------------------
-- The connectives, parametric in the carrier's SEMIRING (add, mul). NO lattice,
-- NO min/max, NO truncation — these are the carrier's own +,× applied rail-wise.
-- Bool's (∨, ∧) recover Verdict's connectives; ℝ/ℂ/ℚ/CD use their +,×.
------------------------------------------------------------------------

module Connectives {C : Set} (add mul : C → C → C) where

  -- info order — the §1 independent accumulators:
  _⊗E_ _⊕E_ : EvCarrier C → EvCarrier C → EvCarrier C   -- consensus / accumulate
  (pa , na) ⊗E (pb , nb) = mul pa pb , mul na nb
  (pa , na) ⊕E (pb , nb) = add pa pb , add na nb

  -- truth order — the §5/§6 De-Morgan-exchanged pair:
  _∧E_ _∨E_ : EvCarrier C → EvCarrier C → EvCarrier C   -- meet / join
  (pa , na) ∧E (pb , nb) = mul pa pb , add na nb
  (pa , na) ∨E (pb , nb) = add pa pb , mul na nb

-- Bool instance — the Boolean semiring (+ = ∨, × = ∧); recovers Verdict's
-- connectives (up to the Evidence ≅ Bool × Bool iso). The "truncating min/max"
-- never appears: ∧/∨ here are the semiring's ×/+.
module BoolConnectives = Connectives _∨_ _∧_

-- ℚ instance — a genuinely numeric carrier, connectives via +ℚ / *ℚ. Demonstrates
-- the connectives need only a semiring, not an order: no min, no max, no truncation.
module QConnectives = Connectives _+ℚ_ _*ℚ_
