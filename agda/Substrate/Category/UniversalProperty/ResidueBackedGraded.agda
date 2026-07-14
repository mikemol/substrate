------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ResidueBackedGraded — ⟡C2g-m-z3z5 (graded): the ℤ/3 and ℤ/5
-- residue universal properties as Set₀ graded backings, THE GRADE = THE MODULUS.
--
-- Migrates the flat `Z3-backed` / `Z5-backed : BackedUP` (Interop.agda:63/67). Class B CARE: the flat
-- Witness was a mod-CONGRUENCE relation (`x mod-suc n ≡ a mod-suc n`) with `solve = id`; the graded
-- Contentfulᴳ forces functional `t ≡ solve s`, so keeping `solve = id` would LOSE the residue meaning.
-- The honest redesign (the "residue ones = modulus grade" recipe): ONE arrow `solve {n} = _mod-suc n`
-- (the residue normalizer), and the two backings differ only by the MODULUS GRADE at which content
-- lives — Z3 at grade 2 (=mod 3), Z5 at grade 4 (=mod 5). This is the seed of the ⟡C2g-ring C family
-- (C M graded by the modulus). Content: 1 mod-suc n = 1 ≠ 0.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.ResidueBackedGraded where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Algebra.Nat.Mod using (_mod-suc_)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- THE MODULUS IS THE GRADE: solve {n} a = a mod-suc n (the residue normalizer at modulus n+1).
residue-arrowᴳ : UPArrowᴳ (λ _ → ℕ) (λ _ → ℕ)
residue-arrowᴳ = mkUP (λ {n} a → a mod-suc n)

-- ℤ/3 at grade 2 (mod 3): content 1 mod-suc 2 = 1 ≠ 0.
Z3-backedᴳ : BackedUPᴳ (λ _ → ℕ) (λ _ → ℕ)
Z3-backedᴳ = record
  { arrowᴳ  = residue-arrowᴳ
  ; content = 2 , 1 , 0 , λ ()
  }

-- ℤ/5 at grade 4 (mod 5): content 1 mod-suc 4 = 1 ≠ 0.
Z5-backedᴳ : BackedUPᴳ (λ _ → ℕ) (λ _ → ℕ)
Z5-backedᴳ = record
  { arrowᴳ  = residue-arrowᴳ
  ; content = 4 , 1 , 0 , λ ()
  }
