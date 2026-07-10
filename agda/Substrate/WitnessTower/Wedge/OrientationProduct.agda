------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationProduct
--
-- THE MULTIPLICATIVE OPERATION OF THE LEHMER-CODE RIG — GRADED, NEVER COLLAPSED.
--
-- The second face of the graded rig of orderings (after OrientationSum's `+`).
-- `×` = the product of two orderings: order the m·n pairs (i,j) with i by σ and j
-- by τ, through the finite-type product iso Fin(m·n) ≅ Fin m × Fin n
-- (Foundation.Fin.combine / remQuot). It is a grade-SHIFTING map to grade m·n; the
-- rig decategorifies to ℕ's `*`. (An ordering is a Perm here — the vector side of
-- the ordering ≅ LehmerPath, WitnessTower.Wedge.OrientationFixedPoint; `+` lives on
-- the code side, `×` on the vector side, one graded structure via decode/encode.)
--
--   (σ⊗τ)(k) = combine (σ (i)) (τ (j))   where (i,j) = remQuot n k
--
--   swap₂ ⊗ id₂ = [2,3,0,1]   (swap the two size-2 blocks — the wreath action)
--
-- 1 = the one-element ordering; unit and associativity/distributivity are the
-- grade-indexed rig laws (over the *-transports, e.g. 1*n = n+0), to follow.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationProduct where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)

------------------------------------------------------------------------
-- 1. THE GRADED PRODUCT. A grade-shifting map Perm m → Perm n → Perm (m * n):
--    split each target index k into (i,j) by remQuot, order the pair by (σ,τ), and
--    re-combine. The grade is m * n, in the type — the rig's `×` decategorified.
------------------------------------------------------------------------

infixr 7 _⊗_

_⊗_ : ∀ {m n} → Perm m → Perm n → Perm (m * n)
_⊗_ {m} {n} σ τ =
  tabulate (λ k → combine (lookup σ (proj₁ (remQuot {m} n k))) (lookup τ (proj₂ (remQuot {m} n k))))

------------------------------------------------------------------------
-- 2. THE MULTIPLICATIVE UNIT. 1 = the unique ordering of one element.
------------------------------------------------------------------------

1# : Perm 1
1# = zero ∷ []

------------------------------------------------------------------------
-- 3. SEMANTIC CHECK: swap-of-2 ⊗ id-of-2 swaps the two size-2 blocks = [2,3,0,1]
--    (the wreath action of the product). refl.
------------------------------------------------------------------------

_ : (suc zero ∷ zero ∷ []) ⊗ (zero ∷ suc zero ∷ [])
      ≡ (suc (suc zero) ∷ suc (suc (suc zero)) ∷ zero ∷ suc zero ∷ [])
_ = refl
