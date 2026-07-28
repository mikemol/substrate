------------------------------------------------------------------------
-- Substrate.Category.GenericHodgeStar
--
-- The categorical primitive for the Hodge ★ duality
--   ★ : Λᵏ(V) ≅ Λⁿ⁻ᵏ(V)
-- at full rank n = dim V, where V is equipped with an orientation
-- + inner product (or, in the discrete F₂ case, a chosen pairing).
--
-- L5 of the 20-slice L-arc. Substrate-level generic primitive that
-- the existing HodgeStar at HodgeDim4 (L7's bridge target)
-- instantiates.
--
-- The substrate-level minimum: a bijection between two graded
-- pieces of specified degrees. The "magic" — that it's the unique
-- bijection compatible with the inner-product / orientation — is
-- the universal property the bijection satisfies, captured by the
-- caller's choice of source/target sets.
--
-- Per [[categorical-name-first]]: "Hodge ★" / "Hodge dual" /
-- "Hodge star operator" are standard names. The universal property
-- is "the unique linear isomorphism Λᵏ ≅ Λⁿ⁻ᵏ such that
--   α ∧ (★β) = ⟨α, β⟩ vol"
-- where vol is the volume form. The substrate-level primitive
-- captures the bijection; specific universal-property witnesses
-- (inner-product compatibility) are supplied by concrete instances.
--
-- Per [[reserved-selfdual-bijection-gauge]]: at HodgeDim4, the
-- existing HodgeStar is one of 168 F₂-linear bijections; the
-- GaugeTorsor instance + L7 bridge captures the gauge freedom +
-- the canonical choice as one element of the torsor.
--
-- Per [[expose-generator-not-orbit]]: the orbit (Λ²(F₂⁴) ↔ Λ²(F₂⁴)
-- = the 168 bijections at HodgeDim4) is exposed; the substrate-
-- level primitive names the structure that the orbit inhabits.
--
-- Specific instances:
--   * L7 HodgeStar.AsGenericHodge: HodgeDim4 ★ : F₂⁶ ≅ F₂⁶
--   * Cross product on ℝ³ (deferred; ★ : Λ²ℝ³ ≅ Λ¹ℝ³ = ℝ³)
--   * Electromagnetic ★ in 4d (deferred; ★F is the dual field
--     strength tensor)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.GenericHodgeStar where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op3
open import Substrate.Foundation.Eq using (_≡_)

private
  variable
    ℓK ℓNK : Level

------------------------------------------------------------------------
-- The GenericHodgeStar record.
--
-- Bundles:
--   * n : ℕ — ambient dimension
--   * k : Fin (suc n) — source degree (0 ≤ k ≤ n)
--   * LamK : Set — source graded piece Λᵏ(V)
--   * LamNk : Set — target graded piece Λⁿ⁻ᵏ(V)
--   * star : LamK → LamNk — the Hodge dual
--   * star-inv : LamNk → LamK — the inverse (★² = ±1 depending on
--     signature; the substrate captures only the bijection structure)
--   * section : (x : LamK) → star-inv (star x) ≡ x
--   * retraction : (y : LamNk) → star (star-inv y) ≡ y
--
-- The substrate-level primitive is the bijection structure; concrete
-- universal-property witnesses (inner-product compatibility) layer
-- on top.
------------------------------------------------------------------------

-- ⟡set1-rp-smalltail: LamK/LamNk are PARAMETERS now (set1-carrier-always-parameterize);
-- lsuc drops. n/k stay fields (k's type depends on the field n).
record GenericHodgeStar (LamK : Set ℓK) (LamNk : Set ℓNK) : Set (ℓK ⊔ ℓNK) where
  constructor mkGenericHodgeStar
  field
    n          : ℕ
    k          : Fin (ℕ.suc n)
    star       : LamK → LamNk
    star-inv   : LamNk → LamK
    section    : (x : LamK) → star-inv (star x) ≡ x
    retraction : (y : LamNk) → star (star-inv y) ≡ y

------------------------------------------------------------------------
-- Capstone — generic Hodge ★ primitive in place.
--
-- L5 of the L-arc. Closes the L1-L5 "phase Λ" cluster:
--   L1 ACA      — anti-commutative algebra base
--   L2 LieAlgebra — ACA + Jacobi
--   L3 ExteriorAlgebra — graded ACA + nilpotent at deg-1
--   L4 WedgeProduct — rank-2 ergonomic slice
--   L5 GenericHodgeStar — Λᵏ ↔ Λⁿ⁻ᵏ duality
--
-- After L5: substrate has the categorical primitives for Lie +
-- Grassmann + Hodge structures. The next 5 slices (L6-L10) connect
-- these to existing substrate sites (Bivector, HodgeStar) +
-- introduce morphism layers (per Z-arc Grothendieck-closure pattern).
--
-- Per [[universal-property-discipline]]: the Hodge ★ has multiple
-- universal-property characterisations (inner-product, orientation,
-- volume-form-mediated); the substrate's GenericHodgeStar captures
-- the structural bijection-of-graded-pieces minimum. Concrete
-- instances supply additional universal-property data per their
-- domain (F₂-linearity at HodgeDim4; inner-product preservation at
-- ℝⁿ).
--
-- Next: L6 Bivector.AsExterior (HodgeDim4 instance of L3 + L4).
------------------------------------------------------------------------
