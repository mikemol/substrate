------------------------------------------------------------------------
-- Substrate.Foundation.Vec
--
-- Substrate-native length-indexed vectors. Phase 2: native datatype
-- + the standard operations (replicate / lookup / zipWith / map /
-- _++_ / head / tail / foldr / foldl / reverse / length).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)

------------------------------------------------------------------------
-- The Vec datatype.
------------------------------------------------------------------------

infixr 5 _∷_

data Vec (A : Set) : ℕ → Set where
  []  : Vec A zero
  _∷_ : {n : ℕ} → A → Vec A n → Vec A (suc n)

------------------------------------------------------------------------
-- replicate, lookup, map, zipWith, _++_, head, tail.
------------------------------------------------------------------------

replicate : {A : Set} (n : ℕ) → A → Vec A n
replicate zero    _ = []
replicate (suc n) x = x ∷ replicate n x

lookup : {A : Set} {n : ℕ} → Vec A n → Fin n → A
lookup (x ∷ _)  zero    = x
lookup (_ ∷ xs) (suc i) = lookup xs i

map : {A B : Set} {n : ℕ} → (A → B) → Vec A n → Vec B n
map _ []       = []
map f (x ∷ xs) = f x ∷ map f xs

zipWith : {A B C : Set} {n : ℕ} →
          (A → B → C) → Vec A n → Vec B n → Vec C n
zipWith _ []       []       = []
zipWith f (x ∷ xs) (y ∷ ys) = f x y ∷ zipWith f xs ys

head : {A : Set} {n : ℕ} → Vec A (suc n) → A
head (x ∷ _) = x

tail : {A : Set} {n : ℕ} → Vec A (suc n) → Vec A n
tail (_ ∷ xs) = xs

infixr 5 _++_

_++_ : {A : Set} {m n : ℕ} → Vec A m → Vec A n → Vec A (m + n)
[]       ++ ys = ys
(x ∷ xs) ++ ys = x ∷ (xs ++ ys)

foldr : {A : Set} {n : ℕ} (B : ℕ → Set) →
        ({k : ℕ} → A → B k → B (suc k)) → B zero → Vec A n → B n
foldr _ _ z []       = z
foldr B f z (x ∷ xs) = f x (foldr B f z xs)

foldl : {A : Set} {n : ℕ} (B : ℕ → Set) →
        ({k : ℕ} → B k → A → B (suc k)) → B zero → Vec A n → B n
foldl _ _ z []       = z
foldl B f z (x ∷ xs) = foldl (λ k → B (suc k)) f (f z x) xs

length : {A : Set} {n : ℕ} → Vec A n → ℕ
length {n = n} _ = n

-- `reverse` requires `n + 0 ≡ n` / `n + suc m ≡ suc (n + m)` index
-- transports not yet in scope at this slice; reverse stays in
-- Phase-2B's NatProperties-aware Foundation.Vec.Properties.
