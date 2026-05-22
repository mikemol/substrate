------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.SelfDual
--
-- N-5 of M-11.dim4. The self-dual subspace of Λ²(F₂⁴): bivectors
-- fixed by the Hodge ★ involution.
--
-- ω ∈ SelfDual iff `apply hodge-star ω ≡ ω`, equivalently
-- iff `apply hodge-star ω +ⱽ ω ≡ 𝟎ⱽ` (in F₂, addition = subtraction).
--
-- Since Hodge ★ is the index-reversal involution on Fin 6, the self-
-- dual bivectors are those whose Vector 6 coordinates satisfy
-- `lookup ω i ≡ lookup ω (complement i)` for all i. With 3 fixed-
-- point-free pairs (0↔5, 1↔4, 2↔3), this gives 3 independent F₂
-- choices = 2³ = **8 self-dual bivectors**.
--
-- The catalog's "8 reserved signed singletons" reading might
-- identify with this 8-element fixed subspace; a formal bridge to
-- Codeword.agda's `Reserved` is deferred to M-11.dim4.reserved-bridge.
--
-- This file provides:
--   * `SelfDual-Pred` — the predicate form.
--   * Three canonical self-dual generators (sd-pair-01-23, etc.) +
--     refl-or-near-refl proofs that each is self-dual.
--   * Closure properties (sum + scalar multiple of self-dual bivectors
--     is self-dual) — deferred unless a consumer needs them.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.SelfDual where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong; cong₂)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector
open import Substrate.Algebra.F2.Linear
open import Substrate.Algebra.F2.Linear.FromImages
  using (apply-linear-from-images-basis)
open import Substrate.Algebra.F2.HodgeDim4.Bivector
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar

------------------------------------------------------------------------
-- The self-dual predicate.
------------------------------------------------------------------------

SelfDual-Pred : Bivector → Set
SelfDual-Pred ω = apply hodge-star ω ≡ ω

------------------------------------------------------------------------
-- The three canonical self-dual generators.
--
-- Each is a sum of a basis 2-blade and its complement; together they
-- span the 3-dim self-dual subspace (2³ = 8 elements).
------------------------------------------------------------------------

sd-pair-01-23 : Bivector            -- e₀ ∧ e₁ + e₂ ∧ e₃
sd-pair-01-23 = basis b₀₁ +ⱽ basis b₂₃

sd-pair-02-13 : Bivector            -- e₀ ∧ e₂ + e₁ ∧ e₃
sd-pair-02-13 = basis b₀₂ +ⱽ basis b₁₃

sd-pair-03-12 : Bivector            -- e₀ ∧ e₃ + e₁ ∧ e₂
sd-pair-03-12 = basis b₀₃ +ⱽ basis b₁₂

------------------------------------------------------------------------
-- self-dual-via-complement-pair — named universal property: for any
-- basis index x, the bivector `basis x +ⱽ basis (complement x)` is
-- self-dual.
--
-- Chain:
--   apply ★ (basis x +ⱽ basis (complement x))
--     ≡ apply ★ (basis x) +ⱽ apply ★ (basis (complement x))
--                                                      [preserves-+]
--     ≡ basis (complement x) +ⱽ basis (complement (complement x))
--                                                      [apply-basis × 2]
--     ≡ basis (complement x) +ⱽ basis x        [cong on complement-invol]
--     ≡ basis x +ⱽ basis (complement x)         [+ⱽ-comm]
--
-- Each sd-pair-*-self-dual is then a one-liner: pick x; the
-- right-hand side `basis (complement x)` reduces to the partner
-- basis vector definitionally (complement is concretely defined).
------------------------------------------------------------------------

self-dual-via-complement-pair :
  (x : Fin 6) →
  SelfDual-Pred (basis x +ⱽ basis (complement x))
self-dual-via-complement-pair x =
  trans (preserves-+ hodge-star (basis x) (basis (complement x)))
  (trans (cong₂ _+ⱽ_
                (apply-linear-from-images-basis hodge-star-images x)
                (apply-linear-from-images-basis hodge-star-images (complement x)))
  (trans (cong (basis (complement x) +ⱽ_)
               (cong basis (complement-involution x)))
         (+ⱽ-comm (basis (complement x)) (basis x))))

------------------------------------------------------------------------
-- Each generator is self-dual: one-line application of the combinator.
-- The complement of each x reduces to its partner basis index
-- definitionally, so the resulting goal type matches sd-pair-*.
------------------------------------------------------------------------

sd-pair-01-23-self-dual : SelfDual-Pred sd-pair-01-23
sd-pair-01-23-self-dual = self-dual-via-complement-pair b₀₁

sd-pair-02-13-self-dual : SelfDual-Pred sd-pair-02-13
sd-pair-02-13-self-dual = self-dual-via-complement-pair b₀₂

sd-pair-03-12-self-dual : SelfDual-Pred sd-pair-03-12
sd-pair-03-12-self-dual = self-dual-via-complement-pair b₀₃

------------------------------------------------------------------------
-- Closure of self-dual under +ⱽ.
--
-- If ω₁ and ω₂ are self-dual, so is ω₁ +ⱽ ω₂. Follows directly from
-- hodge-star's linearity (preserves-+).
------------------------------------------------------------------------

sd-closed-+ⱽ :
  (ω₁ ω₂ : Bivector) →
  SelfDual-Pred ω₁ → SelfDual-Pred ω₂ →
  SelfDual-Pred (ω₁ +ⱽ ω₂)
sd-closed-+ⱽ ω₁ ω₂ sd₁ sd₂ =
  trans (preserves-+ hodge-star ω₁ ω₂)
        (cong₂ _+ⱽ_ sd₁ sd₂)

------------------------------------------------------------------------
-- Closure of self-dual under scalar multiplication.
--
-- If ω is self-dual, so is c *ₛ ω. Follows from hodge-star's preserves-*ₛ.
------------------------------------------------------------------------

sd-closed-*ₛ :
  (c : F₂) (ω : Bivector) →
  SelfDual-Pred ω → SelfDual-Pred (c *ₛ ω)
sd-closed-*ₛ c ω sd =
  trans (preserves-*ₛ hodge-star c ω)
        (cong (c *ₛ_) sd)

------------------------------------------------------------------------
-- The zero bivector is self-dual (trivially).
------------------------------------------------------------------------

sd-zero : SelfDual-Pred 𝟎ⱽ
sd-zero = preserves-𝟎 hodge-star
