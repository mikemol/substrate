------------------------------------------------------------------------
-- Substrate.Category.Poly
--
-- PF1-PF10: the substrate's polynomial-functor primitive.
--
-- A polynomial functor P : Set → Set has the form
--   P(y) = Σ_{a : Positions} y^{Directions a}
-- i.e., for each "position" a, an arrow type B(a) of "directions"
-- emanating from a. Polynomials model state-dependent input/output
-- arities, which is exactly what compositional / variable-arity
-- signal processing needs.
--
-- Per [[multi-field-tower-architecture]] + the FieldFanOut variable-
-- arity generalization (2026-05-21): Poly is the categorical home
-- of FieldFanOut. A FieldFanOut with Base = Position and
-- arity-fn = Direction-count gives a polynomial functor.
--
-- Per [[categorical-name-first]]: Polynomial Functor (Poly) is
-- the standard name from Spivak / Niu / Garner / Joyal.
--
-- Per the DBE constructive-completeness criterion: the record
-- carries (Positions, Directions). Given these, the polynomial's
-- ACTION on any type y can be constructed mechanically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Poly where

open import Substrate.Foundation.Product using (Σ; _,_; _×_; proj₁; proj₂)
open import Substrate.Foundation.Sum using (_⊎_; inj₁; inj₂)
open import Substrate.Foundation.Unit.Polymorphic using (⊤; tt)
open import Substrate.Foundation.Empty.Polymorphic using (⊥)
open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓ ℓ₁ ℓ₂ : Level

------------------------------------------------------------------------
-- PF1: The polynomial functor record.
--
-- Two-component data: a type of positions, and for each position a
-- type of directions.

record Poly : Set (lsuc ℓ) where
  field
    Positions  : Set ℓ
    Directions : Positions → Set ℓ

open Poly public

------------------------------------------------------------------------
-- PF2: Position / direction projections.
--
-- The polynomial's action on a type y:
--   P y = Σ (a : Positions) → (Directions a → y)
-- i.e., a position together with a function from its directions
-- into y.

⟦_⟧ : Poly {ℓ} → Set ℓ → Set ℓ
⟦ P ⟧ y = Σ (Positions P) λ a → (Directions P a → y)

------------------------------------------------------------------------
-- PF3: Polynomial functor morphism (lens shape).
--
-- A morphism P → Q is a pair:
--   on-positions : Positions P → Positions Q
--   on-directions : (p : Positions P) → Directions Q (on-positions p) →
--                                       Directions P p
-- The direction map is COVARIANT in Q, CONTRAVARIANT in P — i.e.,
-- it goes BACKWARDS. This is the lens shape: the forward map is
-- positions; the backward map carries directions back.

record _⇒_ (P Q : Poly {ℓ}) : Set ℓ where
  field
    on-positions  : Positions P → Positions Q
    on-directions : (p : Positions P) →
                    Directions Q (on-positions p) →
                    Directions P p

open _⇒_ public

------------------------------------------------------------------------
-- PF4: Identity polynomial functor morphism.

id-poly : ∀ {P : Poly {ℓ}} → P ⇒ P
id-poly = record
  { on-positions  = λ p → p
  ; on-directions = λ _ d → d
  }

------------------------------------------------------------------------
-- PF5: Coproduct (sum) of polynomials.
--
-- (P + Q)(y) = P(y) + Q(y).
-- Positions: Positions P ⊎ Positions Q.
-- Directions: case-split.

_⊕_ : Poly {ℓ} → Poly {ℓ} → Poly {ℓ}
P ⊕ Q = record
  { Positions  = Positions P ⊎ Positions Q
  ; Directions = λ where
      (inj₁ p) → Directions P p
      (inj₂ q) → Directions Q q
  }

------------------------------------------------------------------------
-- PF6: Product of polynomials.
--
-- (P × Q)(y) = P(y) × Q(y).
-- Positions: Positions P × Positions Q.
-- Directions: Directions P p ⊎ Directions Q q.

_⊗-poly_ : Poly {ℓ} → Poly {ℓ} → Poly {ℓ}
P ⊗-poly Q = record
  { Positions  = Positions P × Positions Q
  ; Directions = λ pq → Directions P (proj₁ pq) ⊎ Directions Q (proj₂ pq)
  }

------------------------------------------------------------------------
-- PF7: Composition `◁` of polynomials.
--
-- (P ◁ Q)(y) = P(Q(y)).
-- Positions of P ◁ Q: a position of P together with, for each of P's
-- directions, a position of Q.

_◁_ : Poly {ℓ} → Poly {ℓ} → Poly {ℓ}
P ◁ Q = record
  { Positions  = Σ (Positions P) λ p → (Directions P p → Positions Q)
  ; Directions = λ pq →
      Σ (Directions P (proj₁ pq)) λ d →
        Directions Q (proj₂ pq d)
  }

------------------------------------------------------------------------
-- PF8: Tensor `⊗` of polynomials (Day convolution).
--
-- (P ⊗ Q)(y) at positions (p, q) has directions (Directions P p) ×
-- (Directions Q q) — Cartesian product (vs ⊕ for ⊗-poly product).

_⊗ᴾ_ : Poly {ℓ} → Poly {ℓ} → Poly {ℓ}
P ⊗ᴾ Q = record
  { Positions  = Positions P × Positions Q
  ; Directions = λ pq → Directions P (proj₁ pq) × Directions Q (proj₂ pq)
  }

------------------------------------------------------------------------
-- PF9: The constant polynomial y ↦ A.
--
-- Constant A = Σ (a : A) → (⊥ → y) = A.
-- Positions = A, Directions a = ⊥.

const-poly : (A : Set ℓ) → Poly {ℓ}
const-poly A = record
  { Positions  = A
  ; Directions = λ _ → ⊥
  }

------------------------------------------------------------------------
-- PF10: The identity polynomial y ↦ y.
--
-- Identity = Σ (a : ⊤) → (⊤ → y) = y.
-- Positions = ⊤, Directions tt = ⊤.

identity-poly : Poly {ℓ}
identity-poly {ℓ} = record
  { Positions  = ⊤
  ; Directions = λ _ → ⊤
  }

------------------------------------------------------------------------
-- Categorical reading (PF arc partial).
--
-- The category Poly has polynomial functors as objects and
-- polynomial morphisms (PF3) as arrows. It has:
--   * Identity arrows (PF4)
--   * Composition `◁` (PF7) — Cartesian closed
--   * Coproducts and products (PF5, PF6)
--   * Two tensor products (⊗-poly via product, ⊗ᴾ via Day convolution)
--   * Constants and identity functor (PF9, PF10)
--
-- Per [[expose-generator-not-orbit]]: Poly is the generator of
-- variable-arity / mode-dependent system structure. The substrate's
-- existing FieldFanOut is a special case (constant Directions count).
------------------------------------------------------------------------
