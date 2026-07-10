------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.GradedStarV4
--
-- THE GRADED TWO-COMMUTATIVITY V₄ — the +↔× symmetry of the graded rig (⟡rig-1).
--
-- Commutativity of a magma operation is a C₂: `a·b = b·a` says the op is invariant
-- under the argument-swap involution σ:(a,b)↦(b,a), σ²=id. A rig has TWO commutative
-- operations, so two C₂s → V₄ = ℤ/2 × ℤ/2. For the graded Lehmer rig those are:
--   ⊕-commutativity = the block-swap (exchange the two ⊕-summands),
--   ⊗-commutativity = the factor-swap (exchange the two ⊗-factors),
-- two COMMUTING involutions (rows vs columns of the cross arrangement), whose composite
-- (klein-rot) permutes the diagonals the ×-comparison compares — the `×` being
-- V₄-equivariant (StarV4's "CrossMul is a Klein rotation").
--
-- This is StarV4 at the wedge centre, GRADED: the arrangement V₄ of FourPointV4 lifted
-- over a ℕ-graded carrier `C : ℕ → Set` (the carrier of a GradedDivStr / the tower's
-- orderings), living at EACH grade as its own Set₀ — never `Σ ℕ` collapse. It closes the
-- loop the session opened: FourPointV4 (from the four points) = StarV4 (at the wedge
-- centre) = GradedStarV4 (over the graded rig) — one V₄, three views, reusing exactly one
-- CommutingInvolutions packager.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.GradedStarV4 where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Category.Lawvere using (CommutingInvolutions)
open import Substrate.Algebra.Wedge.FourPointV4
  using (Square; rowSwap; colSwap; klein-rot; square-V4; klein-rot-inv)
open import Substrate.WitnessTower.Enumerate using (Perm)

------------------------------------------------------------------------
-- 1. THE GRADED V₄ over any ℕ-graded carrier. At grade n the four points are a 2×2
--    over the grade-n carrier `C n` — its own Set₀. The two commuting involutions ARE
--    the two rig commutativities.
------------------------------------------------------------------------

module _ (C : ℕ → Set) where

  -- the four points at grade n (a 2×2 over the grade-n carrier).
  GradedSquare : ℕ → Set
  GradedSquare n = Square {C n}

  -- ⊕-commutativity (row/summand exchange) and ⊗-commutativity (column/factor exchange),
  -- per grade — the two C₂s.
  ⊕-comm ⊗-comm : (n : ℕ) → GradedSquare n → GradedSquare n
  ⊕-comm n = rowSwap
  ⊗-comm n = colSwap

  -- THE GRADED V₄: at each grade the two commutativities commute (V₄-not-dihedral) and
  -- close to Klein four (klein-rot = their composite), packaged by the ONE
  -- CommutingInvolutions FourPointV4 uses. Each grade Set₀; no Σ ℕ collapse.
  graded-V4 : (n : ℕ) → CommutingInvolutions (GradedSquare n)
  graded-V4 n = square-V4 {C n}

  -- the cross-rotation (⊕-comm ∘ ⊗-comm = klein-rot): the diagonal swap the ×-comparison
  -- is equivariant under — an involution.
  cross-rot : (n : ℕ) → GradedSquare n → GradedSquare n
  cross-rot n = klein-rot

  cross-rot-inv : (n : ℕ) (s : GradedSquare n) → cross-rot n (cross-rot n s) ≡ s
  cross-rot-inv n = klein-rot-inv

------------------------------------------------------------------------
-- 2. INSTANTIATED AT THE ORIENTATION TOWER. The graded carrier is `Perm` (the tower's
--    grade-n orderings, OrientationFixedPoint's μΦ). So the graded two-commutativity V₄
--    lives over the actual Sₙ orientations — the +↔× symmetry of the ⟡perm rig.
------------------------------------------------------------------------

tower-V4 : (n : ℕ) → CommutingInvolutions (Square {Perm n})
tower-V4 = graded-V4 Perm
