------------------------------------------------------------------------
-- Substrate.Algebra.F2
--
-- M-1 of the Cocycles structural-migration plan (Substrate/Cocycles.DBE.md).
--
-- The field with 2 elements, as a custom 2-constructor data type with
-- field operations and axioms proven by case analysis. Rolling our own
-- (per user direction: no stdlib dependency in the structural migration).
--
-- The universal property — "any 2-element field is isomorphic to F₂" —
-- lives in M-1.5 (Substrate.Algebra.F2.Universal). That property is the
-- bridge to any future alternative representation (Bool, Coxeter Z₂,
-- Fin 2, etc.) without enumerating equivalence per representation.
--
-- Design notes:
--   * `𝟘` and `𝟙` are the elements; `_+_` is XOR, `_·_` is AND.
--   * `-_` is identity (characteristic 2; every element is self-inverse).
--   * `_+_` has the leftmost-argument pivot pattern (𝟘 + y = y) so
--     identityˡ is refl; identityʳ needs a 2-case proof.
--   * `_·_` is left-strict (𝟘 · _ = 𝟘) so absorbˡ is refl.
--   * Multiplicative inverse is treated only for 𝟙 (the only invertible
--     element); 𝟘 has no inverse in any field (this is part of the
--     field axiom — see M-1.5 for the universal statement).
--
-- See: catalog/cocycles.md — the V₄-Signature / RM(1,3) layer this
-- module foundations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2 where

open import Substrate.Foundation.Empty using (⊥; ⊥-elim)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)

------------------------------------------------------------------------
-- The 2-element carrier.
------------------------------------------------------------------------

data F₂ : Set where
  𝟘 : F₂
  𝟙 : F₂

------------------------------------------------------------------------
-- Operations.
------------------------------------------------------------------------

infixl 6 _+_
infixl 7 _·_
infix  8 -_

_+_ : F₂ → F₂ → F₂
𝟘 + y = y
𝟙 + 𝟘 = 𝟙
𝟙 + 𝟙 = 𝟘

_·_ : F₂ → F₂ → F₂
𝟘 · _ = 𝟘
𝟙 · y = y

-_ : F₂ → F₂
- x = x   -- characteristic 2: every element is its own additive inverse

------------------------------------------------------------------------
-- Distinctness of the two elements (the non-trivial field axiom).
------------------------------------------------------------------------

𝟙≢𝟘 : 𝟙 ≡ 𝟘 → ⊥
𝟙≢𝟘 ()

𝟘≢𝟙 : 𝟘 ≡ 𝟙 → ⊥
𝟘≢𝟙 ()

------------------------------------------------------------------------
-- Decidable equality (used by Vec F₂ n and downstream modules).
------------------------------------------------------------------------

_≟_ : (x y : F₂) → Dec (x ≡ y)
𝟘 ≟ 𝟘 = yes refl
𝟘 ≟ 𝟙 = no 𝟘≢𝟙
𝟙 ≟ 𝟘 = no 𝟙≢𝟘
𝟙 ≟ 𝟙 = yes refl

------------------------------------------------------------------------
-- Additive axioms.
--
-- Identity-left and absorb-zero are `refl` by the operations' pivot
-- choice. The other axioms are 2- or 4-case enumerations on F₂.
------------------------------------------------------------------------

+-identityˡ : (x : F₂) → (𝟘 + x) ≡ x
+-identityˡ _ = refl

+-identityʳ : (x : F₂) → (x + 𝟘) ≡ x
+-identityʳ 𝟘 = refl
+-identityʳ 𝟙 = refl

+-assoc : (x y z : F₂) → ((x + y) + z) ≡ (x + (y + z))
+-assoc 𝟘 _ _ = refl
+-assoc 𝟙 𝟘 _ = refl
+-assoc 𝟙 𝟙 𝟘 = refl
+-assoc 𝟙 𝟙 𝟙 = refl

+-comm : (x y : F₂) → (x + y) ≡ (y + x)
+-comm 𝟘 𝟘 = refl
+-comm 𝟘 𝟙 = refl
+-comm 𝟙 𝟘 = refl
+-comm 𝟙 𝟙 = refl

+-inverseˡ : (x : F₂) → ((- x) + x) ≡ 𝟘
+-inverseˡ 𝟘 = refl
+-inverseˡ 𝟙 = refl

+-inverseʳ : (x : F₂) → (x + (- x)) ≡ 𝟘
+-inverseʳ 𝟘 = refl
+-inverseʳ 𝟙 = refl

------------------------------------------------------------------------
-- Multiplicative axioms.
--
-- 𝟙 is the multiplicative identity; 𝟘 absorbs. The only invertible
-- element is 𝟙 (which is its own inverse).
------------------------------------------------------------------------

·-identityˡ : (x : F₂) → (𝟙 · x) ≡ x
·-identityˡ _ = refl

·-identityʳ : (x : F₂) → (x · 𝟙) ≡ x
·-identityʳ 𝟘 = refl
·-identityʳ 𝟙 = refl

·-absorbˡ : (x : F₂) → (𝟘 · x) ≡ 𝟘
·-absorbˡ _ = refl

·-absorbʳ : (x : F₂) → (x · 𝟘) ≡ 𝟘
·-absorbʳ 𝟘 = refl
·-absorbʳ 𝟙 = refl

·-assoc : (x y z : F₂) → ((x · y) · z) ≡ (x · (y · z))
·-assoc 𝟘 _ _ = refl
·-assoc 𝟙 _ _ = refl

·-comm : (x y : F₂) → (x · y) ≡ (y · x)
·-comm 𝟘 𝟘 = refl
·-comm 𝟘 𝟙 = refl
·-comm 𝟙 𝟘 = refl
·-comm 𝟙 𝟙 = refl

------------------------------------------------------------------------
-- Multiplicative inverse on the invertible element only.
--
-- The total form `_⁻¹ : F₂ → F₂` is intentionally absent — there is
-- no inverse for 𝟘 in any field, and giving 𝟘⁻¹ a junk value (e.g.
-- 𝟘 or 𝟙) creates a leaky abstraction. Consumers that need an
-- inverse work with the partial form `inv-of-𝟙` directly, and the
-- (rare) generic inverse pattern is mediated by the universal
-- property in M-1.5.
------------------------------------------------------------------------

inv-of-𝟙 : (𝟙 · 𝟙) ≡ 𝟙
inv-of-𝟙 = refl

------------------------------------------------------------------------
-- Distributivity.
------------------------------------------------------------------------

·-distribˡ-+ : (x y z : F₂) → (x · (y + z)) ≡ ((x · y) + (x · z))
·-distribˡ-+ 𝟘 _ _ = refl
·-distribˡ-+ 𝟙 _ _ = refl

·-distribʳ-+ : (x y z : F₂) → ((y + z) · x) ≡ ((y · x) + (z · x))
·-distribʳ-+ x y z =
  trans (·-comm (y + z) x)
        (trans (·-distribˡ-+ x y z)
               (cong₂ _+_ (·-comm x y) (·-comm x z)))

------------------------------------------------------------------------
-- A handful of useful derived facts (all proven by case analysis,
-- finitely small here, but used as inference rules elsewhere).
------------------------------------------------------------------------

-- x + x ≡ 𝟘 (characteristic 2).
+-self-inverse : (x : F₂) → (x + x) ≡ 𝟘
+-self-inverse 𝟘 = refl
+-self-inverse 𝟙 = refl

-- x · x ≡ x (idempotency).
·-idempotent : (x : F₂) → (x · x) ≡ x
·-idempotent 𝟘 = refl
·-idempotent 𝟙 = refl

-- The two-element trichotomy: every F₂ element is 𝟘 or 𝟙. This is
-- the structural-extensionality lemma that lets downstream code
-- prove F₂-valued equalities by 2 cases instead of arbitrary
-- pattern-matching.
F₂-cases : (x : F₂) → (x ≡ 𝟘) ⊎ (x ≡ 𝟙)
F₂-cases 𝟘 = inj₁ refl
F₂-cases 𝟙 = inj₂ refl
