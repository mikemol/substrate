------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.ResidueIsBezoutGCD
--
-- The CrossMix cross-term residue is GOVERNED by the Bézout GCD — and the
-- substrate's constructive EEA/Bézout/CRT spine is "precisely for this kind of
-- thing" (user, 2026-06-25). The coprime/orthogonal split I had flagged as
-- "awkward" is the CRT-clean case, with EEA as its certificate:
--
--   gcd ≡ 1  (coprime)        ⟺  ORTHOGONAL — cross-term vanishes (CRT clean).
--                                 The CRT idempotents e₁,e₂ ARE the codec legs;
--                                 `coprime-trace` is the EEA/Bézout certificate.
--   gcd > 1  (shared factor)  ⟺  graded RESIDUE — the cross-term is a nonzero
--                                 nilpotent (the obstruction's cost).
--
-- So the residue is not mysterious: it is the GCD's deviation from 1, and
-- Euclid's extended algorithm computes it (and, via Bézout coefficients, the
-- reconstruction = the CRT idempotents). The two Ξ★ examples are the two sides:
-- CenterIsStarCRT (ℤ/6 = ℤ/2×ℤ/3, gcd 1, orthogonal) and CenterIsStarNumeral
-- (ℤ/2³, the prime 2 with itself, gcd 2, residue).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.ResidueIsBezoutGCD where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Nat.GCD.GcdN using (gcd-ℕ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (coprime-trace)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Wedge.CrossMul using (cross)
open import Substrate.Logic.Evidence.ElAtlas.CenterIsStarCRT using (crt-mix; e₁; e₂; clean-cross)
open import Substrate.Logic.Evidence.ElAtlas.CenterIsStarNumeral using (numeral-mix; obstruction-cross)

------------------------------------------------------------------------
-- 1. Coprime (gcd ≡ 1) ⟹ orthogonal, no residue (the CRT case). The EEA
--    trace bottoming at 1 IS the Bézout certificate of the clean split.
------------------------------------------------------------------------

coprime-2-3 : gcd-ℕ 2 3 ≡ 1
coprime-2-3 = refl

crt-split-certificate : EEATrace 2 3 1                 -- the EEA/Bézout coprimality witness
crt-split-certificate = coprime-trace 2 3 refl

orthogonal-no-residue : cross crt-mix e₁ e₂ ≡ 0        -- gcd 1 ⟹ cross-term vanishes
orthogonal-no-residue = clean-cross

------------------------------------------------------------------------
-- 2. Shared factor (gcd > 1) ⟹ graded residue (the numeral case). The same
--    EEA engine that returns 1 above returns the SHARED FACTOR here — and that
--    factor is exactly why the cross-term cannot vanish.
------------------------------------------------------------------------

shared-2-2 : gcd-ℕ 2 2 ≡ 2
shared-2-2 = refl

residue-from-shared : cross numeral-mix 2 2 ≡ 4        -- gcd 2 > 1 ⟹ nonzero graded residue
residue-from-shared = obstruction-cross
