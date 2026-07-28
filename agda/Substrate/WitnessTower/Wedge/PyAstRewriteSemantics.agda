------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRewriteSemantics
--
-- ⟡pyrig-rebuild-semantics — CONCRETE semantics of a pyast rewrite, reusing the
-- tower. A rewrite is a `PyRewrite n = LehmerPath n` (a Coxeter word / permutation
-- in normal form); its interpretation is `interp = foldR` (PyAstRewrite) into a
-- semantic rig algebra.
--
-- VERIFIED BARRIER (⟡reuse-structural-first): a FULL non-trivial pyast
-- `RigAlgebra` (a rich valued carrier for `interp`/`foldR`) is gated by the
-- `⊗ᶜ-step` coherence (replayᶜ) — the tower packages only `LehmerRig` (identity /
-- the normal form) and `TrivRig` (one point). Building another is the tower's
-- `OrientationProductStructural` territory — deferred as ⟡pyrig-rebuild-semantics-rig.
--
-- What IS achievable now are the meaningful READINGS the tower already provides —
-- two genuine invariants of a transformation:
--
--   pyLength — its Coxeter LENGTH = Σ Lehmer digits = the number of atomic
--              adjacent-transposition rewrites = the COST (a LehmerAlgebra fold).
--   pySign   — its PARITY / chirality (even vs odd), via the tower's sign hom.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRewriteSemantics where

open import Substrate.Foundation.Nat using (ℕ; zero; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Bool using (Bool)
open import Substrate.WitnessTower.LehmerPath using (decode)
open import Substrate.WitnessTower.Wedge.OrientationUniversal using (LehmerAlgebra; fold)
open import Substrate.WitnessTower.Wedge.OrientationRigCatPermSign using (sign)
open import Substrate.WitnessTower.Wedge.PyAstRewrite using (PyRewrite)

-- LENGTH: the transformation's cost = the number of atomic adjacent-transposition rewrites =
-- Σ of the Lehmer digits. A LehmerAlgebra fold: base 0, each ◂-step adds its digit.
lengthAlg : LehmerAlgebra (λ _ → ℕ)
lengthAlg = record { base = zero ; step = λ c p → c + toℕ p }

pyLength : {n : ℕ} → PyRewrite n → ℕ
pyLength = fold lengthAlg

-- SIGN: the transformation's parity / chirality, via the tower's sign homomorphism on decode.
pySign : {n : ℕ} → PyRewrite n → Bool
pySign l = sign (decode l)
