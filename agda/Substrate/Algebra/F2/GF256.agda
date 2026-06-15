------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256
--
-- GF(2⁸) = F₂[x]/(x⁸+x⁴+x³+x+1), the Rijndael field, as a `Ring` on the
-- byte carrier `Vector 8`. Multiplication `gmul a b = reduce-mod-m (a *P b)`
-- is a THIN SKIN over `Polynomial.RingLaws`' `_*P_`; `reduce-mod-m` is the
-- Horner fold (digit-on-demand), whose only kernel `xtime` (·x mod m) reuses
-- the modulus as data (`m-lo`).
--
-- `reduce-mod-m` is proven a RING HOMOMORPHISM (additive `reduce-+ⱽ`,
-- multiplicative `reduce-*-hom`), so `gmul`'s ring laws are `_*P_`'s laws
-- PULLED THROUGH `reduce` — not re-proven; the graded length-`subst`s vanish
-- at the fixed carrier 8. Built via the fold ⇒ NO polynomial long division.
-- Capstone: `GF256-Ring : Ring (Vector 8)`.
--
-- FIPS-197 §4.2 `{57}·{13}={fe}` holds by `refl` through this `gmul`.
-- The multiplicative inverse (⇒ `Field`) is deferred to the EEA construction.
--
-- This module is a RE-EXPORT HUB; the development is split theorem-per-stage
-- under GF256/ (the `make advise` theorem-per-file idiom):
--   Xtime       §A1   ·x mod m + its two linearity laws
--   Reduce      §A3   the Horner fold + F₂-linearity
--   Expand      §A4   reduce(p*q) = hsum over the left factor
--   Idempotent  §A6   reduce∘reduce = id on a byte; reduce-*-hom
--   Mul         §6e   gmul + comm/distrib (the additive-side laws)
--   MulLaws     §6e   unit/zero/assoc
--   Ring        §6f   GF256-Ring : Ring (Vector 8)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256 where

open import Substrate.Algebra.F2.GF256.Xtime      public
open import Substrate.Algebra.F2.GF256.Reduce     public
open import Substrate.Algebra.F2.GF256.Expand     public
open import Substrate.Algebra.F2.GF256.Idempotent public
open import Substrate.Algebra.F2.GF256.Mul        public
open import Substrate.Algebra.F2.GF256.MulLaws    public
open import Substrate.Algebra.F2.GF256.Ring       public
