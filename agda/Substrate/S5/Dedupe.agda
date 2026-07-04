{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.S5.Dedupe — the shared observed-state deduplicator + its
-- length-monotonicity proof, LIFTED (⟡dedup) out of S5TwoFuel and
-- S5TwoFuelFix, which had byte-identical copies (jea_pysim clusters
-- 93–99). The two fuel-metered runners now DERIVE from this one parent
-- (the "find the common structure, recursively" reflex): the calculation
-- fuel = length ∘ dedupe, and `dedupe-≤` is the L3 (calc ≤ trav) witness.
-- `≤-up` was itself a re-derivation of Foundation's ≤-suc-r — deduped here.
------------------------------------------------------------------------

module Substrate.S5.Dedupe where

open import Substrate.Foundation.Bool                 using (Bool; true; false)
open import Substrate.Foundation.Nat                  using (ℕ; suc; _≤_; z≤n; s≤s)
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r)
open import Substrate.Foundation.List                 using (List; []; _∷_)
open import Substrate.Foundation.List.Length          using (length)

-- dedupe over an arbitrary decidable-ish equality eqb (abstract carrier A).
module Dedupe {A : Set} (eqb : A → A → Bool) where
  member : A → List A → Bool
  member a []       = false
  member a (x ∷ xs) = memb (eqb a x)
    where memb : Bool → Bool
          memb true  = true
          memb false = member a xs
  go     : List A → List A → List A
  branch : List A → A → List A → Bool → List A
  go seen []       = []
  go seen (x ∷ xs) = branch seen x xs (member x seen)
  branch seen x xs true  = go seen xs
  branch seen x xs false = x ∷ go (x ∷ seen) xs
  dedupe : List A → List A
  dedupe = go []
  go-≤     : (seen xs : List A) → length (go seen xs) ≤ length xs
  branch-≤ : (seen : List A) (x : A) (xs : List A) (b : Bool)
           → length (branch seen x xs b) ≤ suc (length xs)
  go-≤ seen []       = z≤n
  go-≤ seen (x ∷ xs) = branch-≤ seen x xs (member x seen)
  branch-≤ seen x xs true  = ≤-suc-r (go-≤ seen xs)
  branch-≤ seen x xs false = s≤s (go-≤ (x ∷ seen) xs)
  dedupe-≤ : (xs : List A) → length (dedupe xs) ≤ length xs
  dedupe-≤ = go-≤ []
