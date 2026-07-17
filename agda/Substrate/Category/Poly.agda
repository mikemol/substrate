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

-- ⟡rc-poly (⟡set1-rerank2): Positions/Directions are PARAMETERS now (vestigial
-- record; a Set-valued field pins the record at Set (lsuc ℓ), params never raise
-- the sort). Combinators carry their computed carriers in the return TYPE.
record Poly (Positions : Set ℓ) (Directions : Positions → Set ℓ) : Set ℓ where
  constructor mkPoly

------------------------------------------------------------------------
-- PF2: Position / direction projections.
--
-- The polynomial's action on a type y:
--   P y = Σ (a : Positions) → (Directions a → y)
-- i.e., a position together with a function from its directions
-- into y.

⟦_⟧ : {Pos : Set ℓ} {Dir : Pos → Set ℓ} → Poly Pos Dir → Set ℓ → Set ℓ
⟦_⟧ {Pos = Pos} {Dir} P y = Σ Pos λ a → (Dir a → y)

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

record _⇒_ {PosP : Set ℓ} {DirP : PosP → Set ℓ}      -- ⟦shape:7fe1edaf {PosQ,(P,on-positions⟧
           {PosQ : Set ℓ} {DirQ : PosQ → Set ℓ}
           (P : Poly PosP DirP) (Q : Poly PosQ DirQ) : Set ℓ where
  field
    on-positions  : PosP → PosQ
    on-directions : (p : PosP) →
                    DirQ (on-positions p) →
                    DirP p

open _⇒_ public

------------------------------------------------------------------------
-- PF4: Identity polynomial functor morphism.

id-poly : ∀ {Pos : Set ℓ} {Dir : Pos → Set ℓ} {P : Poly Pos Dir} → P ⇒ P
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

_⊕_ : {PosP : Set ℓ} {DirP : PosP → Set ℓ} {PosQ : Set ℓ} {DirQ : PosQ → Set ℓ}
    → Poly PosP DirP → Poly PosQ DirQ
    → Poly (PosP ⊎ PosQ) (λ where (inj₁ p) → DirP p
                                  (inj₂ q) → DirQ q)
P ⊕ Q = record {}

------------------------------------------------------------------------
-- PF6: Product of polynomials.
--
-- (P × Q)(y) = P(y) × Q(y).
-- Positions: Positions P × Positions Q.
-- Directions: Directions P p ⊎ Directions Q q.

_⊗-poly_ : {PosP : Set ℓ} {DirP : PosP → Set ℓ} {PosQ : Set ℓ} {DirQ : PosQ → Set ℓ}
    → Poly PosP DirP → Poly PosQ DirQ
    → Poly (PosP × PosQ) (λ pq → DirP (proj₁ pq) ⊎ DirQ (proj₂ pq))
P ⊗-poly Q = record {}

------------------------------------------------------------------------
-- PF7: Composition `◁` of polynomials.
--
-- (P ◁ Q)(y) = P(Q(y)).
-- Positions of P ◁ Q: a position of P together with, for each of P's
-- directions, a position of Q.

_◁_ : {PosP : Set ℓ} {DirP : PosP → Set ℓ} {PosQ : Set ℓ} {DirQ : PosQ → Set ℓ}
    → Poly PosP DirP → Poly PosQ DirQ
    → Poly (Σ PosP (λ p → DirP p → PosQ))
           (λ pq → Σ (DirP (proj₁ pq)) λ d → DirQ (proj₂ pq d))
P ◁ Q = record {}

------------------------------------------------------------------------
-- PF8: Tensor `⊗` of polynomials (Day convolution).
--
-- (P ⊗ Q)(y) at positions (p, q) has directions (Directions P p) ×
-- (Directions Q q) — Cartesian product (vs ⊕ for ⊗-poly product).

_⊗ᴾ_ : {PosP : Set ℓ} {DirP : PosP → Set ℓ} {PosQ : Set ℓ} {DirQ : PosQ → Set ℓ}
    → Poly PosP DirP → Poly PosQ DirQ
    → Poly (PosP × PosQ) (λ pq → DirP (proj₁ pq) × DirQ (proj₂ pq))
P ⊗ᴾ Q = record {}

------------------------------------------------------------------------
-- PF9: The constant polynomial y ↦ A.
--
-- Constant A = Σ (a : A) → (⊥ → y) = A.
-- Positions = A, Directions a = ⊥.

const-poly : (A : Set ℓ) → Poly A (λ _ → ⊥)
const-poly A = record {}

------------------------------------------------------------------------
-- PF10: The identity polynomial y ↦ y.
--
-- Identity = Σ (a : ⊤) → (⊤ → y) = y.
-- Positions = ⊤, Directions tt = ⊤.

identity-poly : Poly {ℓ} ⊤ (λ _ → ⊤)
identity-poly = record {}

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
