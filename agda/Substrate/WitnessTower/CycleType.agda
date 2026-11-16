------------------------------------------------------------------------
-- Substrate.WitnessTower.CycleType
--
-- The finer grading lego: the full CYCLE TYPE (partition λ) of a
-- permutation, computed by tracing orbits over the iterated enumeration —
-- not just the support sum. This resolves what moved-count cannot: a
-- 4-cycle (4) and a double-transposition (2,2) BOTH have support 4, but
-- different cycle type. With cycle type the whole conjugacy-class census of
-- each rung drops out, and (next module) the 4 Klein-fours split by the
-- cycle types of their elements.
--
-- Representation. cycle-type σ : Vec ℕ n, position j = the number of
-- cycles of length (j+1). This IS the partition λ of n (Σ (j+1)·tⱼ = n).
-- Orbits are traced with fuel n (an orbit has ≤ n points), counting each
-- cycle once at its least element (orbit-min?).
--
--   n = 4 conjugacy classes and their cycle-type vectors [t₁,t₂,t₃,t₄]:
--     identity            (1,1,1,1)   [4,0,0,0]   count 1
--     transposition       (2,1,1)     [2,1,0,0]   count 6
--     double-transp.      (2,2)       [0,2,0,0]   count 3
--     3-cycle             (3,1)       [1,0,1,0]   count 8
--     4-cycle             (4)         [0,0,0,1]   count 6   (1+6+3+8+6=24)
--
-- All five counts are refl over the enumeration below.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.CycleType where

-- ⚑ WAS `open import ...Foundation.Nat using (…) renaming (_≟_ to _≟ℕ_)` — a
-- retired barrel AND a banned renaming, in one statement.  The `_≟ℕ_` alias
-- names nothing tree-wide; the ℕ decidable equality is `Nat.Dec._≟_` and the Fin
-- one is now `Fin.Op._≟ᶠ_`, so the two are separable without an alias.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Dec
-- ⚑ `<?ℕ` IS THE SECOND ALIAS FROM THE SAME DISSOLVED STATEMENT.  One
-- `renaming (…)` clause can carry several, so clearing one leaves the rest —
-- `fix_notinscope` REFUSED this (`no definer in index`) rather than guessing,
-- which is correct: the alias names nothing, and only history says what it meant.
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Bool.And
open import Substrate.Foundation.Bool.Bool
open import Substrate.Foundation.Bool.IfThenElse
open import Substrate.Foundation.Vec.Properties.EqDec

open import Substrate.WitnessTower.Enumerate using (Perm; perms; all-positions; lengthL)
open import Substrate.WitnessTower.FirstAppearance using (⌊_⌋; filterL)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.WellFounded

------------------------------------------------------------------------
-- 1. Orbit length: the cycle length of the point i under σ (fuel n).
------------------------------------------------------------------------

orbit-len-aux : {n : ℕ} → ℕ → Perm n → Fin n → Fin n → ℕ → ℕ
orbit-len-aux zero    σ s c acc = acc
orbit-len-aux (suc f) σ s c acc =
  if ⌊ lookup σ c ≟ᶠ s ⌋ then suc acc
  else orbit-len-aux f σ s (lookup σ c) (suc acc)

orbit-len : {n : ℕ} → Perm n → Fin n → ℕ
orbit-len {n} σ i = orbit-len-aux n σ i i zero

------------------------------------------------------------------------
-- 2. Orbit-min?: is i the LEAST element of its orbit (the cycle's
--    canonical representative)? Walk the orbit; fail if a smaller point
--    appears before returning. (fuel n.)
------------------------------------------------------------------------

orbit-min?-aux : {n : ℕ} → ℕ → Perm n → Fin n → Fin n → Bool
orbit-min?-aux zero    σ s c = true
orbit-min?-aux (suc f) σ s c =
  if ⌊ lookup σ c ≟ᶠ s ⌋ then true
  else if ⌊ toℕ (lookup σ c) <? toℕ s ⌋ then false
  else orbit-min?-aux f σ s (lookup σ c)

orbit-min? : {n : ℕ} → Perm n → Fin n → Bool
orbit-min? {n} σ i = orbit-min?-aux n σ i i

------------------------------------------------------------------------
-- 3. Cycle counts and the cycle-type vector (the partition λ).
------------------------------------------------------------------------

-- number of cycles of length ℓ: representatives with orbit-length ℓ.
cycles-of-len : {n : ℕ} → Perm n → ℕ → ℕ
cycles-of-len {n} σ ℓ =
  lengthL (filterL (λ i → orbit-min? σ i ∧ ⌊ orbit-len σ i ≟ ℓ ⌋)
                   (all-positions n))

-- cycle-type σ : Vec ℕ n, position j = #cycles of length (j+1).
cycle-type : {n : ℕ} → Perm n → Vec ℕ n
cycle-type {n} σ = tabulate (λ j → cycles-of-len σ (suc (toℕ j)))

------------------------------------------------------------------------
-- 4. Census by conjugacy class: count permutations of rung n whose cycle
--    type equals a given vector.
------------------------------------------------------------------------

_≟ᵛ_ : {n : ℕ} (xs ys : Vec ℕ n) → _
-- ⚑ THE ALIAS IN ITS *DECLARED* SPELLING, passed as an argument — a third
-- surface for one dissolved `renaming`.  It fails as `[NoParseForApplication]`
-- rather than `[NotInScope]`, so `fix_noparse` saw it and correctly REFUSED: no
-- operator is displaced here, the name simply never existed.  `Vec ℕ n` needs
-- the ℕ element decider.
_≟ᵛ_ = ≡-dec _≟_

count-class : {n : ℕ} → Vec ℕ n → ℕ
count-class {n} t = lengthL (filterL (λ σ → ⌊ cycle-type σ ≟ᵛ t ⌋) (perms n))

------------------------------------------------------------------------
-- 5. The full S₄ conjugacy-class census — every count refl over the
--    enumeration. (4) and (2,2) now distinguished (support alone cannot).
------------------------------------------------------------------------

-- cycle-type vectors for the 5 classes of S₄ (length 4).
ty-id ty-transp ty-double ty-3cyc ty-4cyc : Vec ℕ 4
ty-id     = 4 ∷ 0 ∷ 0 ∷ 0 ∷ []       -- (1,1,1,1)
ty-transp = 2 ∷ 1 ∷ 0 ∷ 0 ∷ []       -- (2,1,1)
ty-double = 0 ∷ 2 ∷ 0 ∷ 0 ∷ []       -- (2,2)
ty-3cyc   = 1 ∷ 0 ∷ 1 ∷ 0 ∷ []       -- (3,1)
ty-4cyc   = 0 ∷ 0 ∷ 0 ∷ 1 ∷ []       -- (4)

census-id     : count-class ty-id     ≡ 1
census-id     = refl
census-transp : count-class ty-transp ≡ 6
census-transp = refl
census-double : count-class ty-double ≡ 3
census-double = refl
census-3cyc   : count-class ty-3cyc   ≡ 8
census-3cyc   = refl
census-4cyc   : count-class ty-4cyc   ≡ 6
census-4cyc   = refl

-- the boundary moved-count could not cross: support 4 = (2,2) ⊎ (4),
-- two DISTINCT classes (3 + 6), here separated by cycle type.
census-support4-split : count-class ty-double ℕ+ count-class ty-4cyc ≡ 9
census-support4-split = refl
