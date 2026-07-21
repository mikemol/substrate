------------------------------------------------------------------------
-- Substrate.WitnessTower.CofreeDual
--
-- Ⓤ.cofree-dual — wiring the terminal-coalgebra (cofree) side of the
-- uniqueness family, the exact dual of the initial-algebra (cata) side.
-- Nothing here is re-derived: the duality is ALREADY established (R.Trace.Final
-- frames RealTrace as the terminal coalgebra, "the exact codual of the Free/
-- initial centre, one adjoint hinged by Lawvere", with `ana-unique` proven).
-- This module NAMES the dual pair in one place and makes the EEATrace-`≡`
-- refinement concrete.
--
--   INITIAL (data, induction, `≡`):  eea-fold-unique  (Nat.GCD.Fold)
--   TERMINAL (codata, corecursion, `~`):  ana-unique  (R.Trace.Final)
--   same functor S(X) = ℕ × X; the ℚ ⊣ ℝ adjunction (RationalAdjunction) bridges.
--
-- The `≡`-via-generator point (the cofree `~`-side is NOT the only equality):
-- a finitely-generated real's equality is DECIDED on its finite inductive CF
-- generator by `≡`, never on the stream by `~`. `generator-recovers` (the unit,
-- new here = `eea-unit ∘ gcd-trace`) shows ℚ→ℝ→ℚ recovers the seed by `≡`;
-- `μ↔ν-prefix` (digit-agreement) bridges the finite digits to the stream prefix;
-- `generator-faithful` (cf-injective) shows the CF shape DETERMINES the value by
-- `≡`. So the `~`-cofree obstruction shrinks to the non-finitely-generated tail.
--
-- Zero postulates, --safe --without-K --guardedness (infective via R.Trace).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.WitnessTower.CofreeDual where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Nat.GCD.Fold using (eea-fold-unique)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (gcd-trace)
open import Substrate.Algebra.Nat.GCD.CFInjective using (cf-injective)
open import Substrate.Algebra.R.Trace.Final using (ana-unique)
open import Substrate.Algebra.R.Trace.RationalAdjunction using (reconstruct; eea-unit)
open import Substrate.WitnessTower.EEATower using (digit-agreement)
open import Substrate.Algebra.Wedge.NuShapeIso using (shape-is-canonical)
open import Substrate.Algebra.Wedge.Shape.Double.InternedEffectivity using (corr⇔addr)

------------------------------------------------------------------------
-- 1. The dual pair, named in one place.
------------------------------------------------------------------------

-- the INITIAL-algebra ∃! (cata, up to `≡`).
cata-uniqueness = eea-fold-unique

-- the TERMINAL-coalgebra ∃! (ana, up to `~`) — the cofree dual.
cofree-uniqueness = ana-unique

------------------------------------------------------------------------
-- 2. The `≡`-via-generator handles (the cofree `~` is not the only equality).
------------------------------------------------------------------------

-- THE UNIT (new): the ℚ → ℝ → ℚ round-trip recovers the seed by `≡` (not `~`) —
-- equality of a finitely-generated real is decided on its finite CF generator.
generator-recovers : (a b : ℕ) → reconstruct (gcd-trace a b) ≡ (a , b)
generator-recovers a b = eea-unit (gcd-trace a b)

-- the finite μ-digits ARE the first cf-length digits of the coinductive stream.
μ↔ν-prefix = digit-agreement

-- the CF shape DETERMINES the (coprime) value by `≡` — the generator is faithful,
-- so the cofree `~`-side reduces to `≡` wherever the generator is finite.
generator-faithful = cf-injective

------------------------------------------------------------------------
-- 3. THE ν-SIDE AT FINITE GRADE — the interner (⟡sppf-quotient-coapex).
--
-- The μ⊣ν pair above is determination (unique map OUT of the initial algebra)
-- against identification (identity IN the terminal coalgebra, where `~` IS
-- equality). The INTERNER is the identification half read at FINITE grade:
--
--   Corr t₁ t₂ = shape t₁ ≡ shape t₂          -- kernel of the shape-projection
--   corr⇔addr                                  -- that kernel IS address-equality
--
-- ⚑ AN EARLIER VERSION OF THIS PARAGRAPH SAID `NuShapeIso` "is what makes this
-- one structure rather than an analogy". THAT WAS AN OVERCLAIM — and the worse
-- of the two I shipped, because it explicitly DENIED the analogy status that is
-- in fact exactly what remains. What `NuShapeIso` actually supplies is the ν
-- side: `shape-is-canonical` IS `ana-unique (quotient-coalg co)`, the canonicity
-- of the INFINITE projection. It ASSERTS the finite↔infinite same-projection
-- identity in prose (`NuShapeIso:12,:91`) but never imports
-- `Substrate.Algebra.Wedge.Shape` — all six of its terms are on the infinite
-- side — so nothing wires the two grades together. Until ⟡corr-as-finite-bisim
-- lands, "one structure rather than an analogy" is THE TARGET OF THIS FILE, not
-- a fact it can cite.
--
-- So the interner's effectivity is not a third instance of the μ-side
-- uniqueness shape (see UniquenessBridge for that naming boundary) — it is the
-- ν side, finitely. Recorded here because THIS is where the dual pair lives.
------------------------------------------------------------------------

-- the ν-uniqueness of the shape-projection (= ana-unique at the quotient coalgebra).
shape-projection-uniqueness = shape-is-canonical

-- the same projection at FINITE grade: its kernel is exactly address-equality.
interner-effectivity = corr⇔addr
