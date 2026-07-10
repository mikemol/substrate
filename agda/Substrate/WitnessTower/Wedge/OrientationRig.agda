------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationRig
--
-- THE GRADED LEHMER RIG, ASSEMBLED — ⟡rig-3 (decategorified Semiring-over-ℕ) and
-- ⟡rig-4 (the two commutativity C₂s), over ⟡rig-1 (GradedStarV4's V₄) and ⟡rig-2
-- (OrientationProductPerm's ⊗-closure).
--
-- The "semiring of Lehmer codes" is a symmetric rig GROUPOID: its objects are the
-- orderings (graded, each grade its own Set₀ — never `Σ ℕ` collapse), and its laws are
-- of two kinds, and this file keeps them honestly separate:
--
--   • STRICT, at the DECATEGORIFIED level (⟡rig-3). The grade of a rig element is its
--     ℕ-index; the operations shift it by ℕ's + and * BY THE TYPE (⊕ : grade m+n,
--     ⊗ : grade m·n; 0#/1# at grades 0/1). So the decategorification is exactly
--     (ℕ, +, *, 0, 1) — a commutative semiring, its laws literally ℕ's. We bank them
--     here as the strict rig laws. The ONE law that also lifts strictly to the orderings
--     is the additive left-unit (0# ⊕ l ≡ l, definitional — grade 0+n=n).
--
--   • UP-TO-ISO, at the CATEGORIFIED level (the coherence). ⊕-associativity, the
--     ⊗-associator, and the two distributors relate orderings via the canonical
--     block-/factor-transposition permutations — the symmetric-rig-groupoid coherence.
--     Those ordering-level isos are the NEXT arc; here we bank the grade-strict skeleton
--     they lift, and the two COMMUTATIVITY isos, which ⟡rig-1 already packages as a V₄.
--
-- ⟡rig-4: commutativity a·b = b·a is invariance under the argument-swap involution
-- s:(a,b)↦(b,a) (a C₂). The rig's two ops give two C₂s over that one swap, distinguished
-- by grade-effect: ⊕ ↦ +-comm, ⊗ ↦ *-comm. GradedStarV4's 2×2 arrangement gives them
-- INDEPENDENT axes (rowSwap = ⊕-comm, colSwap = ⊗-comm) so the two commute = V₄.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.OrientationRig where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-identityʳ; +-assoc; +-comm)
open import Substrate.Foundation.Nat.Properties.Mul
  using (*-identityˡ; *-identityʳ; *-assoc; *-comm; *-distribˡ-+; *-distribʳ-+)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Category.Lawvere using (CommutingInvolutions)
open import Substrate.Algebra.Wedge.FourPointV4 using (Square; rowSwap; colSwap; square-V4)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath)
open import Substrate.WitnessTower.Wedge.OrientationSum using (_⊕_; 0#; ⊕-unit-left)
open import Substrate.WitnessTower.Wedge.OrientationProduct using (_⊗_; 1#)
open import Substrate.WitnessTower.Wedge.OrientationProductPerm using (⊗-is-perm)
open import Substrate.WitnessTower.Wedge.GradedStarV4 using (tower-V4)

------------------------------------------------------------------------
-- 1. ⟡rig-3 — THE DECATEGORIFIED COMMUTATIVE SEMIRING (ℕ, +, *, 0, 1).
--    The grade laws ARE ℕ's; we bank them as the strict rig skeleton. Each governs the
--    correspondingly-graded rig operation by the type (⊕ : m+n, ⊗ : m·n).
------------------------------------------------------------------------

-- additive commutative monoid (the ⊕ grade):
⊕-grade-assoc : (m n p : ℕ) → (m + n) + p ≡ m + (n + p)
⊕-grade-assoc = +-assoc

⊕-grade-identityʳ : (n : ℕ) → n + zero ≡ n
⊕-grade-identityʳ = +-identityʳ

⊕-grade-comm : (m n : ℕ) → m + n ≡ n + m
⊕-grade-comm = +-comm

-- multiplicative commutative monoid (the ⊗ grade):
⊗-grade-assoc : (m n p : ℕ) → (m * n) * p ≡ m * (n * p)
⊗-grade-assoc = *-assoc

⊗-grade-identityˡ : (n : ℕ) → suc zero * n ≡ n
⊗-grade-identityˡ = *-identityˡ

⊗-grade-identityʳ : (n : ℕ) → n * suc zero ≡ n
⊗-grade-identityʳ = *-identityʳ

⊗-grade-comm : (m n : ℕ) → m * n ≡ n * m
⊗-grade-comm = *-comm

-- distributivity of × over + at the grade (the rig coherence, decategorified):
⊗-grade-distribˡ : (a m n : ℕ) → a * (m + n) ≡ a * m + a * n
⊗-grade-distribˡ = *-distribˡ-+

⊗-grade-distribʳ : (a m n : ℕ) → (m + n) * a ≡ m * a + n * a
⊗-grade-distribʳ = *-distribʳ-+

-- The one law that lifts STRICTLY to the orderings (not just the grades): the additive
-- left-unit. 0# is start : LehmerPath 0, and 0# ⊕ l ≡ l on the nose (grade 0+n=n).
⊕-ordering-unit-left : ∀ {n} (l : LehmerPath n) → 0# ⊕ l ≡ l
⊕-ordering-unit-left = ⊕-unit-left

------------------------------------------------------------------------
-- 2. ⟡rig-4 — THE TWO COMMUTATIVITY C₂s. The argument-swap involution on an operand
--    grade-pair, and the two commutativity witnesses (⊕ ↦ +-comm, ⊗ ↦ *-comm) it makes
--    a C₂ of. GradedStarV4's V₄ is these two on independent 2×2 axes.
------------------------------------------------------------------------

-- the argument-swap s:(a,b)↦(b,a) on an operand grade-pair — the C₂ generator.
swap-grade : ℕ × ℕ → ℕ × ℕ
swap-grade (m , n) = (n , m)

-- it is an involution (s² = id): the C₂ is genuine.
swap-grade-inv : (p : ℕ × ℕ) → swap-grade (swap-grade p) ≡ p
swap-grade-inv (m , n) = refl

-- ⊕-commutativity: the additive grade is invariant under the swap — this IS +-comm.
--   grade(a ⊕ b) = m + n ; grade(b ⊕ a) = n + m ; +-comm bridges them.
⊕-commutativity : (p : ℕ × ℕ) →
                  proj₁ p + proj₂ p ≡ proj₁ (swap-grade p) + proj₂ (swap-grade p)
⊕-commutativity (m , n) = +-comm m n

-- ⊗-commutativity: the multiplicative grade is invariant under the swap — this IS *-comm.
⊗-commutativity : (p : ℕ × ℕ) →
                  proj₁ p * proj₂ p ≡ proj₁ (swap-grade p) * proj₂ (swap-grade p)
⊗-commutativity (m , n) = *-comm m n

-- The two C₂s, packaged as the V₄ on the 2×2 arrangement (⟡rig-1). rowSwap is the
-- ⊕-commutativity axis, colSwap the ⊗-commutativity axis; they commute (V₄, not
-- dihedral) at every grade — GradedStarV4's tower-V4.
rig-V4 : (n : ℕ) → CommutingInvolutions (Square {Perm n})
rig-V4 = tower-V4

-- the two commutativity involutions on the arrangement, named at the rig:
⊕-comm-involution ⊗-comm-involution : ∀ {C : Set} → Square {C} → Square {C}
⊕-comm-involution = rowSwap
⊗-comm-involution = colSwap

------------------------------------------------------------------------
-- 3. ⟡rig-2 — MULTIPLICATIVE CLOSURE ON THE ORDERINGS. `×` maps orderings to orderings
--    (the product of two permutations is a permutation), re-exported from
--    OrientationProductPerm — so the rig lives on Sₙ, not on raw Vecs.
------------------------------------------------------------------------

⊗-closed : ∀ {m n} (σ : Perm m) (τ : Perm n) → IsPerm σ → IsPerm τ → IsPerm (σ ⊗ τ)
⊗-closed = ⊗-is-perm
