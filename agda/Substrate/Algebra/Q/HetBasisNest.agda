------------------------------------------------------------------------
-- Substrate.Algebra.Q.HetBasisNest
--
-- FOLLOW-UP CHALLENGE: can HetQ be the type of HetQ's numerator? Its
-- denominator? Both?
--
-- YES to all three, unconditionally. `HetQ : Set → Set → Set` and
-- `HetQ A B : Set`, so HetQ may be substituted into EITHER or BOTH of its own
-- arguments — it is freely self-composable (a bifunctor closed under nesting).
-- The three nestings each have a meaning, and each FLATTENS one rung by
-- cross-multiplication (the same cross term that is HetQ's equality):
--
--   (1) numerator nested   (p/q)/d   = p/(q·d)              -- inner ratio sinks
--   (2) denominator nested a/(p/q)   = a·q/p                -- RECIPROCAL: the
--                                                              continued-fraction move
--   (3) both nested      (p/q)/(r/s) = (p·s)/(q·r)          -- division of fractions
--
-- Iterating (2) is the reciprocal SPINE of a continued fraction: 1/(p/(q/…))
-- is HetQ nested in its own denominator, arbitrarily deep. (A full continued
-- fraction aᵢ + 1/(…) layers an affine +aᵢ on each rung; the self-nesting here
-- is the bare reciprocal tower it is built on — which is why ℚ-as-HetQ being
-- self-closed is the structural prerequisite for the substrate's CF machinery.)
--
-- Carrier ℕ here (positive rationals) so the flatten arithmetic stays sign-free
-- and the checks reduce to `refl`.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Q.HetBasisNest where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Q.HetBasis

------------------------------------------------------------------------
-- Inner fraction carrier + its cross-multiplication equality in R = ℕ.
------------------------------------------------------------------------

Frac : Set
Frac = HetQ ℕ ℕ

open CrossEq _*_ _≡_ refl sym renaming (_≈H_ to _≈Hℕ_)

------------------------------------------------------------------------
-- (1) HetQ as the NUMERATOR type:  (p/q)/d.
------------------------------------------------------------------------

NumNested : Set
NumNested = HetQ Frac ℕ

ex-num-nested : NumNested
ex-num-nested = (1 // 2) // 3              -- (1/2)/3

flattenNum : NumNested → Frac              -- (p/q)/d = p/(q·d)
flattenNum h = hnum (hnum h) // (hden (hnum h) * hden h)

chkNum : flattenNum ex-num-nested ≈Hℕ (1 // 6)
chkNum = refl                              -- 1//(2·3) = 1//6;  1·6 ≡ 1·6

------------------------------------------------------------------------
-- (2) HetQ as the DENOMINATOR type:  a/(p/q) — the reciprocal / CF step.
------------------------------------------------------------------------

DenNested : Set
DenNested = HetQ ℕ Frac

ex-den-nested : DenNested
ex-den-nested = 6 // (2 // 3)              -- 6/(2/3)

flattenDen : DenNested → Frac              -- a/(p/q) = a·q/p
flattenDen h = (hnum h * hden (hden h)) // hnum (hden h)

chkDen : flattenDen ex-den-nested ≈Hℕ (9 // 1)
chkDen = refl                              -- (6·3)//2 = 18//2;  18·1 ≡ 9·2

------------------------------------------------------------------------
-- (3) HetQ as BOTH:  (p/q)/(r/s) — ratio of ratios (division of fractions).
------------------------------------------------------------------------

BothNested : Set
BothNested = HetQ Frac Frac

ex-both : BothNested
ex-both = (1 // 2) // (3 // 4)             -- (1/2)/(3/4)

flattenBoth : BothNested → Frac            -- (p/q)/(r/s) = (p·s)/(q·r)
flattenBoth h = (hnum (hnum h) * hden (hden h)) // (hden (hnum h) * hnum (hden h))

chkBoth : flattenBoth ex-both ≈Hℕ (2 // 3)
chkBoth = refl                             -- (1·4)//(2·3) = 4//6;  4·3 ≡ 2·6

------------------------------------------------------------------------
-- The self-closure is genuine: a THREE-deep tower (HetQ in a denominator that
-- is itself denominator-nested) type-checks and flattens by iterating (2).
------------------------------------------------------------------------

DeepTower : Set
DeepTower = HetQ ℕ (HetQ ℕ Frac)           -- a/(b/(c/d))

ex-tower : DeepTower
ex-tower = 1 // (2 // (3 // 4))             -- 1/(2/(3/4))

-- collapse the inner two rungs with flattenDen, then the outer rung.
flattenTower : DeepTower → Frac
flattenTower h = flattenDen (hnum h // flattenDen (hden h))

chkTower : flattenTower ex-tower ≈Hℕ (3 // 8)
chkTower = refl    -- 2/(3/4) = 8/3; 1/(8/3) = 3/8;  3·8 ≡ 3·8
