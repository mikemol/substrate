------------------------------------------------------------------------
-- Substrate.Algebra.GL3F2
--
-- GL(3, F₂) — the general linear group of order 168 = 2³·3·7. Defined
-- here as a thin record over Linear 3 3 bundling a linear map with an
-- inverse witness (two-sided pointwise inverse).
--
-- Per [[multi-route-equivariance-recovery]] +
-- [[klein-quartic-kinematic-anatomy]]: (Classically GL(3,F₂) ≅ PSL(2,7),
-- simple of order 168 — cited, NOT formalized here.) The substrate's
-- multi-route equivariance arc generates
-- it from three Sylow-canonical witnesses (one each from Sylow-2,
-- Sylow-3, Sylow-7). The full 168-element enumeration is OUT of scope
-- for this slice; this module provides only the type, group operations,
-- and the HasOrder-Linear convenience for the per-generator order proofs
-- that S4/S5 will use.
--
-- Per [[prefer-coxeter-backed]]: GL(3, F₂) is not natively a Coxeter
-- group, but its Sylow generators ARE Coxeter-backed (Sylow-3 via
-- Z3-Coxeter; Sylow-7 via Z7-Coxeter; Sylow-2 via the existing
-- Permutation-Axis S₄ — Coxeter-backed S₄ via A₃ presentation is a
-- queued follow-on slice). Composition here is Linear composition, not
-- word concatenation; downstream perf optimization (Coxeter-backed
-- composition) is the follow-on.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.GL3F2 where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector)
open import Substrate.Algebra.F2.Linear using (Linear; id-L; _∘L_; apply)
open import Substrate.Category.Coalgebra.FiniteOrder
  using (iterate; HasOrder)

------------------------------------------------------------------------
-- 1. GL3F2 — F₂-linear endomorphism of Vector 3 with a two-sided
-- pointwise inverse.
------------------------------------------------------------------------

record GL3F2 : Set where
  constructor mkGL3F2
  field
    L      : Linear 3 3
    L⁻¹    : Linear 3 3
    L-left : (v : Vector 3) → apply L⁻¹ (apply L v) ≡ v
    L-right : (v : Vector 3) → apply L (apply L⁻¹ v) ≡ v

open GL3F2 public

------------------------------------------------------------------------
-- 2. Identity element.
------------------------------------------------------------------------

id-GL : GL3F2
id-GL = mkGL3F2 id-L id-L (λ _ → refl) (λ _ → refl)

------------------------------------------------------------------------
-- 3. Composition: g ·G h applies h first, then g. Inverse is built
-- from the per-component inverses in reverse order.
------------------------------------------------------------------------

infixl 7 _·G_

_·G_ : GL3F2 → GL3F2 → GL3F2
g ·G h = mkGL3F2
  (L g ∘L L h)
  (L⁻¹ h ∘L L⁻¹ g)
  (λ v →
    trans (cong (apply (L⁻¹ h)) (L-left g (apply (L h) v)))
          (L-left h v))
  (λ v →
    trans (cong (apply (L g)) (L-right h (apply (L⁻¹ g) v)))
          (L-right g v))

------------------------------------------------------------------------
-- 4. Inverse: just swap L and L⁻¹.
------------------------------------------------------------------------

_⁻¹G : GL3F2 → GL3F2
g ⁻¹G = mkGL3F2 (L⁻¹ g) (L g) (L-right g) (L-left g)

------------------------------------------------------------------------
-- 5. Pointwise application — applies the underlying Linear's apply.
------------------------------------------------------------------------

applyG : GL3F2 → Vector 3 → Vector 3
applyG g = apply (L g)

------------------------------------------------------------------------
-- 6. HasOrder for Linear maps: convenience wrapper around HasOrder on
-- (apply L : Endomap (Vector 3)). Used by S4/S5 to state per-generator
-- orders (Sylow-2 generator has order 2; Sylow-3 has order 3;
-- Sylow-7 = singer has order 7).
------------------------------------------------------------------------

HasOrder-Linear : Linear 3 3 → ℕ → Set
HasOrder-Linear L k = HasOrder (apply L) k

HasOrder-GL : GL3F2 → ℕ → Set
HasOrder-GL g k = HasOrder-Linear (L g) k

------------------------------------------------------------------------
-- 7. Iteration of a GL3F2 element via composition (alternative form;
-- equivalent to iterate on apply via the canonical iso under funext
-- — stated pointwise here per substrate discipline).
------------------------------------------------------------------------

iterateG : ℕ → GL3F2 → GL3F2
iterateG zero    _ = id-GL
iterateG (suc n) g = g ·G iterateG n g

------------------------------------------------------------------------
-- 8. Helper: an element's order is the smallest n with iterate n (apply L)
-- ≡ id pointwise. This is the structural fact `HasOrder-GL g k` from §6.
-- The substrate's [[3plus1-parity-universal]] / FLT-for-dimensional-spaces
-- framing applies: every finite-order element of GL3F2 carries its own
-- local cyclic subgroup Z/k.
--
-- The 168-element group's element orders divide |G| = 168 (Lagrange);
-- since GL(3, F₂) ≅ PSL(2, 7) is simple, the element orders are
-- divisors of 168 with the additional structural constraints of PSL(2, 7):
-- orders ∈ {1, 2, 3, 4, 7}. (Verifiable downstream — out of scope.)
------------------------------------------------------------------------
