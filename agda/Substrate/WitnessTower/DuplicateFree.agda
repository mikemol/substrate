------------------------------------------------------------------------
-- Substrate.WitnessTower.DuplicateFree
--
-- Brick 2: perms n is DUPLICATE-FREE. With brick 1 (sound) and brick 3
-- (complete) this upgrades "perms n is exactly Sₙ as a set" to "perms n
-- lists each permutation exactly once" — so |Sₙ| = length (perms n) = n!,
-- and the list index gives a bijection Fin (n!) ≅ Sₙ.
--
-- Crux: insert-at is injective in BOTH arguments (the head recovers p, the
-- map recovers σ via punchIn-injective). So the construction's children are
-- all distinct and the blocks for distinct smaller permutations are
-- disjoint — NoDup is preserved through map and concatMap.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.DuplicateFree where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Sucinjective
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; cong₂; sym; subst; trans)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂; [_,_])
open import Substrate.Foundation.Fin.Punctured using (punchIn)

open import Substrate.WitnessTower.Enumerate
  using (Perm; perms; insert-at; mapL; concatMapL; all-positions)
open import Substrate.WitnessTower.IsPermutation using (punchIn-injective)
open import Substrate.WitnessTower.Complete using (_∈_; here; there)

------------------------------------------------------------------------
-- 0. Vec ∷-injectivity (private upstream) + map injective.
------------------------------------------------------------------------

∷-inj-head : {A : Set} {n : ℕ} {x y : A} {v w : Vec A n} → (x ∷ v) ≡ (y ∷ w) → x ≡ y
∷-inj-head refl = refl

∷-inj-tail : {A : Set} {n : ℕ} {x y : A} {v w : Vec A n} → (x ∷ v) ≡ (y ∷ w) → v ≡ w
∷-inj-tail refl = refl

map-injective :
  {A B : Set} {n : ℕ} (f : A → B) → (∀ {x y} → f x ≡ f y → x ≡ y) →
  {v w : Vec A n} → map f v ≡ map f w → v ≡ w
map-injective f finj {[]}    {[]}    _  = refl
map-injective f finj {x ∷ v} {y ∷ w} eq =
  cong₂ _∷_ (finj (∷-inj-head eq)) (map-injective f finj (∷-inj-tail eq))

------------------------------------------------------------------------
-- 1. insert-at injective in both arguments.
------------------------------------------------------------------------

insert-at-injˡ :
  {n : ℕ} {p q : Fin (suc n)} {σ τ : Perm n} →
  insert-at p σ ≡ insert-at q τ → p ≡ q
insert-at-injˡ eq = ∷-inj-head eq

insert-at-inj :
  {n : ℕ} {p q : Fin (suc n)} {σ τ : Perm n} →
  insert-at p σ ≡ insert-at q τ → (p ≡ q) × (σ ≡ τ)
insert-at-inj {p = p} eq with insert-at-injˡ eq
... | refl = refl , map-injective (punchIn p) (punchIn-injective p) (∷-inj-tail eq)

------------------------------------------------------------------------
-- 2. NoDup + the membership lemmas it needs.
------------------------------------------------------------------------

data NoDup {A : Set} : List A → Set where
  []  : NoDup []
  _∷_ : {x : A} {xs : List A} → ¬ (x ∈ xs) → NoDup xs → NoDup (x ∷ xs)

∈-++-split : {A : Set} (xs : List A) {ys : List A} {z : A} →
             z ∈ (xs ++ ys) → (z ∈ xs) ⊎ (z ∈ ys)
∈-++-split []       p         = inj₂ p
∈-++-split (x ∷ xs) here      = inj₁ here
∈-++-split (x ∷ xs) (there p) with ∈-++-split xs p
... | inj₁ q = inj₁ (there q)
... | inj₂ q = inj₂ q

NoDup-++ :
  {A : Set} (xs ys : List A) → NoDup xs → NoDup ys →
  ({z : A} → z ∈ xs → z ∈ ys → ⊥) → NoDup (xs ++ ys)
NoDup-++ []       ys _              ndy _    = ndy
NoDup-++ (x ∷ xs) ys (x∉xs ∷ ndxs) ndy disj =
  (λ x∈ → [ x∉xs , (λ x∈ys → disj here x∈ys) ] (∈-++-split xs x∈)) ∷
  NoDup-++ xs ys ndxs ndy (λ z∈xs z∈ys → disj (there z∈xs) z∈ys)

-- map membership inverse, existential form (avoids unifying f y =? f x).
∈-mapL-inv :
  {A B : Set} (f : A → B) {z : B} {xs : List A} →
  z ∈ mapL f xs → Σ A (λ y → (z ≡ f y) × (y ∈ xs))
∈-mapL-inv f {xs = x ∷ xs} here      = x , refl , here
∈-mapL-inv f {xs = x ∷ xs} (there p) with ∈-mapL-inv f p
... | y , z≡fy , y∈xs = y , z≡fy , there y∈xs

NoDup-mapL :
  {A B : Set} (f : A → B) → (∀ {x y} → f x ≡ f y → x ≡ y) →
  {xs : List A} → NoDup xs → NoDup (mapL f xs)
NoDup-mapL f finj []           = []
NoDup-mapL f finj (x∉xs ∷ nd)  = (λ fx∈ → x∉xs (recover fx∈)) ∷ NoDup-mapL f finj nd
  where
    recover : {x : _} {xs : _} → f x ∈ mapL f xs → x ∈ xs
    recover {x} fx∈ with ∈-mapL-inv f fx∈
    ... | y , fx≡fy , y∈xs = subst (_∈ _) (sym (finj fx≡fy)) y∈xs

------------------------------------------------------------------------
-- 3. concatMap membership inverse + NoDup of concatMap.
------------------------------------------------------------------------

∈-concatMapL-inv :
  {A B : Set} (g : A → List B) (xs : List A) {z : B} →
  z ∈ concatMapL g xs → Σ A (λ x → (x ∈ xs) × (z ∈ g x))
∈-concatMapL-inv g (x ∷ xs) {z} z∈ with ∈-++-split (g x) z∈
... | inj₁ z∈gx  = x , here , z∈gx
... | inj₂ z∈rest with ∈-concatMapL-inv g xs z∈rest
...   | x' , x'∈xs , z∈gx' = x' , there x'∈xs , z∈gx'

NoDup-concatMapL :
  {A B : Set} (g : A → List B) (xs : List A) →
  NoDup xs → ((x : A) → NoDup (g x)) →
  ({x x' : A} {z : B} → z ∈ g x → z ∈ g x' → x ≡ x') →
  NoDup (concatMapL g xs)
NoDup-concatMapL g []       _              _    _      = []
NoDup-concatMapL g (x ∷ xs) (x∉xs ∷ ndxs) ndg  ident =
  NoDup-++ (g x) (concatMapL g xs) (ndg x)
    (NoDup-concatMapL g xs ndxs ndg ident)
    (λ {z} z∈gx z∈rest →
      let (x' , x'∈xs , z∈gx') = ∈-concatMapL-inv g xs z∈rest
      in x∉xs (subst (_∈ xs) (sym (ident z∈gx z∈gx')) x'∈xs))

------------------------------------------------------------------------
-- 4. perms is duplicate-free.
------------------------------------------------------------------------

all-positions-nodup : (n : ℕ) → NoDup (all-positions n)
all-positions-nodup zero    = []
all-positions-nodup (suc n) = zero∉ ∷ NoDup-mapL suc fin-suc-injective (all-positions-nodup n)
  where
    -- zero is not in mapL suc (...) — suc is never zero.
    zero∉ : ¬ (zero ∈ mapL suc (all-positions n))
    zero∉ z∈ with ∈-mapL-inv suc z∈
    ... | y , () , _

perms-nodup : (n : ℕ) → NoDup (perms n)
perms-nodup zero    = (λ ()) ∷ []
perms-nodup (suc n) =
  NoDup-concatMapL g (perms n) (perms-nodup n) block-nodup blocks-identify
  where
    g : Perm n → List (Perm (suc n))
    g τ = mapL (λ q → insert-at q τ) (all-positions (suc n))
    -- each block is NoDup: insert-at · τ is injective in the position.
    block-nodup : (τ : Perm n) → NoDup (g τ)
    block-nodup τ =
      NoDup-mapL (λ q → insert-at q τ)
                 (λ {q}{q'} eq → insert-at-injˡ eq)
                 (all-positions-nodup (suc n))
    -- a child identifies its source τ: insert-at q τ ≡ insert-at q' τ' ⟹ τ ≡ τ'.
    blocks-identify : {τ τ' : Perm n} {z : Perm (suc n)} →
                      z ∈ g τ → z ∈ g τ' → τ ≡ τ'
    blocks-identify {τ} {τ'} z∈ z∈'
      with ∈-mapL-inv (λ q → insert-at q τ) z∈ | ∈-mapL-inv (λ q → insert-at q τ') z∈'
    ... | _ , z≡ , _ | _ , z≡' , _ with insert-at-inj (trans (sym z≡) z≡')
    ...   | _ , τ≡τ' = τ≡τ'
