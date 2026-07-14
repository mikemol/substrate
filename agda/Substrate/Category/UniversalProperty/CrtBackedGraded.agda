------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.CrtBackedGraded — ⟡C2g-m-crt (graded): the CRT (ℤ/3 × ℤ/5 →
-- ℤ/15) universal property as a Set₀ graded backing.
--
-- Migrates the flat `crt-backed : BackedUP` (Backed.agda:69). Class B CARE: the flat Witness was the
-- mod-3 ∧ mod-5 CONGRUENCE product (`(x ≡ p₁ mod 3) × (x ≡ p₂ mod 5)`); the graded Contentfulᴳ
-- collapses it to functional `t ≡ combine witness-3-5 s` (the CRT combine — the whole
-- gcd→Bézout→inverse→idempotent→combine chain). `solves` (the two-mod congruence) is dropped. Content
-- at grade 0: combine witness-3-5 (1,2) = 7 (the CRT solution ≡ 7 mod 15), so 0 ≢ it.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.CrtBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Quotient.CRT using (combine)
open import Substrate.Algebra.Quotient.CRT.FromTrace using (witness-3-5)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- solve = the CRT combine at the (3,5) witness (the number-theoretic wedge backing CRT).
crt-arrowᴳ : UPArrowᴳ (λ _ → ℕ × ℕ) (λ _ → ℕ)
crt-arrowᴳ = mkUP (λ p → combine witness-3-5 p)

crt-backedᴳ : BackedUPᴳ (λ _ → ℕ × ℕ) (λ _ → ℕ)
crt-backedᴳ = record
  { arrowᴳ  = crt-arrowᴳ
  ; content = 0 , (1 , 2) , 0 , λ ()
  }
