{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.JacobianNegCodec — ⟡jac-neg-route-B.
--
-- ROUTE B of ⟡jac-neg-three-routes: the LOG/EXP GAUGE — the RULED-PREFERRED
-- one. Negation is neither fielded (Route A) nor transposed (Route C) but
-- TRANSPORTED: log to the multiplicative side, involute about 𝟙, antilog back.
-- The carrier never acquires an inverse.
--
--     x ⊕ neg x ≡ 𝟘        (additive, on the log side)
--     expL x · expL (neg x) ≈ 𝟙   (multiplicative, on the exp side)
--
-- `ExpLogCodec.agda:47-56` states the conclusion outright: "the reciprocal
-- involution IS the additive negation transported by exp; no
-- multiplicative-inverse axiom is needed, it is DERIVED."
--
-- ⚑ WHY THIS SUBSTRATE PREFERS IT. The four job gauges (ℕ/F₂/Bool/tropical,
-- `Semiring/Instances.agda`) are defined by carriers WITHOUT additive inverses.
-- Route A must climb to a ring to get negation; Route B keeps the semiring and
-- obtains the inverse STRUCTURALLY, by transport across the +↔× bridge.
--
-- ⚑⚑ THE COLLAPSE IS REAL, AND THE POLE IS WHAT EXCLUDES IT.
-- `ZPow` is parameterized `(g h : ℚ) (gh : g *ℚ h ≈ℚ 1ℚ)` with
-- `expℤ (+ n) = powℚ g n`, `expℤ (-suc n) = powℚ h (suc n)`. At `g = h = 1ℚ`
-- the hypothesis HOLDS and `expℤ` is CONSTANTLY 1ℚ — a codec transporting
-- nothing. So the codec's existence proves nothing on its own; only a
-- DISCRIMINATION witness at the chosen base does. Hence §3.
--
-- ⚑ AND A CAVEAT ABOUT AN EXISTING WITNESS. `Primes.agda:222`
-- `ℤpow-antipode-fires` is commented "the codec fires NON-trivially" — that
-- refers to the EXPONENT cancelling (`+1 ⊕ -1 = 𝟘`, unlike ℕ-power-codec's
-- degenerate `0+0`), NOT to the base. It holds at `g = h = 1ℚ` too, so it is
-- NOT a base-level discrimination witness and must not be cited as this route's
-- pole. (Probed.)
--
-- Zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.JacobianNegCodec where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Q using (ℚ; mkℚ; 1ℚ; -1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Logic.Evidence.GValueLSpace.Primes using (module ZPow)

------------------------------------------------------------------------
-- 1. A NON-TRIVIAL BASE — (2, ½).
--
-- `g *ℚ h ≈ℚ 1ℚ` holds by `refl`: `_≈ℚ_` is cross-multiplication over the
-- UNNORMALIZED pair `mkℚ (num : ℤ) (den-1 : ℕ)`, so 2/1 · 1/2 = 2/2 ≈ 1/1.
------------------------------------------------------------------------

2ℚ half : ℚ
2ℚ   = mkℚ (+ 2) 0      -- 2/1
half = mkℚ (+ 1) 1      -- 1/2

base-inverse : (2ℚ *ℚ half) ≈ℚ 1ℚ
base-inverse = refl

open ZPow 2ℚ half base-inverse using (expℤ; ℤ-power-codec)

------------------------------------------------------------------------
-- 2. THE DETERMINANT'S NEGATION, TRANSPORTED.
--
-- `Algebra.Z.JacobianResidue.constant-part` gives `det Jac F ≡ −2` over ℤ. The
-- ADDITIVE fact that −2 and +2 cancel becomes, through the codec, the
-- MULTIPLICATIVE fact that their images are reciprocals in ℚ:
--     expℤ (−2) · expℤ (+2)  =  ¼ · 4  ≈ℚ  1ℚ
-- The inverse is never added to ℤ; it is read off the exp side.
------------------------------------------------------------------------

route-B : (expℤ (-suc 1) *ℚ expℤ (+ 2)) ≈ℚ 1ℚ
route-B = refl

------------------------------------------------------------------------
-- 3. THE MANDATORY POLE — the codec at THIS base actually separates.
--
-- Without this, §2 is satisfied by the collapsed codec (where every product is
-- 1ℚ because every image is 1ℚ) and says nothing.
------------------------------------------------------------------------

codec-discriminates : expℤ (+ 1) ≈ℚ expℤ (-suc 0) → ⊥
codec-discriminates ()

------------------------------------------------------------------------
-- 4. A SECOND INSTANCE — THE SIGN CODEC, AND WHY THE POLE IS INSTANCE-RELATIVE.
--
-- At base (−1, −1), `expℤ z = (−1)^z`: the PARITY gauge. This is the
-- instantiation the Jacobian's sign structure wants — `JacobianResidue.agda:
-- 197-199` each carry exactly one `kP (-suc 0)` factor and `:194-196` none,
-- i.e. the S₃ sign character.
--
-- ⚑ ITS POLE IS A DIFFERENT STATEMENT. The sign codec does NOT separate +1 from
-- −1 (both are odd, both map to −1ℚ) — and that is CORRECT for a parity gauge,
-- not a defect. What it separates is EVEN from ODD. So §3's pole would be FALSE
-- here, and this one would be uninformative at base (2,½). A route's
-- discrimination witness belongs to its instance, never to the record.
------------------------------------------------------------------------

neg-one-squared : (-1ℚ *ℚ -1ℚ) ≈ℚ 1ℚ
neg-one-squared = refl

module Sign = ZPow -1ℚ -1ℚ neg-one-squared

sign-codec : ℤ → ℚ
sign-codec = Sign.expℤ

-- the parity gauge separates even from odd — (−1)⁰ = 1 vs (−1)¹ = −1.
sign-discriminates : sign-codec (+ 0) ≈ℚ sign-codec (+ 1) → ⊥
sign-discriminates ()

------------------------------------------------------------------------
-- 5. HONEST SCOPE.
--
-- (a) §2 transports the CONSTANT coefficient's negation. It does NOT re-derive
--     `det Jac F ≡ −2`; that is `JacobianResidue`'s, over ℤ. Route B is a gauge
--     ON the sign/negation structure, not a replacement for the coefficient
--     arithmetic — which lands back on ℤ.
-- (b) The base (2,½) is a CHOICE. Any `(g,h)` with `g *ℚ h ≈ℚ 1ℚ` and `g ≉ℚ h`
--     serves; the collapsed base is excluded by §3, not by the type.
-- (c) This is one gauge of three (A: `Algebra.Z.CommRing`; C:
--     `Algebra.Z.JacobianNegSemiring`). Their equivalence is ⟡jac-neg-cover,
--     whose apex is an `ExpLogCodec ℤ` with each route derived THROUGH it and a
--     mandatory `trivial-codec` (G = ⊤) vacuity pole — the cover-level analogue
--     of §3.
------------------------------------------------------------------------
