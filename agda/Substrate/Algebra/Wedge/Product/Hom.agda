------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Hom
--
-- SLICE 4: graded homomorphisms — the bridge layer between graded products, the
-- graded analog of Algebra.Wedge.Bridge. A GradedHom P Q is a grade-preserving
-- map respecting the unit and the wedge product. With identity and composition,
-- GradedProduct + GradedHom is a category; this is how graded roots
-- interconnect (the graded form of "raise the bridge-degree").
--
--   * id-hom / comp-hom — the category structure.
--   * vec-map-hom — every A → B lifts to GradedHom (vec-product A) (vec-product
--     B) (Vec functoriality: map distributes over append).
--   * flatten-map — flatten is FUNCTORIAL: a GradedHom induces a map on the
--     flattened carriers respecting the flat product (the grade is carried, the
--     residue never dropped).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.Hom where

open import Substrate.Foundation.Nat using (ℕ; _+_)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; trans)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; _++_; map)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; C; u; _∧_; vec-product)

------------------------------------------------------------------------
-- 1. The graded homomorphism: grade-preserving, unit- and ∧-respecting.
------------------------------------------------------------------------

record GradedHom (P Q : GradedProduct) : Set where
  field
    map₀  : {n : ℕ} → C P n → C Q n
    map-u : map₀ (u P) ≡ u Q
    map-∧ : {i j : ℕ} (a : C P i) (b : C P j) →
            map₀ (_∧_ P a b) ≡ _∧_ Q (map₀ a) (map₀ b)

open GradedHom public

------------------------------------------------------------------------
-- 2. The category structure: identity and composition.
------------------------------------------------------------------------

id-hom : (P : GradedProduct) → GradedHom P P
id-hom P = record { map₀ = λ x → x ; map-u = refl ; map-∧ = λ a b → refl }

comp-hom : {P Q R : GradedProduct} → GradedHom Q R → GradedHom P Q → GradedHom P R
comp-hom g f = record
  { map₀  = λ x → map₀ g (map₀ f x)
  ; map-u = trans (cong (map₀ g) (map-u f)) (map-u g)
  ; map-∧ = λ a b → trans (cong (map₀ g) (map-∧ f a b))
                          (map-∧ g (map₀ f a) (map₀ f b))
  }

------------------------------------------------------------------------
-- 3. Vec is functorial: A → B lifts to a graded hom (map distributes over ++).
------------------------------------------------------------------------

vmap-++ : {A B : Set} (f : A → B) {m n : ℕ} (xs : Vec A m) (ys : Vec A n) →
          map f (xs ++ ys) ≡ map f xs ++ map f ys
vmap-++ f []       ys = refl
vmap-++ f (x ∷ xs) ys = cong (f x ∷_) (vmap-++ f xs ys)

vec-map-hom : {A B : Set} (f : A → B) → GradedHom (vec-product A) (vec-product B)
vec-map-hom f = record
  { map₀  = map f
  ; map-u = refl                       -- map f [] = []
  ; map-∧ = λ a b → vmap-++ f a b
  }

------------------------------------------------------------------------
-- 4. flatten is functorial: a GradedHom induces a map on the flattened
--    carriers respecting the flat product. The grade is carried, never dropped.
------------------------------------------------------------------------

flatten-map : {P Q : GradedProduct} → GradedHom P Q → Σ ℕ (C P) → Σ ℕ (C Q)
flatten-map h (n , x) = n , map₀ h x

flatten-map-· : {P Q : GradedProduct} (h : GradedHom P Q)
                {i j : ℕ} (a : C P i) (b : C P j) →
                flatten-map h (i + j , _∧_ P a b)
                  ≡ (i + j , _∧_ Q (map₀ h a) (map₀ h b))
flatten-map-· h a b = cong (_ ,_) (map-∧ h a b)
