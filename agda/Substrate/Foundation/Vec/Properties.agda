------------------------------------------------------------------------
-- Substrate.Foundation.Vec.Properties
--
-- Substrate-native Vec properties. Phase 2: decidable equality on Vec.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Foundation.Vec.Properties where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; sym; trans)
open import Substrate.Foundation.Negation using (¬_; Dec; yes; no)
open import Substrate.Foundation.Level using (Level)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- ∷ is injective in both arguments.
------------------------------------------------------------------------

private
  ∷-injective-head : {A : Set} {n : ℕ} {x y : A} {xs ys : Vec A n} →
                     (x ∷ xs) ≡ (y ∷ ys) → x ≡ y
  ∷-injective-head refl = refl

  ∷-injective-tail : {A : Set} {n : ℕ} {x y : A} {xs ys : Vec A n} →
                     (x ∷ xs) ≡ (y ∷ ys) → xs ≡ ys
  ∷-injective-tail refl = refl

------------------------------------------------------------------------
-- ≡-dec: lift decidable equality on elements to decidable equality on
-- length-indexed vectors.
------------------------------------------------------------------------

≡-dec :
  {A : Set} {n : ℕ} →
  ((x y : A) → Dec (x ≡ y)) →
  (xs ys : Vec A n) → Dec (xs ≡ ys)
≡-dec _≟_ []       []       = yes refl
≡-dec _≟_ (x ∷ xs) (y ∷ ys) with x ≟ y | ≡-dec _≟_ xs ys
... | yes refl | yes refl = yes refl
... | no  ¬x≡y | _        = no λ p → ¬x≡y (∷-injective-head p)
... | _        | no  ¬eq  = no λ p → ¬eq (∷-injective-tail p)

------------------------------------------------------------------------
-- tabulate / lookup round-trip lemmas.
--
-- lookup∘tabulate : lookup (tabulate f) i ≡ f i
-- tabulate∘lookup : tabulate (lookup xs) ≡ xs
------------------------------------------------------------------------

lookup∘tabulate :
  {A : Set ℓ} {n : ℕ}
  (f : Fin n → A) (i : Fin n) →
  lookup (tabulate f) i ≡ f i
lookup∘tabulate {n = suc _} f zero    = refl
lookup∘tabulate {n = suc _} f (suc i) = lookup∘tabulate (λ j → f (suc j)) i

tabulate∘lookup :
  {A : Set ℓ} {n : ℕ}
  (xs : Vec A n) → tabulate (lookup xs) ≡ xs
tabulate∘lookup []       = refl
tabulate∘lookup (x ∷ xs) = cong (x ∷_) (tabulate∘lookup xs)

------------------------------------------------------------------------
-- tabulate-cong + vec-ext: pointwise equality ⟹ vector equality.
--
-- The generic Vec extensionality, derived from the two round-trips
-- above (no funext, no K): if two vectors agree at every index they
-- are equal. Subsumes F₂'s ≡-from-lookup at any element type, so it
-- serves both the row level (Vec of rows) and the entry level.
------------------------------------------------------------------------

tabulate-cong :
  {A : Set ℓ} {n : ℕ}
  (f g : Fin n → A) → ((i : Fin n) → f i ≡ g i) → tabulate f ≡ tabulate g
tabulate-cong {n = zero}  f g p = refl
tabulate-cong {n = suc _} f g p =
  cong₂ _∷_ (p zero) (tabulate-cong (λ i → f (suc i)) (λ i → g (suc i)) (λ i → p (suc i)))

vec-ext :
  {A : Set ℓ} {n : ℕ}
  (u v : Vec A n) → ((i : Fin n) → lookup u i ≡ lookup v i) → u ≡ v
vec-ext u v p =
  trans (sym (tabulate∘lookup u))
        (trans (tabulate-cong (lookup u) (lookup v) p) (tabulate∘lookup v))
