------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.InclusionBridge
--
-- THE ℕ ↪ ℤ INCLUSION as a `Bridge` — a second wedge-constructed cross-root
-- edge (after ParityBridge's ℕ↠F₂). The translation is the non-negative
-- coercion `+_ : ℕ → ℤ`, and it RESPECTS `recon` definitionally: ℤ
-- arithmetic is built so `(+ m) +ℤ (+ n) = + (m + n)` and
-- `(+ m) *ℤ (+ n) = + (m * n)` are definitional clauses (Z.Arithmetic), so
-- `recon ℤ-div q (+ b) (+ r) = (+ q) ·ℤ (+ b) +ℤ (+ r)` reduces straight back
-- to `+ (q·b + r) = + (recon ℕ-div q b r)`. Hence `respects = refl`.
--
-- PAYOFF: the inclusion transports the whole ℕ Euclidean apparatus into ℤ —
-- so a ℕ gcd / Bézout trace embeds into ℤ, where the SIGNED Bézout fold
-- (Algebra.Z.Bezout) lives. The two paths the session opened (EEA→Bézout-ℤ
-- and root-founding) meet here: this edge is exactly the carrier inclusion
-- the Bézout fold's operand type assumes.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.InclusionBridge where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.Z using (+_)
open import Substrate.Algebra.Z.Wedge using (ℤ-div)
open import Substrate.Algebra.Wedge using (ℕ-div; Trace)
open import Substrate.Algebra.Wedge.Bridge using (Bridge; transport-trace)

-- ℕ ↪ ℤ: the non-negative coercion respects recon definitionally.
include-ℕℤ : Bridge ℕ-div ℤ-div
include-ℕℤ = record
  { translate = +_ ; respects = λ _ _ _ → refl ; z-pres = refl }

-- the inclusion carries ℕ Euclidean traces into ℤ (where signed Bézout lives).
include-transport-trace : {a b g : _} →
  Trace ℕ-div a b g → Trace ℤ-div (+ a) (+ b) (+ g)
include-transport-trace = transport-trace include-ℕℤ
