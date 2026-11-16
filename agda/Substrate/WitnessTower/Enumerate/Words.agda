------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.Words
--
-- Defines: words
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.Words where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.ConcatMapL
open import Substrate.WitnessTower.Enumerate.AllPositions
open import Substrate.WitnessTower.Enumerate.Perms



------------------------------------------------------------------------
-- THE PRODUCT RULE: the number of length-k sequences (words) over an
-- n-symbol alphabet is nᵏ. Same witness-tower fold as perms, but every
-- rung prepends EVERY symbol to EVERY shorter word (no no-repeat
-- constraint), so the count multiplies by n each rung rather than by the
-- shrinking free-position count. `words`/`perms` share the concatMapL /
-- all-positions machinery above; only the multiplier differs.
------------------------------------------------------------------------

-- All length-k words over the n-symbol alphabet (Fin n): word₀ = the one
-- empty word; each rung prepends every symbol to every shorter word.
words : (n k : ℕ) → List (List (Fin n))
words n zero    = [] ∷ []
words n (suc k) = concatMapL (λ w → mapL (λ s → s ∷ w) (all-positions n)) (words n k)
