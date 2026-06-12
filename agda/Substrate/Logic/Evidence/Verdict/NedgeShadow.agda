------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Verdict.NedgeShadow
--
-- The bridge to the ancestor (el-atlas move #2). Nedge is, ultimately,
-- about HOLONOMY — the phase obstruction (§8.5/§8.6; the H² class in
-- .Phase). Its G-Value Calculus (the Drive Agda spec, module
-- NedgeGCalculus) reads each conduit as a single SCALAR G-value, negation
-- by reciprocal (G-NOT p = 1/p).
--
-- The dual-rail carrier (E⁺,E⁻) is an UPGRADE to Nedge that does NOT force
-- it to change: it expresses the same conduit as a structured, manipulable
-- VECTOR rather than one scalar. Nedge is PRESERVED, not replaced — its
-- scalar reading is recovered here as the bias projection b = E⁺ − E⁻
-- (Nedge's balance point G = 1 is b = 0; cf. §8.6's biasShadow : V4 → ℤ₂).
-- Nothing is taken from Nedge; structure is added.
--
-- What the upgrade BUYS, made precise: a scalar has no direction, so it
-- cannot carry holonomy. The bias projection tells P (net for) from F (net
-- against) but reads the same balanced value for U (conflict) and V
-- (ignorance), so it cannot reconstruct the four-valued verdict on its own
-- (`bias-cannot-carry-verdict`, via NoCollapse.faithful-separates). That is
-- not a defect of Nedge — it is the expressive gain of the vector form: the
-- vector carries exactly what the scalar projects away (the U/V distinction,
-- and with it the V₄-phase of .Phase that IS the holonomy Nedge is after).
--
-- (This also answers OB-6 / spec line-1987: where NedgeGCalculus POSTULATES
-- its scalar carrier and proves no law in Agda, the vector form — the whole
-- Verdict.* tier this imports — is concrete, zero-postulate, with its laws
-- machine-checked; ℚ-Canonical is the same discipline for a number system.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Verdict.NedgeShadow where

open import Substrate.Foundation.Bool  using (true; false)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Eq    using (_≡_; refl)

open import Substrate.Logic.Evidence.Verdict
  using (Evidence; ⟨_,_⟩; Verdict; verdict; eU; U≢V)
open import Substrate.Logic.Evidence.Verdict.NoCollapse using (faithful-separates)

------------------------------------------------------------------------
-- Nedge's single-rail reading, recovered as a PROJECTION of the dual-rail
-- vector: the bias / net-conductance coordinate b = E⁺ − E⁻. Nedge's G = 1
-- (the galvanometer balance) is b = 0. (Total on Evidence — Nedge loses
-- nothing; the vector simply also retains what bias forgets.)
------------------------------------------------------------------------

data Bias : Set where
  net+ net0 net- : Bias   -- net-for (G>1) / balanced (G=1) / net-against (G<1)

bias : Evidence → Bias
bias ⟨ true  , false ⟩ = net+   -- P: for, none against      → G > 1
bias ⟨ false , true  ⟩ = net-   -- F: against, none for       → G < 1
bias ⟨ true  , true  ⟩ = net0   -- U: both — balances at G = 1
bias ⟨ false , false ⟩ = net0   -- V: neither — also G = 1   ← the conflation

-- the V corner (neither rail).
eV : Evidence
eV = ⟨ false , false ⟩

------------------------------------------------------------------------
-- By refl, the projection sends both U (conflict) and V (ignorance) to the
-- same balanced value — a scalar has no room for the distinction (§5.7).
-- This is precisely the structure the vector upgrade adds back, not a flaw.
------------------------------------------------------------------------

bias-conflates-U-V : bias eU ≡ bias eV
bias-conflates-U-V = refl

------------------------------------------------------------------------
-- THE BRIDGE: the scalar projection cannot reconstruct the verdict on its
-- own. No decoder recovers the four-valued verdict from the bias alone,
-- because the projection sends two distinctly-judged corners (U ≠ V) to one
-- value. This is `no-single-rail-quotient` instantiated against Nedge's own
-- reading — the exact measure of what the structured-vector upgrade adds,
-- and why the holonomy (the V₄-phase) lives on the vector, not the scalar.
------------------------------------------------------------------------

bias-cannot-carry-verdict :
  (d : Bias → Verdict) → ((e : Evidence) → d (bias e) ≡ verdict e) → ⊥
bias-cannot-carry-verdict d h =
  faithful-separates bias d h {eU} {eV} U≢V bias-conflates-U-V
