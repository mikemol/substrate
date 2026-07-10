------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.CenterIsStarCRT  (Ξ★.cⁿ)
--
-- The CLEAN / coprime numeral side — the worked CRT instance CrossMul names:
-- "the idempotents e₁, e₂ embed the factors and are ORTHOGONAL (e₁·e₂ ≡ 0) —
-- the cross terms vanish, the factors don't interfere, the correspondence is
-- coherent." This is the degree-0 numeral analog of Ξ★.3 (the bridge-null /
-- orthogonal correspondence), completing the pair with Ξ★.num's NON-coprime
-- ℤ/8 (where the cross term is a nonzero graded residue).
--
-- Here R = ℤ/6 = ℤ/2 × ℤ/3, the SMALLEST coprime (square-free → reduced, NO
-- nilpotents) CRT split — chosen over the ℤ/15 = ℤ/3×ℤ/5 of CrossMul's prose
-- only because the unary `mod-suc` keeps the squares small (10²=100 over ℤ/15
-- is reduction-heavy; ℤ/6's are ≤16). The CRT idempotents: e₁ = 3 (≡1 mod 2,
-- ≡0 mod 3), e₂ = 4 (≡0 mod 2, ≡1 mod 3). They are idempotent (eᵢ²≡eᵢ),
-- complete (e₁+e₂≡1), and ORTHOGONAL (e₁·e₂≡0) — so the cross term vanishes
-- outright: clean coherence.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.CenterIsStarCRT where

open import Substrate.Foundation.Nat using (ℕ; _*_; _+_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Wedge using (DivStr)
open import Substrate.Algebra.Wedge.Mul using (MulDivStr; pow; Nilpotent)
open import Substrate.Algebra.Wedge.Bridge using (id-bridge)
open import Substrate.Algebra.Wedge.CrossMul using (CrossMix; cross; Coherent)

------------------------------------------------------------------------
-- R = ℤ/6 = ℤ/2 × ℤ/3 as a MulDivStr (carrier ℕ, product mod 6); CRT idempotents.
------------------------------------------------------------------------

ℤ6-div : DivStr ℕ
ℤ6-div = record { z = 0 ; recon = λ _ _ r → r }

ℤ6-mul : MulDivStr ℕ
ℤ6-mul = record { base = ℤ6-div ; mul = λ a b → (a * b) mod-suc 5 }

e₁ e₂ : ℕ
e₁ = 3        -- ≡ 1 mod 2, ≡ 0 mod 3
e₂ = 4        -- ≡ 0 mod 2, ≡ 1 mod 3

------------------------------------------------------------------------
-- The CRT idempotent decomposition of ℤ/6 — all numeral, by refl.
------------------------------------------------------------------------

e₁-residues : (e₁ mod-suc 1 ≡ 1) × (e₁ mod-suc 2 ≡ 0)   -- 3 ≡ 1 mod 2, ≡ 0 mod 3
e₁-residues = refl , refl

e₂-residues : (e₂ mod-suc 1 ≡ 0) × (e₂ mod-suc 2 ≡ 1)   -- 4 ≡ 0 mod 2, ≡ 1 mod 3
e₂-residues = refl , refl

e₁-idempotent : (e₁ * e₁) mod-suc 5 ≡ e₁          -- 3² = 9 ≡ 3 (mod 6)
e₁-idempotent = refl

e₂-idempotent : (e₂ * e₂) mod-suc 5 ≡ e₂          -- 4² = 16 ≡ 4 (mod 6)
e₂-idempotent = refl

idempotents-complete : (e₁ + e₂) mod-suc 5 ≡ 1    -- e₁ + e₂ = 7 ≡ 1 (mod 6)
idempotents-complete = refl

idempotents-orthogonal : (e₁ * e₂) mod-suc 5 ≡ 0  -- e₁·e₂ = 12 ≡ 0 : ORTHOGONAL
idempotents-orthogonal = refl

------------------------------------------------------------------------
-- The CRT CrossMix: both factor strands embed into ℤ/6; the cross term of the
-- orthogonal idempotents VANISHES — clean coherence (degree 0).
------------------------------------------------------------------------

crt-mix : CrossMix ℤ6-div ℤ6-div ℤ6-mul
crt-mix = record { embA = id-bridge ℤ6-div ; embB = id-bridge ℤ6-div }

clean-cross : cross crt-mix e₁ e₂ ≡ 0            -- e₁·e₂ mod 6 = 0 : no interference
clean-cross = refl

crt-coherent : Coherent crt-mix e₁ e₂            -- cross term already 0 : degree 0, clean
crt-coherent = 0 , refl
