------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.CanonicalCover
--
-- Polymorphic n-refls tables and their structural compositions.
--
-- One recursive type constructor `Pow A n` (right-associated n-tuple
-- of A) replaces every hand-spelled nested product type.
--
-- Compositional structure (per [[feedback-expose-generator-not-orbit]]):
-- a 4ⁿ-Cayley table IS the n-fold tensor of 4-refls, written as
-- `copies 4` applied repeatedly. The orbit (16, 64, …) shrinks to
-- the generator (`4-refls`, `copies 4`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Coxeter.CanonicalCover where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)

------------------------------------------------------------------------
-- Pow A n = A × A × ... × A (n copies, right-associated). For n ≥ 1.
-- copies n a = (a, a, …, a) — n copies of a.
------------------------------------------------------------------------

Pow : ∀ {ℓ} → Set ℓ → ℕ → Set ℓ
Pow A zero            = A             -- placeholder, callers use n ≥ 1
Pow A (suc zero)      = A
Pow A (suc (suc n))   = A × Pow A (suc n)

copies : ∀ {ℓ} {A : Set ℓ} (n : ℕ) → A → Pow A n
copies zero          a = a
copies (suc zero)    a = a
copies (suc (suc n)) a = a , copies (suc n) a

------------------------------------------------------------------------
-- The single primitive: a flat n-refls tuple, parametric in n.
-- Call sites write `n-refls 4`, `n-refls 6`, etc. — no per-arity alias.
------------------------------------------------------------------------

n-refls : ∀ {ℓ} {A : Set ℓ} {x : A} (n : ℕ) → Pow (x ≡ x) n
n-refls n = copies n refl

------------------------------------------------------------------------
-- Compositional refls — nested products matching Cayley-table fanout.
-- A k-fan over an m-leaf table is `copies k (… inner-table …)`.
--
-- V₄-arity:    4²-refls covers V₄ × V₄;  4³-refls covers V₄³.
-- F₂-binary:   2⁴-refls covers F₂⁴ ≅ V₄ × V₄ via binary fan-out;
--              2³-refls covers F₂³ ≅ S₃-like.
------------------------------------------------------------------------

4²-refls : ∀ {ℓ} {A : Set ℓ} {x : A} → Pow (Pow (x ≡ x) 4) 4
4²-refls = copies 4 (n-refls 4)

4³-refls : ∀ {ℓ} {A : Set ℓ} {x : A} → Pow (Pow (Pow (x ≡ x) 4) 4) 4
4³-refls = copies 4 4²-refls

2²-refls : ∀ {ℓ} {A : Set ℓ} {x : A} → Pow (Pow (x ≡ x) 2) 2
2²-refls = copies 2 (n-refls 2)

2³-refls : ∀ {ℓ} {A : Set ℓ} {x : A} → Pow (Pow (Pow (x ≡ x) 2) 2) 2
2³-refls = copies 2 2²-refls

2⁴-refls : ∀ {ℓ} {A : Set ℓ} {x : A} →
           Pow (Pow (Pow (Pow (x ≡ x) 2) 2) 2) 2
2⁴-refls = copies 2 2³-refls
