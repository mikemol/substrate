------------------------------------------------------------------------
-- Substrate.Logic.Evidence.Atlas.GcdBezout
--
-- The NUMBER-THEORETIC chart pair of el-atlas's exp ⊣ log — and it falls out
-- of the EEA already in the repo, because the substrate's Euclidean trace is
-- ALREADY read two ways ([[project-bridge-indexes-algebra-category]] /
-- Algebra.Wedge.Reads):
--
--   * FORGET the quotients  →  `gcd-fold`  →  the gcd  g       — the MULTIPLICATIVE chart 𝕄
--   * KEEP   the quotients  →  `bezout-ℤ`  →  s·a + t·b = g     — the ADDITIVE       chart 𝔸  (over ℤ)
--
-- So the el-atlas claim C2 ("gcd(ℕ semiring) / Bézout(ℤ ring) = 𝕄 / 𝔸; the
-- trace mediates the chart transition") is the KEEP ⊣ FORGET axis of one trace.
-- Unlike `nedge-atlas` (the LOSSLESS, bijective recode — an adjoint EQUIVALENCE),
-- this pair is a genuine, non-invertible adjunction: forgetting the quotients
-- cannot be undone from the gcd alone. It is therefore the substrate's CENTER —
-- Free ⊣ Forgetful ([[project-center-free-universal-property]]) — realizing the
-- "⊣" in exp ⊣ log, where the recode realizes the "equivalence". Two strengths
-- of the same el-atlas structure.
--
-- "Falls out for free": the value space is `compute-trace a b` (the EEA run);
-- 𝕄 is `proj₁` (the gcd); 𝔸 is `bezout-ℤ` of `proj₂` (the trace). The coherence
-- — the additive chart targets the SAME gcd — is the TYPE of `bezout-chart`,
-- i.e. the keep-read determines the forget-read (the never-discard residue is
-- enough to reconstruct the forgetful one; [[feedback-never-discard-residue]]).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.Atlas.GcdBezout where

open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Algebra.Nat.GCD.ComputeTrace using (compute-trace)
open import Substrate.Algebra.Z.Bezout using (BezoutℤWitness; bezout-ℤ)

------------------------------------------------------------------------
-- 𝕄 — the multiplicative chart: the FORGETFUL trace-read (the gcd).
------------------------------------------------------------------------

gcd-chart : ℕ → ℕ → ℕ
gcd-chart a b = proj₁ (compute-trace a b)

------------------------------------------------------------------------
-- 𝔸 — the additive chart: the KEEP trace-read (the Bézout bridge over ℤ).
-- Its TYPE names the same gcd, so the additive chart determines the
-- multiplicative one — the keep ⊣ forget direction, for free.
------------------------------------------------------------------------

bezout-chart : (a b : ℕ) → BezoutℤWitness a b (gcd-chart a b)
bezout-chart a b = bezout-ℤ (proj₂ (compute-trace a b))

------------------------------------------------------------------------
-- Worked instance: the additive coordinates over the gcd of (12, 8).
-- (Typechecks against the multiplicative chart's gcd — the coherence.)
------------------------------------------------------------------------

_ : BezoutℤWitness 12 8 (gcd-chart 12 8)
_ = bezout-chart 12 8
