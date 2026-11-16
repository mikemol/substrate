------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.WordsLength
--
-- Defines: words-length
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.WordsLength where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Pow
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.List
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.AllPositions
open import Substrate.WitnessTower.Enumerate.LenMap
open import Substrate.WitnessTower.Enumerate.LengthAllPositions
open import Substrate.WitnessTower.Enumerate.LengthConcatMapLConst
open import Substrate.WitnessTower.Enumerate.Words
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



-- |words n k| = nᵏ, by induction on k.
words-length : (n k : ℕ) → lengthL (words n k) ≡ n ^ k
words-length n zero    = refl
words-length n (suc k) =
  trans (length-concatMapL-const n
           (λ w → mapL (λ s → s ∷ w) (all-positions n))
           (words n k)
           (λ w → trans (len-map (λ s → s ∷ w) (all-positions n)) (length-all-positions n)))
        (trans (cong (λ z → z * n) (words-length n k))
               (*-comm (n ^ k) n))
