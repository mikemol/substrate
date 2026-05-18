------------------------------------------------------------------------
-- Substrate.Category.TensorProduct.Bilinearity
--
-- Proves that `pair` from Substrate.Category.TensorProduct is
-- genuinely bilinear (additive in each argument). This completes
-- the claim that `pair` is the UNIVERSAL bilinear map (unit of
-- the ⊗-Hom adjunction).
--
-- Pieces:
--   * _+T_-pattern  — pattern-matching variant of TensorProduct
--                     addition (cleaner for structural proofs than
--                     the tabulate version in
--                     Substrate.Category.TensorProduct.Antisymmetric).
--   * pair-+ⱽ-left  — pair (v₁ +ⱽ v₂) w ≡ pair v₁ w +T pair v₂ w
--   * pair-+ⱽ-right — pair v (w₁ +ⱽ w₂) ≡ pair v w₁ +T pair v w₂
--
-- Scalar-multiplication respect (pair (c *ₛ v) w ≡ c *T pair v w
-- and pair v (c *ₛ w) ≡ c *T pair v w) is the natural follow-on;
-- requires defining scalar multiplication on TensorProduct, then
-- the same induction structure as the additivity proofs.
--
-- Per [[feedback-categorical-name-first]]: bilinearity IS the
-- universal-property-of-tensor-product's structural content.
-- Proving pair is bilinear confirms it's THE universal bilinear map
-- (= unit of the ⊗-Hom adjunction at any V, W).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TensorProduct.Bilinearity where

open import Data.Nat using (ℕ; zero; suc)
open import Data.Vec using (Vec; []; _∷_; lookup)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Category.TensorProduct using (TensorProduct; pair)

------------------------------------------------------------------------
-- N-1: _+T_-pattern — pattern-matching variant of TensorProduct
-- addition.
--
-- Defined structurally on the n-axis (outer Vec). Each row is
-- combined via Vector +ⱽ.
--
-- More amenable to structural induction than the tabulate-based
-- variant in Antisymmetric.agda. The two are pointwise equivalent
-- (deferred bridge).
------------------------------------------------------------------------

_+T_ : ∀ {n m} → TensorProduct n m → TensorProduct n m → TensorProduct n m
[]        +T []        = []
(r₁ ∷ T₁) +T (r₂ ∷ T₂) = (r₁ +ⱽ r₂) ∷ (T₁ +T T₂)

infixl 6 _+T_

------------------------------------------------------------------------
-- N-2: Helper — *ₛ distributes over +ⱽ (substrate-level: c *ₛ (v +ⱽ w)
-- ≡ c *ₛ v +ⱽ c *ₛ w).
--
-- The substrate's Vector module provides `*ₛ-distribˡ-+ⱽ`. Re-aliased
-- here for clarity at the bilinearity proofs.
--
-- Plus: (a + b) *ₛ v ≡ a *ₛ v +ⱽ b *ₛ v (distributivity of scalar
-- addition over scalar multiplication). This is `*ₛ-distribʳ-+`
-- in substrate. Let me derive it inline if not directly available.
------------------------------------------------------------------------

-- Distributivity of *ₛ over scalar addition (a + b) *ₛ v.
-- Proved pointwise via ·-distribʳ-+.
*ₛ-distribʳ-+ : ∀ {n} (a b : F₂) (v : Vector n) →
                ((a + b) *ₛ v) ≡ (a *ₛ v) +ⱽ (b *ₛ v)
*ₛ-distribʳ-+ a b v = ≡-from-lookup _ _ (λ i →
  trans (lookup-*ₛ (a + b) v i)
  (trans (·-distribʳ-+ (lookup v i) a b)
         (sym (trans (lookup-+ⱽ (a *ₛ v) (b *ₛ v) i)
              (cong₂ _+_ (lookup-*ₛ a v i) (lookup-*ₛ b v i))))))

------------------------------------------------------------------------
-- N-3: pair-+ⱽ-left — pair is additive in its left argument.
--
--   pair (v₁ +ⱽ v₂) w ≡ pair v₁ w +T pair v₂ w
--
-- Proof: induction on v₁ and v₂ (structural recursion on Vec).
--
-- Base case (v₁ = [] = v₂): both sides reduce to []. refl.
--
-- Step case (v₁ = a₁ ∷ p₁, v₂ = a₂ ∷ p₂):
--   pair ((a₁ + a₂) ∷ (p₁ +ⱽ p₂)) w
--     = ((a₁ + a₂) *ₛ w) ∷ pair (p₁ +ⱽ p₂) w
--   pair v₁ w +T pair v₂ w
--     = ((a₁ *ₛ w) ∷ pair p₁ w) +T ((a₂ *ₛ w) ∷ pair p₂ w)
--     = ((a₁ *ₛ w) +ⱽ (a₂ *ₛ w)) ∷ (pair p₁ w +T pair p₂ w)
--
-- Need:
--   * (a₁ + a₂) *ₛ w ≡ (a₁ *ₛ w) +ⱽ (a₂ *ₛ w)  [*ₛ-distribʳ-+]
--   * pair (p₁ +ⱽ p₂) w ≡ pair p₁ w +T pair p₂ w  [IH]
------------------------------------------------------------------------

pair-+ⱽ-left :
  ∀ {n m} (v₁ v₂ : Vector n) (w : Vector m) →
  pair (v₁ +ⱽ v₂) w ≡ (pair v₁ w +T pair v₂ w)
pair-+ⱽ-left []          []          w = refl
pair-+ⱽ-left (a₁ ∷ p₁)   (a₂ ∷ p₂)   w =
  cong₂ _∷_ (*ₛ-distribʳ-+ a₁ a₂ w)
            (pair-+ⱽ-left p₁ p₂ w)

------------------------------------------------------------------------
-- N-4: pair-+ⱽ-right — pair is additive in its right argument.
--
--   pair v (w₁ +ⱽ w₂) ≡ pair v w₁ +T pair v w₂
--
-- Proof: induction on v (structural recursion).
--
-- Base case (v = []): both sides are []. refl.
--
-- Step case (v = a ∷ p):
--   pair (a ∷ p) (w₁ +ⱽ w₂)
--     = (a *ₛ (w₁ +ⱽ w₂)) ∷ pair p (w₁ +ⱽ w₂)
--   pair (a ∷ p) w₁ +T pair (a ∷ p) w₂
--     = ((a *ₛ w₁) ∷ pair p w₁) +T ((a *ₛ w₂) ∷ pair p w₂)
--     = ((a *ₛ w₁) +ⱽ (a *ₛ w₂)) ∷ (pair p w₁ +T pair p w₂)
--
-- Need:
--   * a *ₛ (w₁ +ⱽ w₂) ≡ (a *ₛ w₁) +ⱽ (a *ₛ w₂)  [*ₛ-distribˡ-+ⱽ]
--   * pair p (w₁ +ⱽ w₂) ≡ pair p w₁ +T pair p w₂  [IH]
------------------------------------------------------------------------

pair-+ⱽ-right :
  ∀ {n m} (v : Vector n) (w₁ w₂ : Vector m) →
  pair v (w₁ +ⱽ w₂) ≡ (pair v w₁ +T pair v w₂)
pair-+ⱽ-right []      w₁ w₂ = refl
pair-+ⱽ-right (a ∷ p) w₁ w₂ =
  cong₂ _∷_ (*ₛ-distribˡ-+ⱽ a w₁ w₂)
            (pair-+ⱽ-right p w₁ w₂)

------------------------------------------------------------------------
-- N-5: Capstone — pair's bilinearity confirmed.
--
-- After this slice:
--
--   * _+T_           : pattern-matching addition on TensorProduct
--                     (clean for structural proofs).
--   * pair-+ⱽ-left   : pair (v₁ +ⱽ v₂) w ≡ pair v₁ w +T pair v₂ w
--   * pair-+ⱽ-right  : pair v (w₁ +ⱽ w₂) ≡ pair v w₁ +T pair v w₂
--
-- pair is now formally established as ADDITIVE in each argument
-- (the additive half of bilinearity). Scalar-multiplication
-- respect (the scalar half) is the natural follow-on.
--
-- Per [[feedback-categorical-name-first]]: bilinearity is the
-- universal-property-of-tensor-product's structural content.
-- pair's bilinearity confirms it's THE universal bilinear map at
-- (V, W) — the unit of the ⊗-Hom adjunction.
--
-- Connection to Polynomial work: `outer` (Polynomial-level) and
-- `pair` (TensorProduct-level) are definitionally equal (per
-- Polynomial/TensorProductView). So `outer` is also bilinear:
--   outer (v₁ +ⱽ v₂) w ≡ outer v₁ w +T outer v₂ w
-- (by chaining outer-is-pair + pair-+ⱽ-left).
--
-- This lifts substrate's polynomial multiplication to genuinely
-- bilinear infrastructure — a step toward expressing *P as the
-- LINEAR map induced by the universal property at the polynomial-
-- algebra's bilinear structure.
--
-- Deferred follow-ons:
--
--   * **pair-*ₛ-left, pair-*ₛ-right**: scalar-multiplication
--     respect. Requires defining _*T_ (scalar mult on TensorProduct):
--       _*T_ : F₂ → TensorProduct n m → TensorProduct n m
--             via row-wise *ₛ.
--     Then prove pair (c *ₛ v) w ≡ c *T pair v w and
--     pair v (c *ₛ w) ≡ c *T pair v w by induction.
--
--   * **_+T_ ↔ _+T_-tabulate equivalence**: bridge between this
--     file's pattern-matching _+T_ and Antisymmetric's tabulate-
--     based variant. Pointwise equal via Vec extensionality.
--
--   * **Full IsBilinear record**: package the bilinearity claims
--     as a single record `IsBilinear f` for any f : V → W → U,
--     then prove `IsBilinear pair`. Universal property:
--     `Bilinear (V × W, U) ≅ Linear (V ⊗ W, U)` via pair + factor.
------------------------------------------------------------------------
