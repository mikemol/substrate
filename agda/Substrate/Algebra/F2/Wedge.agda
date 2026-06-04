------------------------------------------------------------------------
-- Substrate.Algebra.F2.Wedge
--
-- F₂ FOUNDED ON THE WEDGE — F₂ as a `DivStr`, so it becomes a wedge-carrier
-- (a vertex of the foundational quotient algebra) rather than a primitive
-- data type the wedge cannot reach. The reconstruction is the ring shape
-- `recon q b r = (q copies of b) + r`, with `z = 𝟘` the terminal divisor.
--
-- WHY THIS EXISTS: the shred of the realizable peak showed the foundation is
-- an open DAG with no fluidity — because the roots (F₂, Fin, ℤ, …) are NOT
-- wedge-carriers, so the wedge's bridge-construction machinery has nothing at
-- the bottom to operate on. Founding F₂ here puts a second genuine root on
-- the wedge basis (alongside `ℕ-div`); a `Bridge ℕ-div F₂-div` (parity, the
-- mod-2 homomorphism) is then wedge-EXPRESSIBLE — a bridge the wedge
-- constructs, not one bolted on. With ≥2 roots founded the cross-carrier
-- tensor `_⊗ᴰ_` and its pentagon coherence (Algebra.Wedge.Monoidal) are
-- grounded at the actual roots, not merely abstract.
--
-- NOTE the ℕ-scale is the honest Peano count: `scale q b` is `b` summed `q`
-- times. In F₂ that collapses to `(q mod 2)·b`, but we DON'T optimize — the
-- count IS the wedge's quotient shadow (Quot = ℕ is baked, per Wedge.agda),
-- and keeping it unoptimized keeps `recon`'s quotient the Peano shadow.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Wedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_)
open import Substrate.Algebra.Wedge using (DivStr)

------------------------------------------------------------------------
-- 1. ℕ-scaling: q copies of b, summed (the quotient's Peano shadow).
------------------------------------------------------------------------

scale : ℕ → F₂ → F₂
scale zero    _ = 𝟘
scale (suc n) b = b + scale n b

------------------------------------------------------------------------
-- 2. F₂ as a wedge-carrier: recon q b r = (q copies of b) + r, z = 𝟘.
------------------------------------------------------------------------

F₂-div : DivStr
F₂-div = record { C = F₂ ; z = 𝟘 ; recon = λ q b r → scale q b + r }
