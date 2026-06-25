------------------------------------------------------------------------
-- Substrate.Algebra.F2.Linear.SpectralCRT
--
-- Ⓕ.tower-CRT — the spectral tower is NOT prime-only, and the composite order
-- splits via CRT, built from the EEA spine.
--
-- CORRECTION (verified 2026-06-25): `dim-ker-Φσ` was never restricted to prime
-- order. `Φσ {n} = ΦL (σ {n}) (suc n) = geomSum`, whose kernel is the
-- augmentation complement (`aug-dim`, which uses NO primality) — so
--   dim ker Φσ_n  =  (order) − 1  =  Σ_{d | order, d>1} φ(d)
-- for EVERY order, prime, prime-power, or composite. (For prime p this is
-- p−1 = φ(p); for composite n it is the SUM of all proper cyclotomic degrees,
-- not φ(n) — the single Φ_n eigenspace of dim φ(n) needs the cyclotomic
-- divisor-product x^L−1 = ∏_{m|L} Φ_m, which is STILL deferred to Ⓕ.cyclotomic,
-- distinct from Ⓕ.face's done face-action core in Nat.GCD.LcmCoprime.)
--
-- The CRT content lives in the ORDER: for coprime m,k the cyclic order splits
--   ℤ/(m·k)  ≅  ℤ/m × ℤ/k,
-- and that split is a FOLD of the EEA trace — `crt-from-traces` (the substrate's
-- CRT, assembled combine ← idempotents ← inverses ← Bézout) takes exactly the
-- coprime EEA traces the fold-table (Ⓢ.eea-fold-table, `fold-crt`) produces.
-- So the orthogonal CrossMix (gcd≡1) IS the composite-order decomposition.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Linear.SpectralCRT where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.F2.Linear.KernelSpan using (KernelDim)
open import Substrate.Algebra.F2.Linear.SpectralCycle using (Φσ)
open import Substrate.Algebra.F2.Linear.SpectralCycleDim using (dim-ker-Φσ)
open import Substrate.Algebra.Nat.GCD.GcdTrace using (coprime-trace)
open import Substrate.Algebra.Quotient.CRT using (CRT-Witness)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (crt-from-traces)

------------------------------------------------------------------------
-- 1. The spectral kernel dimension is order−1 for ANY order — primality-free.
--    Prime-power order 4 = 2² (NO coprime split) and composite order 6 = 2·3
--    (coprime split) both give dim ker Φσ = order − 1, by the SAME aug-dim.
------------------------------------------------------------------------

tower-order-4 : KernelDim (Φσ {3}) 3        -- order 4 = 2² (prime power): dim ker = 3 = 4−1
tower-order-4 = dim-ker-Φσ {3}

tower-order-6 : KernelDim (Φσ {5}) 5        -- order 6 = 2·3 (composite): dim ker = 5 = 6−1
tower-order-6 = dim-ker-Φσ {5}

------------------------------------------------------------------------
-- 2. The composite order's CRT split, BUILT FROM the EEA coprime traces (the
--    fold-table's CRT fold): ℤ/6 ≅ ℤ/3 × ℤ/2. `crt-from-traces` assembles the
--    full CRT-Witness from the two coprimality traces — no hand-given inverses.
------------------------------------------------------------------------

split-6 : CRT-Witness 2 1                    -- moduli (suc 2, suc 1) = (3, 2): ℤ/6 ≅ ℤ/3 × ℤ/2
split-6 = crt-from-traces {1} {0} (coprime-trace 3 2 refl) (coprime-trace 2 3 refl)
