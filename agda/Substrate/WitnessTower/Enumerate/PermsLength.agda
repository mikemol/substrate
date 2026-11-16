------------------------------------------------------------------------
-- Substrate.WitnessTower.Enumerate.PermsLength
--
-- Defines: perms-length
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.WitnessTower.Enumerate; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Enumerate.PermsLength where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec
open import Substrate.Foundation.List
open import Substrate.Foundation.Nat.Properties.Mul.TimesComm
open import Substrate.Foundation.Fin.Punctured
open import Substrate.WitnessTower.Enumerate.MapL
open import Substrate.WitnessTower.Enumerate.LengthL
open import Substrate.WitnessTower.Enumerate.InsertAt
open import Substrate.WitnessTower.Enumerate.AllPositions
open import Substrate.WitnessTower.Enumerate.Perms
open import Substrate.WitnessTower.Enumerate.Factorial
open import Substrate.WitnessTower.Enumerate.LenMap
open import Substrate.WitnessTower.Enumerate.LengthAllPositions
open import Substrate.WitnessTower.Enumerate.LengthConcatMapLConst
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans



-- THE GLUE, proved in general (not just spot-checked): |perms n| = n!.
-- |perms (suc n)| = |perms n| · (n+1) because each smaller perm spawns
-- exactly (n+1) children (one per insertion position), and n! · (n+1) =
-- (n+1)! by *-comm.
perms-length : (n : ℕ) → lengthL (perms n) ≡ factorial n
perms-length zero    = refl
perms-length (suc n) =
  trans (length-concatMapL-const (suc n)
           (λ σ → mapL (λ p → insert-at p σ) (all-positions (suc n)))
           (perms n)
           (λ σ → trans (len-map (λ p → insert-at p σ) (all-positions (suc n)))
                        (length-all-positions (suc n))))
        (trans (cong (_* suc n) (perms-length n))
               (*-comm (factorial n) (suc n)))
