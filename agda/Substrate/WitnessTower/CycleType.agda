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

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_) renaming (_≟_ to _≟ℕ_; _<?_ to _<?ℕ_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Bool using (Bool; true; false; _∧_; if_then_else_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Vec.Properties using (≡-dec)

open import Substrate.WitnessTower.Enumerate using (Perm; perms; all-positions; lengthL)
open import Substrate.WitnessTower.FirstAppearance using (⌊_⌋; filterL)

------------------------------------------------------------------------
-- 1. Orbit length: the cycle length of the point i under σ (fuel n).
------------------------------------------------------------------------

orbit-len-aux : {n : ℕ} → ℕ → Perm n → Fin n → Fin n → ℕ → ℕ
orbit-len-aux zero    σ s c acc = acc
orbit-len-aux (suc f) σ s c acc =
  if ⌊ lookup σ c ≟ s ⌋ then suc acc
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
  if ⌊ lookup σ c ≟ s ⌋ then true
  else if ⌊ toℕ (lookup σ c) <?ℕ toℕ s ⌋ then false
  else orbit-min?-aux f σ s (lookup σ c)

orbit-min? : {n : ℕ} → Perm n → Fin n → Bool
orbit-min? {n} σ i = orbit-min?-aux n σ i i

------------------------------------------------------------------------
-- 3. Cycle counts and the cycle-type vector (the partition λ).
------------------------------------------------------------------------

-- number of cycles of length ℓ: representatives with orbit-length ℓ.
cycles-of-len : {n : ℕ} → Perm n → ℕ → ℕ
cycles-of-len {n} σ ℓ =
  lengthL (filterL (λ i → orbit-min? σ i ∧ ⌊ orbit-len σ i ≟ℕ ℓ ⌋)
                   (all-positions n))

-- cycle-type σ : Vec ℕ n, position j = #cycles of length (j+1).
cycle-type : {n : ℕ} → Perm n → Vec ℕ n
cycle-type {n} σ = tabulate (λ j → cycles-of-len σ (suc (toℕ j)))

------------------------------------------------------------------------
-- 4. Census by conjugacy class: count permutations of rung n whose cycle
--    type equals a given vector.
------------------------------------------------------------------------

_≟ᵛ_ : {n : ℕ} (xs ys : Vec ℕ n) → _
_≟ᵛ_ = ≡-dec _≟ℕ_

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
census-support4-split : count-class ty-double + count-class ty-4cyc ≡ 9
census-support4-split = refl
