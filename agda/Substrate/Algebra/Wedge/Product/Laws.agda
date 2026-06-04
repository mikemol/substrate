------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Laws
--
-- THE ASSOCIATIVITY LAWS BELONG OVER THE GRADED PRODUCT (user). Since
-- (a ∧ b) ∧ c : C ((i+j)+k) and a ∧ (b ∧ c) : C (i+(j+k)) live at DIFFERENT
-- grades, associativity of the wedge product IS +-assoc on the grades,
-- transported: the associativity bracket and the grade are the same thing
-- (quote = quotient = grade, Product.agda), so the bracketing law is the grade
-- arithmetic. A GradedMonoid is a GradedProduct whose ∧ satisfies exactly these
-- grade-transported laws.
--
-- Vec is the worked instance: append-associativity carries the +-assoc subst,
-- the left unit is definitional ([] ++ a = a, since 0 + i = i), and the right
-- unit carries +-identityʳ.
--
-- RELATION TO Category.GradedMonoid: that record is the FLAT view of a graded
-- monoid — a single carrier M with degree : M → ℕ, ordinary (·-assoc) with NO
-- transport. This file is the FIBERED view — C : ℕ → Set, assoc carrying the
-- +-assoc subst. The two are bridged by Product.flatten (the Grothendieck
-- construction): flattening Σ ℕ C folds each transport into the Σ first
-- component, so the fibered ++-assoc below becomes the flat ·-assoc up there.
-- (We do NOT re-declare GradedMonoid — these are the laws; the flat packaging
-- already exists.) This file declares no data/record, so it is exempt from the
-- def/proof gate though it imports the ℕ addition properties.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Product.Laws where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-assoc; +-identityʳ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; _++_)
open import Substrate.Foundation.Eq using (_≡_; refl; subst; cong; trans)
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; C; u; _∧_; vec-product)

------------------------------------------------------------------------
-- 1. subst over Vec commutes with cons (a grade-lift through a head).
------------------------------------------------------------------------

subst-∷ : {A : Set} {m n : ℕ} (p : m ≡ n) (x : A) (w : Vec A m) →
          subst (Vec A) (cong suc p) (x ∷ w) ≡ x ∷ subst (Vec A) p w
subst-∷ refl x w = refl

------------------------------------------------------------------------
-- 2. Graded append laws: associativity = +-assoc transported; right unit =
--    +-identityʳ transported. (Left unit is definitional, below.)
------------------------------------------------------------------------

++-assoc : {A : Set} {i j k : ℕ} (xs : Vec A i) (ys : Vec A j) (zs : Vec A k) →
           subst (Vec A) (+-assoc i j k) ((xs ++ ys) ++ zs) ≡ xs ++ (ys ++ zs)
++-assoc []       ys zs = refl
++-assoc {i = suc i'} {j} {k} (x ∷ xs) ys zs =
  trans (subst-∷ (+-assoc i' j k) x ((xs ++ ys) ++ zs))
        (cong (x ∷_) (++-assoc xs ys zs))

++-identityʳ : {A : Set} {i : ℕ} (xs : Vec A i) →
               subst (Vec A) (+-identityʳ i) (xs ++ []) ≡ xs
++-identityʳ []                = refl
++-identityʳ {i = suc i'} (x ∷ xs) =
  trans (subst-∷ (+-identityʳ i') x (xs ++ []))
        (cong (x ∷_) (++-identityʳ xs))

------------------------------------------------------------------------
-- 3. The graded laws abstractly, for ANY GradedProduct (the home of the assoc
--    laws over the wedge product). A GradedProduct P satisfies the graded
--    monoid laws iff it provides these three; Vec (above) is the witness that
--    they are inhabited. The left unit is definitional (u ∧ a : C (0 + i) = C i).
------------------------------------------------------------------------

GradedAssoc : GradedProduct → Set
GradedAssoc P = {i j k : ℕ} (a : C P i) (b : C P j) (c : C P k) →
                subst (C P) (+-assoc i j k) (_∧_ P (_∧_ P a b) c) ≡ _∧_ P a (_∧_ P b c)

GradedUnitˡ : GradedProduct → Set
GradedUnitˡ P = {i : ℕ} (a : C P i) → _∧_ P (u P) a ≡ a

GradedUnitʳ : GradedProduct → Set
GradedUnitʳ P = {i : ℕ} (a : C P i) →
                subst (C P) (+-identityʳ i) (_∧_ P a (u P)) ≡ a

------------------------------------------------------------------------
-- 4. Vec satisfies all three graded laws.
------------------------------------------------------------------------

vec-assoc : (A : Set) → GradedAssoc (vec-product A)
vec-assoc A = ++-assoc

vec-unitˡ : (A : Set) → GradedUnitˡ (vec-product A)
vec-unitˡ A a = refl          -- [] ++ a = a definitionally (0 + i = i)

vec-unitʳ : (A : Set) → GradedUnitʳ (vec-product A)
vec-unitʳ A = ++-identityʳ
