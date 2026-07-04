{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilAbstract — ⟡uniqueness-stencil-abstract:
-- the GENERIC uniqueness stencil over ANY Lawvere fixed-point, cross-form. The cross-form
-- difficulty (the two framings' carriers differ — Trace/RealTrace coinductive vs Kleene
-- Fam) is DISSOLVED by the arrow-category / HetQ CROSS pattern (Algebra.Q.HetBasis,
-- Algebra.Wedge.CrossMul): DON'T unify the carriers — abstract over them POLYMORPHICALLY
-- as two legs of a COSPAN into a common frame R, and let the stencil's agreement be the
-- CROSS-equality (num·den' vs num'·den, meeting in R), refl/sym GENERIC, the one nontrivial
-- law (the hinge) supplied PER INSTANCE.
--
-- THE PARALLEL (grounded, HetBasis.CrossEq): HetQ A B = (hnum : A, hden : B) — two
-- components in DIFFERENT carriers; _≈H_ p q = (hnum p ⊗ hden q) ≈R (hnum q ⊗ hden p) — the
-- cross-equality into common R, refl/sym generic, trans = the carrier's cross-cancellation
-- per instance. For the stencil: the two FRAMINGS are the two carriers (A = the ≡/algebraic
-- framing, B = the ~/Kleene framing), ⊗/cross = the frame-agreement into a common frame R,
-- ≈R = the hinge relation. The per-source layers (μ-fold, ν-step) are the ≡ legs; the
-- ν-whole (map-level) layer is the CROSS relation itself — abstracted, not carrier-unified.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilAbstract where

open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)

------------------------------------------------------------------------
-- ① THE GENERIC STENCIL as a HetQ-style COSPAN (mirroring HetBasis.CrossEq EXACTLY):
-- two framings in DIFFERENT carriers A, B, each crossing into a common frame R via ⊗, with
-- the frame-relation ≈R — all as MODULE PARAMETERS (not record fields), the HetQ shape. A
-- and B are NOT unified — they are two legs of a cospan (the arrow-category dissolution).
------------------------------------------------------------------------
module StencilAgreement {A B R : Set}
  (_⊗_    : A → B → R)                        -- CrossMul's `cross` (frame-A × frame-B → R)
  (_≈R_   : R → R → Set)                      -- the frame-relation (the hinge's target)
  (≈R-refl : {r : R} → r ≈R r)
  (≈R-sym  : {r s : R} → r ≈R s → s ≈R r)
  where

  -- a stencilled object: an A-framing and a B-framing of the SAME fixed-point (HetQ A B).
  record Framed : Set where
    field  fA : A ; fB : B
  open Framed public

  -- the two framings AGREE: the cross terms match in R (the HetQ.CrossEq _≈H_ shape).
  _agrees_ : Framed → Framed → Set
  p agrees q = (fA p ⊗ fB q) ≈R (fA q ⊗ fB p)

  -- refl / sym are GENERIC (from ≈R's), exactly HetQ.CrossEq's generic half.
  agrees-refl : (p : Framed) → p agrees p
  agrees-refl p = ≈R-refl

  agrees-sym : {p q : Framed} → p agrees q → q agrees p
  agrees-sym e = ≈R-sym e

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the cross-form difficulty DISSOLVED by the arrow-category
-- / HetQ cross pattern, NOT by carrier unification): the generic uniqueness stencil is a
-- COSPAN StencilCospan A B R — the two framings live in DIFFERENT carriers A, B (the ≡/
-- algebraic and ~/Kleene sides, or Trace/RealTrace vs Fam), and are related NOT by unifying
-- them but by CROSSING into a common frame R (⊗ = CrossMul's cross), with agreement the
-- cross-equality (StencilAgreement._agrees_, the HetQ.CrossEq shape: fA p ⊗ fB q ≈R fA q ⊗
-- fB p). refl/sym are GENERIC; the hinge (trans / the nontrivial cross-cancellation) is
-- supplied PER INSTANCE — exactly as HetBasis does for ℚ. So the either/or "unify the
-- carriers (Trace vs Fam) OR give up on a generic module" DISSOLVES: the arrow-category
-- framing abstracts over the carriers POLYMORPHICALLY (two cospan legs), and the stencil's
-- agreement is their cross — the per-source layers (μ-fold, ν-step) are the ≡ legs, the
-- ν-whole map-level layer is the cross relation itself. This is why the repo is grounded in
-- arrow categories + allegory + the CrossMul/HetQ pattern: heterogeneous objects are related
-- through a common frame, never forcibly identified. The concrete stencil instances
-- (FixpointStencilRecord's TwoFraming, the Fam-form) are the R = Fam specialization; the
-- coinductive Trace/RealTrace framing is another cospan leg into the same generic shape.
------------------------------------------------------------------------
