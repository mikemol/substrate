------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.ListIso
--
-- SLICE 1: flatten ≅ List-div, made a theorem (was prose). The Grothendieck
-- flatten of the Vec append wedge product (Σ ℕ (Vec A), Product.flatten) IS the
-- free-monoid root List-div A. The total space Σ ℕ (Vec A) is a list (length +
-- contents), and `vecToList ∘ proj₂` is a WEDGE BRIDGE onto List-div:
-- "q copies of b ++ r" on the flattened product = List-div's recon verbatim.
--
-- This file gives the forward homomorphism as a Bridge (flatten → List-div) and
-- the List-retract round-trip (toList ∘ listToΣ ≡ id), so List-div is a retract
-- of the flattened product via vecToList. (The reverse round-trip — recovering
-- the Vec from the list — carries the length transport and is the heavier
-- remaining bit, noted not built; the Bridge is the substrate-idiomatic "maps
-- onto, respecting recon".)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.ListIso where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans; sym)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
import Substrate.Foundation.Vec as V
import Substrate.Foundation.List as L
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Algebra.Wedge.Bridge using (Bridge)
open import Substrate.Algebra.Wedge.Product using (vec-product; gpower; flatten)
open import Substrate.Algebra.List.Wedge using (List-div; lrepeat)

------------------------------------------------------------------------
-- 1. The forgetful Vec → List (drops the length index; no transport).
------------------------------------------------------------------------

vecToList : {A : Set} {n : ℕ} → V.Vec A n → L.List A
vecToList V.[]        = L.[]
vecToList (x V.∷ xs)  = x L.∷ vecToList xs

vecToList-++ : {A : Set} {m n : ℕ} (xs : V.Vec A m) (ys : V.Vec A n) →
               vecToList (xs V.++ ys) ≡ vecToList xs L.++ vecToList ys
vecToList-++ V.[]       ys = refl
vecToList-++ (x V.∷ xs) ys = cong (x L.∷_) (vecToList-++ xs ys)

-- vecToList preserves length — so the Vec's grade IS the List-quotient's length
-- (the count-as-grade bridge: flatten counts by `proj₁`, List-div by `length`).
vecToList-length : {A : Set} {n : ℕ} (v : V.Vec A n) → length (vecToList v) ≡ n
vecToList-length V.[]       = refl
vecToList-length (x V.∷ xs) = cong suc (vecToList-length xs)

-- the q-deep ∧-term (q copies appended) maps to lrepeat (q copies in List).
vecToList-gpower : {A : Set} {i : ℕ} (a : V.Vec A i) (q : ℕ) →
                   vecToList (gpower (vec-product A) a q) ≡ lrepeat q (vecToList a)
vecToList-gpower a zero    = refl
vecToList-gpower a (suc n) =
  trans (vecToList-++ a (gpower (vec-product _) a n))
        (cong (vecToList a L.++_) (vecToList-gpower a n))

------------------------------------------------------------------------
-- 2. THE BRIDGE: flatten (vec-product A) ↠ List-div A — vecToList respects the
--    wedge recon ("q copies of b ++ r"), and the empty word is preserved.
------------------------------------------------------------------------

flatten-vec→list : (A : Set) → Bridge (flatten (vec-product A)) (List-div A)
flatten-vec→list A = record
  { translate = λ p → vecToList (proj₂ p)
  ; respects  = λ q b r →
      trans (vecToList-++ (gpower (vec-product A) (proj₂ b) (proj₁ q)) (proj₂ r))
      (trans (cong (L._++ vecToList (proj₂ r)) (vecToList-gpower (proj₂ b) (proj₁ q)))
             (cong (λ n → lrepeat n (vecToList (proj₂ b)) L.++ vecToList (proj₂ r))
                   (sym (vecToList-length (proj₂ q)))))
  ; z-pres    = refl
  }

------------------------------------------------------------------------
-- 3. List-div is a RETRACT of the flattened product: listToΣ then vecToList is
--    the identity on lists (the contents survive the round-trip).
------------------------------------------------------------------------

listToΣ : {A : Set} → L.List A → Σ ℕ (V.Vec A)
listToΣ L.[]        = zero , V.[]
listToΣ (x L.∷ xs)  = suc (proj₁ (listToΣ xs)) , x V.∷ proj₂ (listToΣ xs)

toList∘listToΣ : {A : Set} (xs : L.List A) → vecToList (proj₂ (listToΣ xs)) ≡ xs
toList∘listToΣ L.[]        = refl
toList∘listToΣ (x L.∷ xs)  = cong (x L.∷_) (toList∘listToΣ xs)
