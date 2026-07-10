------------------------------------------------------------------------
-- Substrate.Algebra.F2.Wedge
--
-- F₂ FOUNDED ON THE WEDGE — F₂ as a `DivStr`, so it becomes a wedge-carrier
-- (a vertex of the foundational quotient algebra) rather than a primitive
-- data type the wedge cannot reach. The reconstruction is the ring shape
-- `recon q b r = (q · b) + r`, with `z = 𝟘` the terminal divisor and the
-- quotient `q` a CARRIER REPRESENTATIVE (an element of F₂), not a ℕ count.
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
-- NOTE the ℕ-scale `scale` (b summed q times) is RETAINED — it is the Peano
-- count shadow of the quotient, and is re-used by the parity bridges
-- (Wedge.ParityBridge / IntParityBridge). But `recon` no longer uses it: with
-- the quotient now a CARRIER REPRESENTATIVE (an element of F₂), the
-- reconstruction is F₂'s own ring multiplication `q · b`, not a Peano count.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.Wedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.F2 using (F₂; 𝟘; _+_; _·_)
open import Substrate.Algebra.Wedge using (DivStr)

------------------------------------------------------------------------
-- 1. ℕ-scaling: q copies of b, summed (the quotient's Peano shadow).
------------------------------------------------------------------------

scale : ℕ → F₂ → F₂
scale zero    _ = 𝟘
scale (suc n) b = b + scale n b

------------------------------------------------------------------------
-- 2. F₂ as a wedge-carrier: recon q b r = (q · b) + r, z = 𝟘.
--    The quotient q is a CARRIER REPRESENTATIVE (an element of F₂), so the
--    reconstruction is F₂'s ring multiplication, not the ℕ-count `scale`.
------------------------------------------------------------------------

F₂-div : DivStr F₂
F₂-div = record { z = 𝟘 ; recon = λ q b r → q · b + r }
