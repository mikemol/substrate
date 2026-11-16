------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Product.Laws
--
-- THE ASSOCIATIVITY LAWS BELONG OVER THE GRADED PRODUCT (user). Since
-- (a ∧ b) ∧ c : C ((i+j)+k) and a ∧ (b ∧ c) : C (i+(j+k)) live at DIFFERENT
-- grades, associativity of the wedge product IS +ℕ-assoc on the grades,
-- transported: the associativity bracket and the grade are the same thing
-- (quote = quotient = grade, Product.agda), so the bracketing law is the grade
-- arithmetic. A GradedMonoid is a GradedProduct whose ∧ satisfies exactly these
-- grade-transported laws.
--
-- Vec is the worked instance: append-associativity carries the +ℕ-assoc subst,
-- the left unit is definitional ([] ++ a = a, since 0 ℕ+ i = i), and the right
-- unit carries +-identityʳ.
--
-- RELATION TO Category.GradedMonoid: that record is the FLAT view of a graded
-- monoid — a single carrier M with degree : M → ℕ, ordinary (·-assoc) with NO
-- transport. This file is the FIBERED view — C : ℕ → Set, assoc carrying the
-- +ℕ-assoc subst. The two are bridged by Product.flatten (the Grothendieck
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

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Vec using (Vec; []; _∷_; _++_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; Σ-≡,≡→≡)
-- ⟡set1-paydown: GradedProduct's carrier family is now its param, so the old
-- `C P` projection becomes the (implicit) module param C threaded here.
open import Substrate.Algebra.Wedge.Product
  using (GradedProduct; u; _∧_; vec-product)
open import Substrate.Category.GradedMonoid using (GradedMonoid)
-- The law PREDICATES live in (proof-free) Product.LawTypes so law-bundling
-- records can import the field types without a proof dependency; re-exported.
open import Substrate.Algebra.Wedge.Product.LawTypes
  using (GradedAssoc; GradedUnitˡ; GradedUnitʳ)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Trans

------------------------------------------------------------------------
-- 1. subst over Vec commutes with cons (a grade-lift through a head).
------------------------------------------------------------------------

subst-∷ : {A : Set} {m n : ℕ} (p : m ≡ n) (x : A) (w : Vec A m) →
          subst (Vec A) (cong suc p) (x ∷ w) ≡ x ∷ subst (Vec A) p w
subst-∷ refl x w = refl

------------------------------------------------------------------------
-- 2. Graded append laws: associativity = +ℕ-assoc transported; right unit =
--    +ℕ-identityʳ transported. (Left unit is definitional, below.)
------------------------------------------------------------------------

++-assoc : {A : Set} {i j k : ℕ} (xs : Vec A i) (ys : Vec A j) (zs : Vec A k) →
           subst (Vec A) (+ℕ-assoc i j k) ((xs ++ ys) ++ zs) ≡ xs ++ (ys ++ zs)
++-assoc []       ys zs = refl
++-assoc {i = suc i'} {j} {k} (x ∷ xs) ys zs =
  trans (subst-∷ (+ℕ-assoc i' j k) x ((xs ++ ys) ++ zs))
        (cong (x ∷_) (++-assoc xs ys zs))

++-identityʳ : {A : Set} {i : ℕ} (xs : Vec A i) →
               subst (Vec A) (+ℕ-identityʳ i) (xs ++ []) ≡ xs
++-identityʳ []                = refl
++-identityʳ {i = suc i'} (x ∷ xs) =
  trans (subst-∷ (+ℕ-identityʳ i') x (xs ++ []))
        (cong (x ∷_) (++-identityʳ xs))

------------------------------------------------------------------------
-- 3. The graded-law PREDICATES (GradedAssoc / GradedUnitˡ / GradedUnitʳ) are
--    defined in Substrate.Algebra.Wedge.Product.LawTypes and re-exported above.
--    Vec (below) is the witness that they are inhabited.
------------------------------------------------------------------------

------------------------------------------------------------------------
-- 4. Vec satisfies all three graded laws.
------------------------------------------------------------------------

vec-assoc : (A : Set) → GradedAssoc (vec-product A)
vec-assoc A = ++-assoc

vec-unitˡ : (A : Set) → GradedUnitˡ (vec-product A)
vec-unitˡ A a = refl          -- [] ++ a = a definitionally (0 ℕ+ i = i)

vec-unitʳ : (A : Set) → GradedUnitʳ (vec-product A)
vec-unitʳ A = ++-identityʳ

------------------------------------------------------------------------
-- 5. THE GROTHENDIECK FLATTEN, as a theorem: a GradedProduct satisfying the
--    graded laws flattens to a FLAT Category.GradedMonoid on Σ ℕ C — the
--    fibered↔flat bridge. THE RESIDUE IS NEVER DROPPED (user): the grade AND
--    the wedged value are BOTH kept in the Σ (degree = proj₁ merely READS the
--    grade back; the non-residue being primary does not discard the residue).
--    Each +ℕ-assoc transport folds into the Σ first component (Σ-≡,≡→≡), turning
--    the fibered (transported) ∧-assoc into the flat (ordinary) ·-assoc.
------------------------------------------------------------------------

flatten-monoid : {C : ℕ → Set} (P : GradedProduct C) →
                 GradedAssoc P → GradedUnitˡ P → GradedUnitʳ P → GradedMonoid (Σ ℕ C)
flatten-monoid {C} P assoc unitˡ unitʳ = record
  { _·_         = λ { (i , a) (j , b) → i ℕ+ j , _∧_ P a b }
  ; ε           = 0 , u P
  ; ·-assoc     = λ { (i , a) (j , b) (k , c) → Σ-≡,≡→≡ (+ℕ-assoc i j k , assoc a b c) }
  ; ·-identityˡ = λ { (i , a) → Σ-≡,≡→≡ (refl , unitˡ a) }
  ; ·-identityʳ = λ { (i , a) → Σ-≡,≡→≡ (+ℕ-identityʳ i , unitʳ a) }
  ; degree      = proj₁
  ; degree-ε    = refl
  ; degree-·    = λ { (i , a) (j , b) → refl }
  }

-- Vec's flat graded monoid = the Grothendieck flatten of the append wedge
-- product (Σ ℕ Vec ≅ List): the fibered ++-laws become the flat monoid laws.
vec-flat-monoid : (A : Set) → GradedMonoid (Σ ℕ (Vec A))
vec-flat-monoid A =
  flatten-monoid (vec-product A) (vec-assoc A) (vec-unitˡ A) (vec-unitʳ A)
