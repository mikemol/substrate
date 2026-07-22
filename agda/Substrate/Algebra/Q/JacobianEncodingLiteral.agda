{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Q.JacobianEncodingLiteral — ◆jac-gamma aggregator.
--
-- Re-exports the three literal closes
--
--     literalᵢ : (x y z : ℚ) → evalℚ x y z R.fᵢ ≋ C.fᵢ x y z   (i ∈ {1,2,3})
--
-- from the per-witness modules JacobianLiteral1/2/3 (lemma-per-file). The
-- per-module memory cap is a FORCING FUNCTION for proof complexity, so each
-- degree-9 uniqueness-lift γᵢ = homAgree eᵢ lives in its OWN module — and f₁'s
-- (1+xy)³ cube (the heavy one, ~730 MB via the AES-Full abstract-Assemble pattern)
-- is thereby ISOLATED, off f₂/f₃ (~94/77 MB). This aggregator is a thin re-export:
-- its own closure deserializes the tiny per-witness cores; it elaborates nothing,
-- so a consumer wanting all three (the capstone) still sees `literal₁/₂/₃` here.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.Q.JacobianEncodingLiteral where

open import Substrate.Algebra.Q.JacobianLiteral1 public using (literal₁)
open import Substrate.Algebra.Q.JacobianLiteral2 public using (literal₂)
open import Substrate.Algebra.Q.JacobianLiteral3 public using (literal₃)
