------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace
--
-- Ω3-L: the L↔G exp⊣log codec, as STRUCTURE (not analytic value).
-- DEFINITION spine (proof-free closure, per the def/proof separation
-- policy); the theorems live in `GValueLSpace.Properties`.
--
-- `GValueAsQ` (Ω3) derived the el-atlas conductance algebra in ℚ: a G-value
-- is a positive ℚ, balance = 1ℚ, G_NOT = recip, G_OR = +ℚ, G_AND = series,
-- DeMorgan exact. Its SCOPE note flagged L-space (L = ln G) as the next
-- bridge and corrected an OVERREAD: the L↔G iso is the exp⊣log codec, and
-- per [[feedback_trace_inversion_vs_transcendental_limit]] that codec is
-- FORMAL — its transcendence lives only in the VALUE projection (the digit
-- sequence of ln), while the STRUCTURE (the homomorphism ·↔+, 1↔0,
-- recip↔neg) is exact and buildable. This module turns that corrected note
-- into code.
--
-- The codec's STRUCTURE is a monoid homomorphism from an additive L-space
-- into the multiplicative G-space (ℚ, *ℚ, 1ℚ):  exp(a+b) = exp a · exp b,
-- exp 0 = 1.  This is the discrete/formal logarithm — "exponents add when
-- powers multiply" — independent of any base: choosing base e gives the
-- analytic ln-VALUE, but the homomorphism does not depend on that choice.
-- (The value-level exp/log on RealTrace live in `Algebra.R.Trace.{Exp,Log,
-- Transcendental}`, where the round-trip `exp-log-roundtrip` is the deferred
-- coinductive bisimulation `~`. Here there is no transcendence to defer: the
-- structure is a finite ≈ℚ-equation, proved by induction in Properties.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_)
open import Substrate.Algebra.ExpLogCodec public using (ExpLogCodec)

------------------------------------------------------------------------
-- THE CODEC INTERFACE is now the carrier-generic `Algebra.ExpLogCodec`
-- (the additive→multiplicative monoid homomorphism, lifted off ℚ). The
-- el-atlas conductance codec is its ℚ INSTANCE — single source, one record:
--   `expL` is the "exp" direction (L → ℚ); the homomorphism laws (·↔+, 1↔0)
--   ARE the structural content — no analytic value is referenced.
------------------------------------------------------------------------

-- the el-atlas G-space codec: exp⊣log into the multiplicative (ℚ, *ℚ, 1ℚ).
-- ⟡set1-paydown (downstream of ExpLogCodec): the L-space carrier is now the
-- record's module parameter, so this ℚ-target alias is carrier-indexed too
-- (the CONSUMER supplies L, as `ExpLogCodecℚ ℕ`, `ExpLogCodecℚ ℤ`, …).
ExpLogCodecℚ : Set → Set
ExpLogCodecℚ L = ExpLogCodec L _*ℚ_ 1ℚ _≈ℚ_

------------------------------------------------------------------------
-- The base-power exponential gⁿ : the carrier of the concrete witness
-- (`GValueLSpace.Properties.ℕ-power-codec`).  A plain definition over *ℚ.
------------------------------------------------------------------------

powℚ : ℚ → ℕ → ℚ
powℚ g zero    = 1ℚ
powℚ g (suc n) = g *ℚ powℚ g n
