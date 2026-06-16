------------------------------------------------------------------------
-- Substrate.Algebra.Fin.Wedge
--
-- THE FINITE CYCLIC QUOTIENT FOUNDED ON THE WEDGE — Z/(suc n) as a
-- `DivStr`, the general-n generalization of `F₂-div` (which is the n=1
-- case, i.e. the modulus suc 1 = 2). The carrier is `Fin (suc n)`, the
-- canonical n+1-element cyclic quotient; `z = zero` is the terminal
-- divisor; the reconstruction is the ring shape `recon q b r =
-- (q copies of b) + r`, evaluated in ℕ and reduced back into
-- Fin (suc n) by the substrate-native modular reduction `_mod-suc n`.
--
-- WHY Fin (suc n) (and not ℕ-reduced-by-recon): the deliverable is the
-- n-element cyclic QUOTIENT as a carrier — a type whose elements ARE the
-- residues, not all of ℕ with reduction hidden inside recon. Fin (suc n)
-- is exactly that quotient as data, and it matches the substrate's own
-- choice of cyclic carrier (Algebra.PontryaginDual.Sites.Zn's add-mod /
-- neg-mod are the same Fin (suc n) + `_mod-suc n` + `fromℕ<` shape).
--
-- WHY `toℕ q * toℕ b` rather than a separate `scale`: the quotient q is now
-- a CARRIER REPRESENTATIVE (an element of Fin (suc n), a residue class), not a
-- bare ℕ count; `toℕ q * toℕ b` reads its ℕ value and forms "q·b" in ℕ, the
-- cyclic analogue of F₂-div's scaled sum. Reducing the whole
-- `toℕ q * toℕ b + toℕ r` mod (suc n) at the end is the cyclic collapse; the
-- product is the wedge's quotient·divisor shadow taken on the representatives.
--
-- The bridge `ℕ-div ↠ Cyc-div n` (modular reduction, the ℕ → Z/(suc n)
-- ring homomorphism) is then wedge-EXPRESSIBLE — see
-- Substrate.Algebra.Fin.Wedge.ModBridge, the general-n parity bridge.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Fin.Wedge where

open import Substrate.Foundation.Nat using (ℕ; suc; _+_; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; toℕ; fromℕ<)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_; mod-suc-bound)
open import Substrate.Algebra.Wedge using (DivStr)

------------------------------------------------------------------------
-- 1. Cyclic reconstruction: (q copies of b) + r, reduced mod (suc n).
--
-- The ℕ value `toℕ q * toℕ b + toℕ r` (q, b, r read as their residue
-- representatives) is reduced into Fin (suc n) via `_mod-suc n` (bound by
-- `mod-suc-bound`, landed by `fromℕ<`). This is the cyclic analogue of
-- F₂-div's `scale q b + r`.
------------------------------------------------------------------------

recon-cyc : (n : ℕ) → Fin (suc n) → Fin (suc n) → Fin (suc n) → Fin (suc n)
recon-cyc n q b r = fromℕ< (mod-suc-bound (toℕ q * toℕ b + toℕ r) n)

------------------------------------------------------------------------
-- 2. Z/(suc n) as a wedge-carrier: recon q b r = (q·b + r) mod (suc n),
--    z = zero (the identity residue χ_0 / the zero class).
------------------------------------------------------------------------

Cyc-div : (n : ℕ) → DivStr
Cyc-div n = record { C = Fin (suc n) ; z = zero {n} ; recon = recon-cyc n }
