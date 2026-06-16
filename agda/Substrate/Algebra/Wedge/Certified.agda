------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Certified
--
-- SLICE 5: the CERTIFIED wedge, generic — the one keystone-#1 bit that was
-- ℕ-only (the r<b smallness, via Algebra.Nat.GCD.Wedge) lifted to an interface
-- over any carrier with a ℕ-valued MEASURE. A certified wedge is a loose wedge
-- (Algebra.Wedge.Wedge) plus a proof that the RESIDUE'S measure is strictly
-- smaller than the divisor's — the well-founded measure that makes recursive
-- factoring terminate.
--
--   * CertifiedWedge D measure a b — the certified triple.
--   * residue-decreases — the measure strictly decreases (the termination
--     measure; the certified residue is the smallest KEPT correction —
--     never-drop + smallness together).
--   * fromℕ-cert — the ℕ-GCD Wedge is the canonical instance (measure = id,
--     smallness = its own r<b).
--
-- MEASURE = GRADE: for a flattened graded product (Product.flatten, carrier
-- Σ ℕ C), the natural measure is proj₁ — the GRADE. So "certified residue =
-- the grade strictly decreases" is the graded reading; constructing such wedges
-- needs the carrier's Euclidean structure (the ℕ-GCD instance is the worked
-- one; per-carrier division is the per-carrier extension).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Certified where

open import Substrate.Foundation.Nat using (ℕ; _<_)
open import Substrate.Algebra.Wedge using (DivStr; C; rem; fromℕ-Wedge; ℕ-div)
  renaming (Wedge to Wedge⟦478f66a6⟧)
import Substrate.Algebra.Nat.GCD.Wedge as N

------------------------------------------------------------------------
-- 1. The certified wedge: a loose wedge whose residue's measure is smaller.
------------------------------------------------------------------------

record CertifiedWedge (D : DivStr) (measure : C D → ℕ) (a b : C D) : Set where
  field
    wedge : Wedge⟦478f66a6⟧ D a b
    small : measure (rem wedge) < measure b

open CertifiedWedge public

-- the certified residue's measure strictly decreases — the termination measure.
residue-decreases : {D : DivStr} {measure : C D → ℕ} {a b : C D} →
                    (w : CertifiedWedge D measure a b) → measure (rem (wedge w)) < measure b
residue-decreases w = small w

------------------------------------------------------------------------
-- 2. The ℕ-GCD wedge is the canonical certified instance: measure = id, the
--    smallness is its own r<b. (The certified-r<b that EEATrace iterates,
--    here as a CertifiedWedge.)
------------------------------------------------------------------------

idℕ : ℕ → ℕ
idℕ n = n

fromℕ-cert : {a b : ℕ} → N.Wedge a b → CertifiedWedge ℕ-div idℕ a b
fromℕ-cert w = record { wedge = fromℕ-Wedge w ; small = N.r<b w }
