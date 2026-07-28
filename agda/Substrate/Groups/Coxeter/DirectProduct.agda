------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.DirectProduct
--
-- Combinator: takes two abstract Coxeter Core instantiations and
-- produces a new abstract Core instantiation for their direct
-- product. Word = Word₁ × Word₂, all operations componentwise.
--
-- This is what makes the "Coxeter framework" actually composable:
-- finite Coxeter groups can be built as products of smaller pieces,
-- with the entire foundation (bridge lemmas, _·_, _≈_, _≉_, clash,
-- normalize-{idem,append,append-right,cong-right,distrib,triple,quad},
-- ≉-idem, ++-assoc-4) inherited unchanged.
--
-- Per [[feedback-v4-typeclass-architecture]] applied at the
-- combinator level: instead of writing a new Coxeter instance from
-- scratch for V₄ (= Z/2 × Z/2), instantiate this module with two
-- Z2-Coxeter Cores.
--
-- USERS: Substrate.Groups.V4-as-Z2xZ2 (and any future product-style
-- Coxeter instantiations: (Z/2)ⁿ, Z/2 × Z/3 = Z/6, etc.).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong; cong₂)

module Substrate.Groups.Coxeter.DirectProduct
  -- First component's Core inputs.
  (Word₁ : Set)
  (_++₁_ : Word₁ → Word₁ → Word₁)
  (ε₁ : Word₁)
  (++-assoc₁ : (a b c : Word₁) → (a ++₁ b) ++₁ c ≡ a ++₁ (b ++₁ c))
  (Canonical₁ : Word₁ → Set)
  (normalize₁ : Word₁ → Word₁)
  (normalize-canonical₁ : (w : Word₁) → Canonical₁ (normalize₁ w))
  (canonical-is-fixed₁ : {w : Word₁} → Canonical₁ w → normalize₁ w ≡ w)
  (normalize-distrib₁ : (a b : Word₁) →
    normalize₁ (a ++₁ b) ≡ normalize₁ (normalize₁ a ++₁ normalize₁ b))
  -- Second component's Core inputs.
  (Word₂ : Set)
  (_++₂_ : Word₂ → Word₂ → Word₂)
  (ε₂ : Word₂)
  (++-assoc₂ : (a b c : Word₂) → (a ++₂ b) ++₂ c ≡ a ++₂ (b ++₂ c))
  (Canonical₂ : Word₂ → Set)
  (normalize₂ : Word₂ → Word₂)
  (normalize-canonical₂ : (w : Word₂) → Canonical₂ (normalize₂ w))
  (canonical-is-fixed₂ : {w : Word₂} → Canonical₂ w → normalize₂ w ≡ w)
  (normalize-distrib₂ : (a b : Word₂) →
    normalize₂ (a ++₂ b) ≡ normalize₂ (normalize₂ a ++₂ normalize₂ b))
  where

------------------------------------------------------------------------
-- 1. Product carrier + monoid structure.
------------------------------------------------------------------------

Word : Set
Word = Word₁ × Word₂

-- Local ++ + ε made private so they don't clash with Core's
-- re-exported names (same definitions).
private
  _++-prod_ : Word → Word → Word
  (a₁ , a₂) ++-prod (b₁ , b₂) = (a₁ ++₁ b₁ , a₂ ++₂ b₂)

  ε-prod : Word
  ε-prod = (ε₁ , ε₂)

++-assoc : (a b c : Word) → (a ++-prod b) ++-prod c ≡ a ++-prod (b ++-prod c)
++-assoc (a₁ , a₂) (b₁ , b₂) (c₁ , c₂) =
  cong₂ _,_ (++-assoc₁ a₁ b₁ c₁) (++-assoc₂ a₂ b₂ c₂)

------------------------------------------------------------------------
-- 2. Product canonical-form predicate + normalize.
--
-- A pair is canonical iff both components are.
-- Normalize componentwise.
------------------------------------------------------------------------

Canonical-prod : Word → Set
Canonical-prod (w₁ , w₂) = Canonical₁ w₁ × Canonical₂ w₂

normalize : Word → Word
normalize (w₁ , w₂) = (normalize₁ w₁ , normalize₂ w₂)

normalize-canonical : (w : Word) → Canonical-prod (normalize w)
normalize-canonical (w₁ , w₂) =
  (normalize-canonical₁ w₁ , normalize-canonical₂ w₂)

canonical-is-fixed : {w : Word} → Canonical-prod w → normalize w ≡ w
canonical-is-fixed {w₁ , w₂} (c₁ , c₂) =
  cong₂ _,_ (canonical-is-fixed₁ c₁) (canonical-is-fixed₂ c₂)

------------------------------------------------------------------------
-- 3. The homomorphism property — lifts componentwise from each
-- component's normalize-distrib.
------------------------------------------------------------------------

normalize-distrib : (a b : Word) →
                    normalize (a ++-prod b) ≡ normalize (normalize a ++-prod normalize b)
normalize-distrib (a₁ , a₂) (b₁ , b₂) =
  cong₂ _,_ (normalize-distrib₁ a₁ b₁) (normalize-distrib₂ a₂ b₂)

------------------------------------------------------------------------
-- 4. Instantiate the abstract Core with the product atoms.
--
-- Re-exports _·_, _≈_, _≉_, ε, normalize-idem, normalize-append,
-- normalize-append-right, normalize-cong-right, normalize-triple,
-- normalize-quad, ≉-idem, clash, ++-assoc-4 — all derived
-- parametrically in Core.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.Core
  Word _++-prod_ ε-prod ++-assoc Canonical-prod normalize normalize-canonical
  canonical-is-fixed normalize-distrib
  public
