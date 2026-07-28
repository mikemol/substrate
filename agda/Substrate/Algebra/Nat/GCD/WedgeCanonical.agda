------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD.WedgeCanonical
--
-- The ℕ wedge as an EXPLICIT instance of the split-idempotent apex
-- (Algebra.Quotient.split-Canonical) — the second concrete instance after
-- UPTerm/≈ᵤ, making "the wedge is a section-based quotient" load-bearing
-- rather than prose (convergence-over-isolation).
--
-- For a fixed nonzero divisor `suc b`:
--   * F = recon-pair  : (q, r) ↦ q·(suc b) + r          — evaluate to the value
--   * s = divide-pair : a ↦ (a div b, a mod b)           — the canonical r<b rep
--   * retract = the wedge-eq read forward: recon-pair (divide-pair a) ≡ a
-- so e = s∘F renormalises an un-normalised (q, r) pair to its r<(suc b) form,
-- and `ker recon-pair` (= "same value") is the quotient it canonicalises. This
-- is the "improper → proper" quotient, structurally the same move as ℚ `reduce`
-- — both `split-Canonical F s retract` with F = evaluate, s = canonical rep.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD.WedgeCanonical where

open import Substrate.Foundation.Nat     using (ℕ; suc; _*_; _+_)
open import Substrate.Foundation.Eq      using (_≡_; sym)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Quotient
open import Substrate.Algebra.Nat.GCD.Wedge
  using (quotient; remainder; wedge-eq)
open import Substrate.Algebra.Nat.GCD.ConstructWedge using (construct-wedge)

module _ (b : ℕ) where    -- the fixed divisor is (suc b)

  -- F: evaluate an un-normalised (quotient, remainder) pair to its value (recon).
  recon-pair : ℕ × ℕ → ℕ
  recon-pair (q , r) = q * suc b + r

  -- s: the canonical division — the unique r < suc b representative.
  divide-pair : ℕ → ℕ × ℕ
  divide-pair a = quotient w , remainder w
    where w = construct-wedge a b

  -- F ∘ s ≡ id: the wedge equation a ≡ q·(suc b)+r read forward. THE retraction.
  recon-divide : (a : ℕ) → recon-pair (divide-pair a) ≡ a
  recon-divide a = sym (wedge-eq (construct-wedge a b))

  -- The wedge IS split-Canonical — exactly like UPTerm/≈ᵤ and ℚ reduce.
  WedgeValue-Quotient : Quotient (ℕ × ℕ) (KerRel recon-pair)
  WedgeValue-Quotient = ker-Quotient recon-pair

  WedgeValue-Canonical : Canonical WedgeValue-Quotient
  WedgeValue-Canonical = split-Canonical recon-pair divide-pair recon-divide
