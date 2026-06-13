------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.BoundedIso
--
-- CARRY-UP consolidation (user, 2026-06-13): the R-arc re-derivation "closed gaps
-- in the other implementation… now we can carry machinery to a common abstraction
-- and use thin local facades." This is the carry-up.
--
-- `Wedge.Adjunction` proved the hom-iso `Wedge ≅ Term` with `from∘to = refl`, but
-- left `to (from t) ≡ t` open — "recoverable once b is concrete… the non-injective-
-- divisor quirk." And `Algebra.Wedge` flagged `rem < b` (smallness) as "the
-- UNIQUENESS / no-gauge certificate (the certified, natural wedge)" — flagged, not
-- proved. The R-arc proved it at ℕ (`RationalAdjunction.qStep∘reconStep`, via
-- `divmod-unique`). Here that proof is lifted to the wedge/`recon` level where the
-- gap was flagged: for `ℕ-div`, `recon` is INJECTIVE ON BOUNDED RESIDUES, so a
-- bounded ℕ wedge is unique — the certificate, now a theorem at the common
-- abstraction. (`RationalAdjunction`'s step-iso is then a thin coalgebra-dynamics
-- facade of this; `reconStep ≡ recon ℕ-div` is `WedgeBridge.reconStep≡recon`.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.BoundedIso where

open import Substrate.Foundation.Nat     using (ℕ; suc; _<_)
open import Substrate.Foundation.Eq      using (_≡_)
open import Substrate.Foundation.Product using (_×_)
open import Substrate.Algebra.Wedge             using (recon; ℕ-div)
open import Substrate.Algebra.Nat.DivMod.Unique using (divmod-unique)

------------------------------------------------------------------------
-- The no-gauge certificate, at the wedge `recon` level: over ℕ-div, the
-- reconstruction `recon q b r = q·b + r` is injective in (q, r) once the residues
-- are bounded below b (`r < b`). So two bounded wedges of the same value against
-- the same divisor are equal — the uniqueness `Wedge.agda` flagged, proved.
--
-- recon ℕ-div q (suc b) r = q * suc b + r, so this is exactly `divmod-unique`,
-- re-presented at the categorical `recon` interface.
------------------------------------------------------------------------

recon-bounded-unique :
  (q₁ q₂ b r₁ r₂ : ℕ) →
  r₁ < suc b → r₂ < suc b →
  recon ℕ-div q₁ (suc b) r₁ ≡ recon ℕ-div q₂ (suc b) r₂ →
  (q₁ ≡ q₂) × (r₁ ≡ r₂)
recon-bounded-unique q₁ q₂ b r₁ r₂ lt₁ lt₂ eq =
  divmod-unique q₁ q₂ r₁ r₂ b lt₁ lt₂ eq
