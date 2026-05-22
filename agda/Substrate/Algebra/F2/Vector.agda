------------------------------------------------------------------------
-- Substrate.Algebra.F2.Vector
--
-- M-2 of the Cocycles structural-migration plan. F₂-vectors of fixed
-- length n, with componentwise field operations.
--
-- Data structure: stdlib's `Data.Vec` (a basic data structure, not an
-- algebra bundle — the "no stdlib" commitment is about not depending
-- on stdlib's Field/Module abstractions, not about reinventing Vec).
--
-- This file's scope is the operational layer: Vec F₂ n + componentwise
-- + / · / scalar · / 0 / basis vectors + componentwise axioms. The
-- universal property (free-module extensionality) is M-2.5
-- (Substrate.Algebra.F2.Vector.Universal) — the "two F₂-linear maps
-- on Vec F₂ n agree iff they agree on basis vectors" lemma that lets
-- bridges reduce to n equalities instead of 2^n.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Vector where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate; lookup; zipWith; map)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2

------------------------------------------------------------------------
-- The vector type and basic operations.
------------------------------------------------------------------------

Vector : ℕ → Set
Vector n = Vec F₂ n

-- Zero vector — all components 𝟘.
𝟎ⱽ : ∀ {n} → Vector n
𝟎ⱽ {n} = replicate n 𝟘

infixl 6 _+ⱽ_
infixl 7 _*ₛ_
infix  8 -ⱽ_

-- Componentwise addition.
_+ⱽ_ : ∀ {n} → Vector n → Vector n → Vector n
_+ⱽ_ = zipWith _+_

-- Scalar multiplication.
_*ₛ_ : ∀ {n} → F₂ → Vector n → Vector n
c *ₛ v = map (c ·_) v

-- Negation — identity in characteristic 2, kept named for clarity at
-- call sites.
-ⱽ_ : ∀ {n} → Vector n → Vector n
-ⱽ_ = map (-_)

-- Componentwise Hadamard product (rarely used directly; included for
-- completeness with the +-/-·- algebra and for code-side computations
-- like coordinatewise testing).
_·ⱽ_ : ∀ {n} → Vector n → Vector n → Vector n
_·ⱽ_ = zipWith _·_

------------------------------------------------------------------------
-- Basis vectors: e_i has 𝟙 at position i, 𝟘 elsewhere.
--
-- Defined recursively on (n, i) via Fin's zero/suc. `basis (suc i)`
-- prepends a 𝟘 to `basis i` in a smaller vector.
------------------------------------------------------------------------

basis : ∀ {n} → Fin n → Vector n
basis {suc _} zero    = 𝟙 ∷ 𝟎ⱽ
basis {suc _} (suc i) = 𝟘 ∷ basis i

------------------------------------------------------------------------
-- Pointwise lookup characterisation.
--
-- These are the structural primitives that drive M-2.5 (universal
-- property): every fact about Vec F₂ n can be reduced to facts about
-- `lookup v i`.
------------------------------------------------------------------------

-- Lookup of zero vector is always 𝟘. Induction on i (which constrains n).
lookup-𝟎 : ∀ {n} (i : Fin n) → lookup (𝟎ⱽ {n}) i ≡ 𝟘
lookup-𝟎 zero    = refl
lookup-𝟎 (suc i) = lookup-𝟎 i

-- Lookup of (u +ⱽ v) at i is (lookup u i) + (lookup v i).
lookup-+ⱽ : ∀ {n} (u v : Vector n) (i : Fin n) →
            lookup (u +ⱽ v) i ≡ (lookup u i) + (lookup v i)
lookup-+ⱽ (x ∷ _) (y ∷ _) zero    = refl
lookup-+ⱽ (_ ∷ u) (_ ∷ v) (suc i) = lookup-+ⱽ u v i

-- Lookup of (c *ₛ v) at i is c · (lookup v i).
lookup-*ₛ : ∀ {n} (c : F₂) (v : Vector n) (i : Fin n) →
            lookup (c *ₛ v) i ≡ c · (lookup v i)
lookup-*ₛ _ (_ ∷ _) zero    = refl
lookup-*ₛ c (_ ∷ v) (suc i) = lookup-*ₛ c v i

-- Lookup of -ⱽ v at i is - (lookup v i).
lookup--ⱽ : ∀ {n} (v : Vector n) (i : Fin n) →
            lookup (-ⱽ v) i ≡ - (lookup v i)
lookup--ⱽ (_ ∷ _) zero    = refl
lookup--ⱽ (_ ∷ v) (suc i) = lookup--ⱽ v i

------------------------------------------------------------------------
-- Basis-lookup characterisation: lookup (basis i) j is 𝟙 if i = j,
-- 𝟘 otherwise. Useful for the universal-property module (M-2.5).
------------------------------------------------------------------------

-- lookup (basis i) i ≡ 𝟙
basis-lookup-same : ∀ {n} (i : Fin n) → lookup (basis i) i ≡ 𝟙
basis-lookup-same zero    = refl
basis-lookup-same (suc i) = basis-lookup-same i

-- Pointwise extensionality of Vec — propositional equality reduces
-- to all-lookup equality. This is the structural primitive that drives
-- "Vec equality from componentwise equality" downstream.
≡-from-lookup : ∀ {n} (u v : Vector n) →
                ((i : Fin n) → lookup u i ≡ lookup v i) →
                u ≡ v
≡-from-lookup []      []      _ = refl
≡-from-lookup (x ∷ u) (y ∷ v) eq =
  cong₂ _∷_ (eq zero) (≡-from-lookup u v (λ i → eq (suc i)))

------------------------------------------------------------------------
-- Algebraic axioms — proved POINTWISE via the lookup characterisation.
--
-- This is the structural pattern: lift each F₂ axiom to Vec F₂ n
-- componentwise. The pattern is:
--   axiom-on-Vec u v ... = ≡-from-lookup _ _ (λ i → axiom-on-F₂ ...)
-- which keeps proofs to one line each, no per-component enumeration.
------------------------------------------------------------------------

+ⱽ-identityˡ : ∀ {n} (v : Vector n) → (𝟎ⱽ +ⱽ v) ≡ v
+ⱽ-identityˡ v = ≡-from-lookup (𝟎ⱽ +ⱽ v) v
  (λ i → trans (lookup-+ⱽ 𝟎ⱽ v i)
        (trans (cong (_+ lookup v i) (lookup-𝟎 i))
               (+-identityˡ (lookup v i))))

+ⱽ-identityʳ : ∀ {n} (v : Vector n) → (v +ⱽ 𝟎ⱽ) ≡ v
+ⱽ-identityʳ v = ≡-from-lookup (v +ⱽ 𝟎ⱽ) v
  (λ i → trans (lookup-+ⱽ v 𝟎ⱽ i)
        (trans (cong (lookup v i +_) (lookup-𝟎 i))
               (+-identityʳ (lookup v i))))

+ⱽ-comm : ∀ {n} (u v : Vector n) → (u +ⱽ v) ≡ (v +ⱽ u)
+ⱽ-comm u v = ≡-from-lookup (u +ⱽ v) (v +ⱽ u)
  (λ i → trans (lookup-+ⱽ u v i)
        (trans (+-comm (lookup u i) (lookup v i))
               (sym (lookup-+ⱽ v u i))))

+ⱽ-assoc : ∀ {n} (u v w : Vector n) →
           ((u +ⱽ v) +ⱽ w) ≡ (u +ⱽ (v +ⱽ w))
+ⱽ-assoc u v w = ≡-from-lookup ((u +ⱽ v) +ⱽ w) (u +ⱽ (v +ⱽ w))
  (λ i →
    let li-uvw = lookup-+ⱽ (u +ⱽ v) w i
        lj-uv  = lookup-+ⱽ u v i
        rk-uvw = lookup-+ⱽ u (v +ⱽ w) i
        rl-vw  = lookup-+ⱽ v w i
    in trans li-uvw
       (trans (cong (_+ lookup w i) lj-uv)
       (trans (+-assoc (lookup u i) (lookup v i) (lookup w i))
       (trans (cong (lookup u i +_) (sym rl-vw))
              (sym rk-uvw)))))

+ⱽ-self-inverse : ∀ {n} (v : Vector n) → (v +ⱽ v) ≡ 𝟎ⱽ
+ⱽ-self-inverse v = ≡-from-lookup (v +ⱽ v) 𝟎ⱽ
  (λ i → trans (lookup-+ⱽ v v i)
        (trans (+-self-inverse (lookup v i))
               (sym (lookup-𝟎 i))))

------------------------------------------------------------------------
-- Scalar-multiplication axioms.
------------------------------------------------------------------------

*ₛ-identityˡ : ∀ {n} (v : Vector n) → (𝟙 *ₛ v) ≡ v
*ₛ-identityˡ v = ≡-from-lookup (𝟙 *ₛ v) v
  (λ i → trans (lookup-*ₛ 𝟙 v i) (·-identityˡ (lookup v i)))

*ₛ-absorbˡ : ∀ {n} (v : Vector n) → (𝟘 *ₛ v) ≡ 𝟎ⱽ
*ₛ-absorbˡ v = ≡-from-lookup (𝟘 *ₛ v) 𝟎ⱽ
  (λ i → trans (lookup-*ₛ 𝟘 v i)
        (trans (·-absorbˡ (lookup v i))
               (sym (lookup-𝟎 i))))

*ₛ-distribˡ-+ⱽ : ∀ {n} (c : F₂) (u v : Vector n) →
                 (c *ₛ (u +ⱽ v)) ≡ ((c *ₛ u) +ⱽ (c *ₛ v))
*ₛ-distribˡ-+ⱽ c u v = ≡-from-lookup (c *ₛ (u +ⱽ v)) ((c *ₛ u) +ⱽ (c *ₛ v))
  (λ i →
    trans (lookup-*ₛ c (u +ⱽ v) i)
    (trans (cong (c ·_) (lookup-+ⱽ u v i))
    (trans (·-distribˡ-+ c (lookup u i) (lookup v i))
    (trans (cong₂ _+_ (sym (lookup-*ₛ c u i)) (sym (lookup-*ₛ c v i)))
           (sym (lookup-+ⱽ (c *ₛ u) (c *ₛ v) i))))))
