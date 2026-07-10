------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationSum
--
-- THE ADDITIVE OPERATION OF THE LEHMER-CODE RIG — GRADED, NEVER COLLAPSED.
--
-- The "semiring of Lehmer codes" (the symmetric rig of finite types) is the graded
-- rig on ⋃ₙ Lehmer(n): + = ⊎ (disjoint union / choice), × = × (product). It is
-- GRADED — a `Σ ℕ LehmerPath` carrier would bundle the whole family into one Set,
-- which is the grade collapse = Set₁ (see set1-is-grade-collapse). So the operations
-- are grade-SHIFTING maps, each grade its own Set₀; the rig decategorifies to ℕ
-- (the grades are the actual semiring carrier, ℕ's +/×), with the codes the graded
-- fibres constructed ACROSS the grade.
--
-- This file is the additive backbone `+`: the block-sum of two orderings — first
-- block ordered by l₁, second by l₂, first entirely before second. On the Lehmer
-- code it is a one-clause recursion: replay l₁'s choices, injecting each rank into
-- the larger index (inject+), on top of l₂. The grade follows ℕ's `+` by the type.
--
--   decode ((start ◂ 0) ⊕ (start ◂ 0)) = [0,1]     (1 ⊕ 1 = the identity of 2)
--   decode ((start ◂ 0) ⊕ (start ◂ 1)) = [0,2,1]   ([0] ⊕ swap = block-sum)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationSum where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Inject using (inject+)
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)

------------------------------------------------------------------------
-- 1. THE GRADED SUM. A grade-shifting map LehmerPath m → LehmerPath n →
--    LehmerPath (m + n): replay l₁'s choices on top of l₂, injecting each rank
--    into the larger index. The grade is m + n, in the type — the rig's `+`
--    decategorified to ℕ's `+`.
------------------------------------------------------------------------

infixr 6 _⊕_

_⊕_ : ∀ {m n} → LehmerPath m → LehmerPath n → LehmerPath (m + n)
start    ⊕ l₂ = l₂
(l₁ ◂ p) ⊕ l₂ = (l₁ ⊕ l₂) ◂ inject+ _ p

------------------------------------------------------------------------
-- 2. THE ADDITIVE UNIT. 0 = start : LehmerPath 0 (the empty ordering), and it is
--    the LEFT unit definitionally: 0 + n = n, start ⊕ l = l.
------------------------------------------------------------------------

0# : LehmerPath 0
0# = start

⊕-unit-left : ∀ {n} (l : LehmerPath n) → 0# ⊕ l ≡ l
⊕-unit-left l = refl

------------------------------------------------------------------------
-- 3. SEMANTIC CHECK: the sum decodes to the block-sum permutation. (1 ⊕ 1 is the
--    identity of 2; [0] ⊕ swap is the block-sum [0,2,1].) Both refl.
------------------------------------------------------------------------

_ : decode ((start ◂ zero) ⊕ (start ◂ zero)) ≡ (zero ∷ suc zero ∷ [])
_ = refl

_ : decode ((start ◂ zero) ⊕ (start ◂ zero ◂ suc zero)) ≡ (zero ∷ suc (suc zero) ∷ suc zero ∷ [])
_ = refl
