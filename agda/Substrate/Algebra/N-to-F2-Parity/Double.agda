------------------------------------------------------------------------
-- Substrate.Algebra.N-to-F2-Parity.Double
--
-- ◆ip-abel-α-ℕ — the arithmetic FORWARD half of "even ≠ prime": doubling
-- lands in the mod-2 kernel.
--
--   parity-double : parity (k ℕ+ k) ≡ 𝟘
--
-- The parity homomorphism sends k ℕ+ k to parity k ℕ+ parity k, and in
-- characteristic 2 every element is its own additive inverse (+-self-inverse),
-- so it collapses to 𝟘. This is "2·k is even" made a TERM — the ℕ shadow of
-- the parity-kernel-is-grade-2-generated lemma (ParityKernel.Universal), of
-- which it is the Gen=⊤, count-per-generator=1 instance.
--
-- The CONVERSE (parity n ≡ 𝟘 → ∃k, n ≡ k ℕ+ k) needs an Even/half predicate the
-- substrate does not yet have (◆ip-parity-even-converse); the universal lemma's
-- even→Gr2Gen supplies the word-level converse without it.
--
-- --safe --without-K, no postulates/holes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.N-to-F2-Parity.Double where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Algebra.F2.F2
open import Substrate.Algebra.F2.PlusSelfInverse
open import Substrate.Algebra.N-to-F2-Parity using (parity; parity-+)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Trans

parity-double : (k : ℕ) → parity (k ℕ+ k) ≡ 𝟘
parity-double k = trans (parity-+ k k) (+-self-inverse (parity k))
