------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Reads
--
-- The three reads of the generic wedge ARE the substrate's existing
-- number-theoretic constructions — not merely named after them. Via the
-- embeddings fromEEATrace / fromℕ-Wedge (Algebra.Wedge), the Euclidean
-- trace IS a generic Trace, and:
--
--   * FORGETFUL trace-read  `collapse`  ≡  `gcd-fold`   (forget all quotients
--     → the gcd value; the annihilating fold).            [collapse-is-gcd]
--   * PRESENTED wedge-read  `cell`      ≡  `remainder`   (keep r, drop q →
--     the residue mod b).                                  [cell-is-remainder]
--   * FORGETFUL wedge-read  `forget`    ≡  the dividend a (evaluate q·b+r).
--                                                          [forget-is-dividend]
--   * KEEP trace-read       (= `bezout-ℤ`)  keeps the quotients → the Bézout
--     bridge; the SAME trace, a richer target.            [keep-read]
--
-- So gcd-fold and bezout-ℤ (Fold.agda / Z.Bezout) — the forget-q and keep-q
-- folds — are the two trace-reads of one generic wedge, and `=` / `mod` are
-- its single-wedge reads. The keep/forget axis is the existing code.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Reads where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
open import Substrate.Algebra.Wedge
  using (ℕ-div; collapse; cell; forget; fromEEATrace; fromℕ-Wedge)
open import Substrate.Algebra.Nat.GCD.EEATrace using (EEATrace)
open import Substrate.Algebra.Nat.GCD.Fold using (gcd-fold; gcd-fold-correct)
import Substrate.Algebra.Nat.GCD.Wedge as N
open import Substrate.Algebra.Z.Bezout using (bezout-ℤ)

------------------------------------------------------------------------
-- 1. Forgetful trace-read = gcd-fold (the annihilating fold).
------------------------------------------------------------------------

collapse-is-gcd : {a b g : ℕ} (t : EEATrace a b g) →
                  collapse (fromEEATrace t) ≡ gcd-fold t
collapse-is-gcd t = sym (gcd-fold-correct t)

------------------------------------------------------------------------
-- 2. Presented wedge-read = the remainder (residue mod b).
------------------------------------------------------------------------

cell-is-remainder : {a b : ℕ} (w : N.Wedge a b) →
                    cell (fromℕ-Wedge w) ≡ N.remainder w
cell-is-remainder w = refl

------------------------------------------------------------------------
-- 3. Forgetful wedge-read = the dividend a (evaluate the term).
------------------------------------------------------------------------

forget-is-dividend : {a b : ℕ} (w : N.Wedge a b) →
                     forget (fromℕ-Wedge w) ≡ a
forget-is-dividend w = sym (N.wedge-eq w)  -- forget = q·b+r ; the witness, reversed

------------------------------------------------------------------------
-- 4. Keep trace-read = bezout-ℤ (the bridge; quotients retained).
--    Same EEATrace (= generic Trace via fromEEATrace), richer target.
------------------------------------------------------------------------

keep-read = bezout-ℤ
