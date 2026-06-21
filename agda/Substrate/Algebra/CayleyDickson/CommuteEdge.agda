------------------------------------------------------------------------
-- Substrate.Algebra.CayleyDickson.CommuteEdge
--
-- ⊙ C3 (a rung of the commute-edge grade): Cayley-Dickson multiplication is
-- COMMUTATIVE at level 1 (ℂ = the Gaussian rationals). This is the bottom of
-- the conjectured "ladder graded loss" ℂ commutative → ℍ noncommutative → 𝕆
-- nonassociative → 𝕊 zero-divisors: the commute-edge GRADE. The top rung (the
-- 𝕊 zero-divisor at level 4) is already in `Algebra.CayleyDickson`
-- (`zd-value-0` + `xZD≢0`/`yZD≢0`); this supplies the commutative bottom.
--
-- Over `≈#` (the CD semantic equality, componentwise `≈ℚ`), since ℚ's `*ℚ`-comm
-- is `≈ℚ`, not `≡`. Reuses *ℚ-comm / +ℚ-comm / +ℚ-cong and the new `-ℚ-cong`
-- (negation respects ≈ℚ, via `neg-*-left`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.CayleyDickson.CommuteEdge where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
open import Substrate.Foundation.Product using (_,_; proj₂)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.Q using (ℚ; num; 0ℚ; 1ℚ; -1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Neg using (-ℚ_)
open import Substrate.Algebra.Z using (-ℤ_)
open import Substrate.Algebra.Z.Mul using (_*ℤ_)
open import Substrate.Algebra.Z.Properties.Mul using (neg-*-left)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.Q.Properties.Field using (*ℚ-comm; +ℚ-comm)
open import Substrate.Algebra.Q.Properties.Congruence using (+ℚ-cong)
open import Substrate.Algebra.CayleyDickson using (Carrier; ℂ#; ℍ#; mul; ≈#)

------------------------------------------------------------------------
-- ℚ negation respects ≈ℚ (a general Congruence lemma; the `sub`-component of
-- the CD product needs it). Negate both sides of the cross-product identity.
------------------------------------------------------------------------

-ℚ-cong : {x y : ℚ} → x ≈ℚ y → (-ℚ x) ≈ℚ (-ℚ y)
-ℚ-cong {x} {y} x≈y =
  trans (neg-*-left (num x) _)
        (trans (cong -ℤ_ x≈y) (sym (neg-*-left (num y) _)))

------------------------------------------------------------------------
-- C3 rung: ℂ multiplication commutes (the commute-edge bottom).
--   mul 1 (a,b) (c,d) = (a·c − d·b , d·a + b·c)   [conj is id at level 0]
-- 1st component commutes by *ℚ-comm under the subtraction (-ℚ-cong);
-- 2nd component is a bare +ℚ-comm.
------------------------------------------------------------------------

mul-comm-ℂ : (x y : ℂ#) → ≈# 1 (mul 1 x y) (mul 1 y x)
mul-comm-ℂ (a , b) (c , d) =
    +ℚ-cong {a *ℚ c} {c *ℚ a} { -ℚ (d *ℚ b) } { -ℚ (b *ℚ d) }
            (*ℚ-comm a c) (-ℚ-cong {d *ℚ b} {b *ℚ d} (*ℚ-comm d b))
  , +ℚ-comm (d *ℚ a) (b *ℚ c)

------------------------------------------------------------------------
-- THE EDGE: ℍ multiplication does NOT commute (the rung above ℂ). i·j = k,
-- j·i = −k, so they differ at the k-component (1ℚ vs −1ℚ). With mul-comm-ℂ
-- above, this PINPOINTS the commute-edge grade: commutativity is lost going
-- ℂ → ℍ (level 1 → 2). (Same ≈#-⊥ pattern as CayleyDickson.xZD≢0.)
------------------------------------------------------------------------

1ℚ≉-1ℚ : 1ℚ ≈ℚ -1ℚ → ⊥
1ℚ≉-1ℚ ()

iₕ jₕ : ℍ#
iₕ = ((0ℚ , 1ℚ) , (0ℚ , 0ℚ))   -- the level-1 imaginary, in ℍ's first half
jₕ = ((0ℚ , 0ℚ) , (1ℚ , 0ℚ))   -- the new (level-2) imaginary

mul-noncomm-ℍ : ≈# 2 (mul 2 iₕ jₕ) (mul 2 jₕ iₕ) → ⊥
mul-noncomm-ℍ z = 1ℚ≉-1ℚ (proj₂ (proj₂ z))
