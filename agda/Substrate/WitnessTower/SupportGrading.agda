------------------------------------------------------------------------
-- Substrate.WitnessTower.SupportGrading
--
-- Generalizing the involution census (WitnessTower.FirstAppearance) to
-- ALL permutations, the way an external reading suggested: the rung at
-- which a structure first appears is its MINIMAL SUPPORT, and that is a
-- grading.
--
--   grade(structure) = min { n | realizable at rung n } = support(structure)
--
-- For a permutation, support = moved-count (the number of non-fixed
-- points) — already defined in FirstAppearance, and it is the support
-- size for ANY permutation, not only involutions. So "new objects at rung
-- n" = cycle types with support EXACTLY n, and the census reads the debut
-- of each support value off the iterated enumeration.
--
-- The clean fact Agda is asked to confirm: at rung n the count of FULLY
-- supported permutations (support = n, i.e. no fixed point) is the
-- DERANGEMENT number Dₙ — these are exactly the structures whose grade
-- (minimal support) is n, the ones genuinely NEW at rung n.
--
--   D₂ = 1, D₃ = 2, D₄ = 9.   (by-support n n ≡ Dₙ)
--
-- HONESTY caveat (the reason the earlier involution census was special):
-- moved-count COLLAPSES cycle type. (1 2 3 4) and (1 2)(3 4) BOTH move 4.
-- So support is a complete invariant for grading-BY-SUPPORT, but NOT a
-- cycle-type discriminator outside involutions (where moved-count =
-- 2·#2-cycles is injective on type). At rung 4 the support-4 debut (9
-- elements) splits into 3 double-transpositions + 6 four-cycles —
-- distinguishing those needs an actual cycle decomposition, not
-- moved-count. We compute that split here too, to mark the boundary
-- honestly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.SupportGrading where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_) renaming (_≟_ to _≟ℕ_)
open import Substrate.Foundation.Bool using (Bool; _∧_; not)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.WitnessTower.Enumerate using (Perm; perms; lengthL)
open import Substrate.WitnessTower.FirstAppearance
  using (moved-count; is-involution; filterL; ⌊_⌋)

------------------------------------------------------------------------
-- 1. Census by support value: how many permutations of rung n have
--    support (moved-count) exactly m.
------------------------------------------------------------------------

by-support : (n m : ℕ) → ℕ
by-support n m =
  lengthL (filterL (λ σ → ⌊ moved-count σ ≟ℕ m ⌋) (perms n))

------------------------------------------------------------------------
-- 2. Support 1 is impossible at every rung (you cannot move exactly one
--    point) — so rung 1 contributes no new realizable structure, and the
--    grading skips 1.
------------------------------------------------------------------------

support-1-impossible-4 : by-support 4 1 ≡ 0
support-1-impossible-4 = refl
support-1-impossible-3 : by-support 3 1 ≡ 0
support-1-impossible-3 = refl

------------------------------------------------------------------------
-- 3. The debut = minimal support. Support m is ABSENT below rung m, and
--    PRESENT at rung m with multiplicity Dₘ (derangements: full support).
------------------------------------------------------------------------

-- support 2 debuts at rung 2 with D₂ = 1.
support-2-absent-1 : by-support 1 2 ≡ 0
support-2-absent-1 = refl
support-2-debut    : by-support 2 2 ≡ 1        -- D₂
support-2-debut    = refl

-- support 3 debuts at rung 3 with D₃ = 2 (the two 3-cycles).
support-3-absent-2 : by-support 2 3 ≡ 0
support-3-absent-2 = refl
support-3-debut    : by-support 3 3 ≡ 2        -- D₃
support-3-debut    = refl

-- support 4 debuts at rung 4 with D₄ = 9 (all derangements of 4 points).
support-4-absent-3 : by-support 3 4 ≡ 0
support-4-absent-3 = refl
support-4-debut    : by-support 4 4 ≡ 9        -- D₄
support-4-debut    = refl

------------------------------------------------------------------------
-- 4. Support is COARSER than cycle type: the rung-4 support-4 debut
--    (9 derangements) splits into involutions (the 3 double-transpositions
--    = gauge V₄ minus id) and the rest (6 four-cycles). moved-count alone
--    cannot tell a 4-cycle from a (2,2) — both have support 4 — so this
--    split needs the involution predicate (σ² = id), not just support.
------------------------------------------------------------------------

-- support-4 involutions = double-transpositions = 3.
support-4-involutions : ℕ
support-4-involutions =
  lengthL (filterL (λ σ → ⌊ moved-count σ ≟ℕ 4 ⌋ ∧ is-involution σ) (perms 4))

-- support-4 non-involutions = four-cycles = 6.
support-4-fourcycles : ℕ
support-4-fourcycles =
  lengthL (filterL (λ σ → ⌊ moved-count σ ≟ℕ 4 ⌋ ∧ not (is-involution σ)) (perms 4))

support-4-split-invol : support-4-involutions ≡ 3
support-4-split-invol = refl
support-4-split-four  : support-4-fourcycles ≡ 6
support-4-split-four  = refl

-- and they reconcile to the full support-4 debut D₄ = 9.
support-4-reconcile : support-4-involutions + support-4-fourcycles ≡ by-support 4 4
support-4-reconcile = refl
