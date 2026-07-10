------------------------------------------------------------------------
-- Substrate.Algebra.Z.Wedge
--
-- ℤ FOUNDED ON THE WEDGE — ℤ as a `DivStr`, a third foundational root on the
-- wedge basis (with `ℕ-div` and `F₂-div`). The reconstruction is the ring
-- shape `recon q b r = q ·ℤ b + r`, `z = 0ℤ`, where the quotient `q` is now a
-- CARRIER REPRESENTATIVE (an element of `ℤ`), not a bare ℕ count coerced by `+_`
-- — so a negative quotient is allowed (the recon is de-lossified). ℤ's
-- arithmetic (`_+ℤ_`, `_*ℤ_`) is exactly the operand layer the
-- EEA→Bézout bridge needed (Algebra.Z.Bezout) — so founding ℤ here reuses it
-- and ties the Bézout fold's carrier into the monoidal groupoid of roots.
--
-- DEF/PROOF SEPARATION: imports only the ℤ definition modules (`Z`,
-- `Z.Arithmetic`), no `Z.Properties.*` — `ℤ-div` is a definition, not a proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Z.Wedge where

open import Substrate.Algebra.Z using (ℤ; 0ℤ)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Wedge using (DivStr)

ℤ-div : DivStr ℤ
ℤ-div = record { z = 0ℤ ; recon = λ q b r → (q *ℤ b) +ℤ r }
