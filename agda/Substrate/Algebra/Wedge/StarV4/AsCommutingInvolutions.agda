------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.StarV4.AsCommutingInvolutions
--
-- StarV4's ⟨recip, bar⟩ IS Lawvere's `CommutingInvolutions` — the bridge, not
-- a re-derivation.
--
-- ⚑ EVERY OBLIGATION WAS ALREADY DISCHARGED; only the packaging was missing.
-- `Category.Lawvere.CommutingInvolutions` (:200-205) asks for δ₁ δ₂ with
-- δ₁-inv, δ₂-inv, commute.  `StarV4` proves exactly those four, under its own
-- names, and has since it was written:
--
--     δ₁      = recip        (the dagger † / fraction-level inverse)   StarV4:74
--     δ₂      = bar          (the conjugation twist)                   StarV4:77
--     δ₁-inv  = recip-recip                                            StarV4:80
--     δ₂-inv  = bar-bar                                                StarV4:83
--     commute = recip-bar    (the V₄-not-dihedral condition)           StarV4:88
--
-- ⚑ AND `Lawvere` NAMED THIS AS OWED.  :196-197 — *"(Literal iso to the
-- Coxeter-backed V₄ / V4Seam's klein-pairs, and the F₂² instance with its
-- freeness, are the next bridge.)"*  This lands the first half: the literal
-- `CommutingInvolutions` instance from the star structure.  The freeness half
-- is NOT landed here and is discussed below.
--
-- ⚑ WHAT THIS BUYS.  `CommutingInvolutions` derives `δ₁₂` and proves `δ₁₂-inv`
-- (:208-217) — the composite of two commuting involutions is an involution, so
-- {id, δ₁, δ₂, δ₁₂} CLOSES.  That is the Klein four, and StarV4's own header
-- (:16-18) asserts exactly that closure in prose: *"⟨†, bar⟩ ≅ ℤ/2 × ℤ/2 … The
-- fourth element † ∘ bar is the transpose/adjoint."*  Before this bridge that
-- was a prose claim; after it, `δ₁₂-inv` is a term.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.StarV4.AsCommutingInvolutions where

open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.StarV4
open import Substrate.Category.Lawvere using (CommutingInvolutions)
open import Substrate.Algebra.Q.HetBasisNest
open import Substrate.Category.UniversalProperty.ExtrudeCoEmitGraded.Bar
open import Substrate.Algebra.Nat.GCD.EEATrace

------------------------------------------------------------------------
-- The bridge.  Parameterized exactly as StarV4 is — carrier, its DivStr, and
-- the star structure over it — so the instance exists for EVERY *-carrier, not
-- one chosen example.
------------------------------------------------------------------------

module _ {C : Set} (base : DivStr C) (S : StarDivStr base) where

  star-V₄ : CommutingInvolutions (Frac base S)
  star-V₄ = record
    { δ₁      = recip base S
    ; δ₂      = bar base S
    ; δ₁-inv  = recip-recip base S
    ; δ₂-inv  = bar-bar base S
    ; commute = λ f → recip-bar base S f
    }

------------------------------------------------------------------------
-- ⚑ WHAT IS *NOT* HERE, AND WHY — the freeness half.
--
-- `CommutingInvolutions` asks only that the two flips be involutions and
-- COMMUTE.  It does NOT ask that they be fixed-point-FREE, and StarV4's pair is
-- not: `recip (a , a) ≡ (a , a)`, so the dagger fixes the whole diagonal, and
-- `bar` fixes every self-conjugate fraction (over plain ℚ, where conj = id,
-- bar is the IDENTITY — StarV4:12-14 says so).
--
-- So this instance is a V₄ but NOT a gauge V₄ in Lawvere's §6 sense
-- (:220-224): the discriminator `fpf-≠-has-fixpoint` (:227) exists precisely to
-- separate "all flips free" from "extra generators fix points", and StarV4's
-- pair lands on the fixing side.  Claiming `FixedPointFree` here would be
-- false, and the honest instance is the weaker record that is actually
-- inhabited.
--
-- ⚑ THAT IS A FINDING, NOT A GAP.  `Lawvere:191-193` expects the free V₄ at
-- V = F₂² (the tetrahedron's four vertices, coordinate translations), and
-- `WitnessTower.Diagonal:153,198` already carries `F₂²-V₄` and `interface-V₄`
-- for that carrier.  Two DIFFERENT V₄'s over two different carriers, one free
-- and one fixing — which is exactly the distinction §6 was written to make.
------------------------------------------------------------------------
