------------------------------------------------------------------------
-- THE TRIM — structural recursion LSB-first: trim the tail, put the head
-- back. Three clauses, each discharging its certificate by one `cong`
-- through the Horner step.
-- Context: Substrate/Algebra/Wedge/BinTrim/README.md
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BinTrim.Trim where

open import Substrate.Foundation.Bool.Bool
open import Substrate.Algebra.Wedge.Bin.Value
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Bool.BoolToNat
open import Substrate.Foundation.Vec
open import Substrate.Algebra.Wedge.Bin.Carrier
open import Substrate.Algebra.Wedge.BinTrim.Trimmed
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.WitnessTower.SnVersusTwoPow

trim : {n : ℕ} (b : Bin n) → Trimmed b
trim []                             = is-zero refl
trim (b ∷ bs) with trim bs
-- tail zero, head zero ⇒ the numeral is zero.
trim (false ∷ bs) | is-zero h       = is-zero (cong (λ z → z ℕ+ z) h)
-- tail zero, head one ⇒ the exact width is 1.
trim (true  ∷ bs) | is-zero h       =
  is-tight zero (true ∷ []) (s≤s z≤n) refl
           (cong (λ z → boolToℕ true ℕ+ (z ℕ+ z)) (sym h))
-- tail tight at suc e ⇒ the numeral is tight at suc (suc e); the top bit
-- IS the tail's, definitionally (see Msb).
trim (b ∷ bs) | is-tight e t fits hm hv =
  is-tight (suc e) (b ∷ t) (s≤s fits) hm
           (cong (λ z → boolToℕ b ℕ+ (z ℕ+ z)) hv)
