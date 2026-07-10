------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarNumeral  (Ξ★.num)
--
-- The NUMERAL graded coherence CrossMul named and deferred ("CRT is that
-- numeral example"). Ξ★.g gave graded coherence ABSTRACTLY (the N-complex
-- Three = {𝟘, η, sq}); here it is realised with real numbers in ℤ/8 = ℤ/2³,
-- where the nilpotency degree tracks an ACTUAL value:
--
--   2 ↔ η  : 2² = 4 ≠ 0,  2³ = 8 ≡ 0   — degree 3 (NOT square-zero; N-complex).
--   4 ↔ sq : 4² = 16 ≡ 0               — degree 2 (square-zero).
--   0 ↔ 𝟘  : the multiplicative zero.
--
-- ℤ/8's ideal {0,2,4,6} carries exactly Three's multiplication (2·2=4, 2·4≡0,
-- 4·4≡0) — Ξ★.g's abstract N-complex made numeral. (The CLEAN/coprime side of
-- the CRT family — orthogonal idempotents e₁·e₂≡0 in a square-free modulus like
-- ℤ/15 — is the degree-0 numeral analog of Ξ★.3; this is the NON-square-free
-- side where the obstruction is genuinely graded.)
--
-- The common carrier R = ℤ/8 as a MulDivStr (carrier ℕ, mul = product mod 8);
-- the cross term of the CrossMix is a numeral whose nilpotency degree is the
-- cost — measured, not posited.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarNumeral where

open import Substrate.Foundation.Nat using (ℕ; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; pow; Nilpotent; square-zero)
open import Substrate.Algebra.Wedge.Bridge using (id-bridge)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)

------------------------------------------------------------------------
-- R = ℤ/8 as a MulDivStr: carrier ℕ, zero 0, product reduced mod 8.
------------------------------------------------------------------------

ℤ8-div : DivStr ℕ
ℤ8-div = record { z = 0 ; recon = λ _ _ r → r }

ℤ8-mul : MulDivStr ℕ
ℤ8-mul = record { base = ℤ8-div ; mul = λ a b → (a * b) mod-suc 7 }

------------------------------------------------------------------------
-- Numeral nilpotency degrees in ℤ/8 — the grade IS an actual number.
------------------------------------------------------------------------

2-not-square-zero : square-zero ℤ8-mul 2 → ⊥        -- 2² = 4 ≠ 0 : the N-complex d²≠0
2-not-square-zero ()

2-degree-3 : Nilpotent ℤ8-mul 2                     -- 2³ = 8 ≡ 0 : degree 3
2-degree-3 = 2 , refl

4-degree-2 : Nilpotent ℤ8-mul 4                     -- 4² = 16 ≡ 0 : degree 2
4-degree-2 = 1 , refl

------------------------------------------------------------------------
-- The numeral graded CrossMix: same cospan, cross terms of varying numeral
-- degree (the cost). 2⊗2 = 4 (degree-2 obstruction); 2⊗4 = 0 (clean / null).
------------------------------------------------------------------------

numeral-mix : CrossMix ℤ8-div ℤ8-div ℤ8-mul
numeral-mix = record { embA = id-bridge ℤ8-div ; embB = id-bridge ℤ8-div }

obstruction-cross : cross numeral-mix 2 2 ≡ 4         -- 2·2 mod 8 = 4 ≠ 0 : obstruction
obstruction-cross = refl

graded-obstruction : Coherent numeral-mix 2 2         -- the cross term 4 is degree-2 nilpotent
graded-obstruction = 1 , refl

clean-cross : cross numeral-mix 2 4 ≡ 0               -- 2·4 mod 8 = 0 : the bridge-null
clean-cross = refl

clean-pair : Coherent numeral-mix 2 4                 -- cross term already 0 : degree 0
clean-pair = 0 , refl
