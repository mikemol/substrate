------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Mul
--
-- THE FORCED ENRICHMENT (step 1 of the cross-multiplication). Bare DivStr
-- (Set + recon) tops out at lockstep; genuine bilinear mixing — and even the
-- WORD "nilpotent" — needs the carrier to MULTIPLY. So enrich: a MulDivStr
-- is a DivStr whose carrier carries a multiplication. This is the structure
-- the construction forced, not one chosen ahead of need.
--
-- With multiplication, the nilpotent graded residue becomes COMPUTABLE, and
-- that residue IS the differential degree:
--   * `pow x n = xⁿ`; `Nilpotent x = Σ n. xⁿ = z` — x reduces to zero under
--     powers (z, the wedge's terminal, is the multiplicative 0).
--   * a residue nilpotent of degree n is `dⁿ = 0`. The degree-2 case
--     (`x² = z`, `square-zero`) is the ordinary differential `d² = 0`; degree
--     n > 2 is an N-complex (`d² ≠ 0`), the boundary-of-a-boundary that
--     doesn't vanish — and the degree, the structural WHY, is now a number
--     the wedge can read off the residue rather than an axiom imposed.
--
-- WITNESSES: ℕ (reduced — no nontrivial nilpotents, correctly), and the
-- square-zero carrier where `ε² = z` exhibits ε as the differential `d`
-- itself — abstractly (the infinitesimal / tangent direction), no numerals.
--
-- NEXT: cross-carrier MIXING on top of this — two carriers meeting in a
-- common MulDivStr where `mul` mixes them, residues nilpotent of graded
-- degree. That is the genuine tensor; this is the multiplication it needs.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Mul where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.Wedge using (DivStr; C; z; recon; ℕ-div)

------------------------------------------------------------------------
-- 1. The enrichment: a carrier that multiplies.
------------------------------------------------------------------------

record MulDivStr : Set₁ where
  field
    base : DivStr
    mul  : C base → C base → C base

open MulDivStr public

------------------------------------------------------------------------
-- 2. Powers and nilpotency = the differential degree.
------------------------------------------------------------------------

pow : (M : MulDivStr) → C (base M) → ℕ → C (base M)
pow M x zero    = x                       -- pow x 0 = x ; pow x n = x^(n+1)
pow M x (suc n) = mul M x (pow M x n)

-- x reduces to the zero z under powers: the nilpotent graded residue.
Nilpotent : (M : MulDivStr) → C (base M) → Set
Nilpotent M x = Σ ℕ (λ n → pow M x n ≡ z (base M))

-- x ANNIHILATES: it kills EVERY product (x·y = z for all y) — a dead-end, the
-- structure collapses. Distinct from Nilpotent (x kills only its OWN powers).
-- ⊙ conjecture #5: a nonzero nilpotent residue is a GRADED obstruction, NOT an
-- annihilator — "kill can't happen", the structure deforms but never dead-ends
-- (ties #1: the wedge correction is always handed back). Separation witnessed in
-- `Wedge.Wedderburn` (e₁₂ nilpotent yet e₁₂·e₂₁ = e₁₁ ≠ z).
Annihilator : (M : MulDivStr) → C (base M) → Set
Annihilator M x = (y : C (base M)) → mul M x y ≡ z (base M)

-- x² = z : the differential element, d² = 0 (the degree-2 nilpotent).
square-zero : (M : MulDivStr) → C (base M) → Set
square-zero M x = pow M x 1 ≡ z (base M)         -- pow x 1 = x * x

square-zero→nilpotent : (M : MulDivStr) (x : C (base M)) →
                        square-zero M x → Nilpotent M x
square-zero→nilpotent M x sq = 1 , sq

------------------------------------------------------------------------
-- 3. Witness A: ℕ is multiplicative and REDUCED (no nontrivial nilpotents —
--    a domain; nilpotents arise only in non-reduced carriers, next).
------------------------------------------------------------------------

ℕ-mul : MulDivStr
ℕ-mul = record { base = ℕ-div ; mul = _*_ }

------------------------------------------------------------------------
-- 4. Witness B: the square-zero carrier — ε is the differential d (ε² = z),
--    abstractly (the infinitesimal / tangent direction), no numerals.
------------------------------------------------------------------------

data Two : Set where
  𝟘 ε : Two

two-div : DivStr
two-div = record { C = Two ; z = 𝟘 ; recon = λ _ _ r → r }

two-mul : MulDivStr
two-mul = record { base = two-div ; mul = λ _ _ → 𝟘 }    -- square-zero: x·y = 0

ε-square-zero : square-zero two-mul ε                    -- ε² = z (d² = 0)
ε-square-zero = refl

ε-nilpotent : Nilpotent two-mul ε                        -- ε is a degree-2 residue
ε-nilpotent = square-zero→nilpotent two-mul ε ε-square-zero
