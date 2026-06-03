------------------------------------------------------------------------
-- Substrate.WitnessTower.Complete
--
-- Brick 3: the tower's enumeration is COMPLETE — every permutation of
-- Fin n appears in perms n. With brick 1 (every entry is a permutation)
-- this gives: membership in perms n ⟺ being a permutation. The enumeration
-- is exactly Sₙ as a set (modulo duplicates, removed in brick 2).
--
-- Proof: induction via the decomposition lemma. A permutation σ of
-- Fin (suc n) is insert-at p σ' with σ' a permutation of Fin n; by IH
-- σ' ∈ perms n, and p ∈ all-positions, so insert-at p σ' is one of the
-- enumerated children — hence σ ∈ perms (suc n).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Complete where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; [])
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; subst; sym)
open import Substrate.Foundation.Product using (Σ; _,_)

open import Substrate.WitnessTower.Enumerate
  using (Perm; perms; insert-at; mapL; concatMapL; all-positions)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Decompose using (decompose)

------------------------------------------------------------------------
-- 0. List membership + the structural lemmas.
------------------------------------------------------------------------

data _∈_ {A : Set} (x : A) : List A → Set where
  here  : {xs : List A} → x ∈ (x ∷ xs)
  there : {y : A} {xs : List A} → x ∈ xs → x ∈ (y ∷ xs)

∈-++ʳ : {A : Set} {x : A} (xs : List A) {ys : List A} → x ∈ ys → x ∈ (xs ++ ys)
∈-++ʳ []       p = p
∈-++ʳ (z ∷ xs) p = there (∈-++ʳ xs p)

∈-mapL : {A B : Set} {x : A} (f : A → B) {xs : List A} →
         x ∈ xs → f x ∈ mapL f xs
∈-mapL f here      = here
∈-mapL f (there p) = there (∈-mapL f p)

-- membership in a concatMap: if x ∈ xs and y ∈ g x then y ∈ concatMapL g xs.
∈-concatMapL :
  {A B : Set} {y : B} (g : A → List B) {xs : List A} {x : A} →
  x ∈ xs → y ∈ g x → y ∈ concatMapL g xs
∈-concatMapL g (here {xs})    yg = ∈-++ˡ (g _) yg
  where
    ∈-++ˡ : {A : Set} {x : A} (as : List A) {bs : List A} → x ∈ as → x ∈ (as ++ bs)
    ∈-++ˡ (a ∷ as) here      = here
    ∈-++ˡ (a ∷ as) (there p) = there (∈-++ˡ as p)
∈-concatMapL g (there {y = x'} p) yg = ∈-++ʳ (g x') (∈-concatMapL g p yg)

------------------------------------------------------------------------
-- 1. all-positions is complete: every position occurs.
------------------------------------------------------------------------

all-positions-complete : (n : ℕ) (p : Fin n) → p ∈ all-positions n
all-positions-complete (suc n) zero    = here
all-positions-complete (suc n) (suc p) = there (∈-mapL suc (all-positions-complete n p))

------------------------------------------------------------------------
-- 2. Completeness.
------------------------------------------------------------------------

-- the empty permutation is the only Perm 0, and it is enumerated.
perms-complete : (n : ℕ) (σ : Perm n) → IsPerm σ → σ ∈ perms n
perms-complete zero    []  _    = here
perms-complete (suc n) σ   perm with decompose σ perm
... | p , σ' , σ'-perm , σ≡ =
  subst (_∈ perms (suc n)) (sym σ≡) child-∈
  where
    -- insert-at p σ' is one of σ'’s children, and σ' ∈ perms n by IH.
    g : Perm n → List (Perm (suc n))
    g τ = mapL (λ q → insert-at q τ) (all-positions (suc n))
    insert-∈-g : insert-at p σ' ∈ g σ'
    insert-∈-g = ∈-mapL (λ q → insert-at q σ') (all-positions-complete (suc n) p)
    child-∈ : insert-at p σ' ∈ perms (suc n)
    child-∈ = ∈-concatMapL g (perms-complete n σ' σ'-perm) insert-∈-g
