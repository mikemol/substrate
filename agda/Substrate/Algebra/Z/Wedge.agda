------------------------------------------------------------------------
-- Substrate.Algebra.Z.Wedge
--
-- ℤ FOUNDED ON THE WEDGE — ℤ as a `DivStr`, a third foundational root on the
-- wedge basis (with `ℕ-div` and `F₂-div`). The reconstruction is the ring
-- shape `recon q b r = (+ q) ·ℤ b + r`, `z = 0ℤ`. ℤ's arithmetic
-- (`_+ℤ_`, `_*ℤ_`, the `+_` coercion) is exactly the operand layer the
-- EEA→Bézout bridge needed (Algebra.Z.Bezout) — so founding ℤ here reuses it
-- and ties the Bézout fold's carrier into the monoidal groupoid of roots.
--
-- DEF/PROOF SEPARATION: imports only the ℤ definition modules (`Z`,
-- `Z.Arithmetic`), no `Z.Properties.*` — `ℤ-div` is a definition, not a proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Wedge where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Algebra.Z using (ℤ; +_; 0ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Wedge using (DivStr)

ℤ-div : DivStr
ℤ-div = record { C = ℤ ; z = 0ℤ ; recon = λ q b r → ((+ q) *ℤ b) +ℤ r }
