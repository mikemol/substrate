------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.NuBackedGraded — ⟡C2g-m-nu (graded): the ν terminal-coalgebra
-- (wedge unfold) UP as a Set₀ graded backing.
--
-- Migrates the flat `nu-backed : BackedUP` (NuBacked.agda:58). Class B CARE-HIGH — the trap: the flat
-- `wedge-contentful` refuted `0 ≡ recon 0 1 1` (coalgebra-INDEPENDENT); the graded functional Witness
-- `qr ≡ solve (a,b)` makes content depend on `divide co`, which for an abstract module-param `co` does
-- NOT reduce. Fix: instantiate `co` to the CONCRETE canonical ℕ-div coalgebra (ℕ-divide, self-
-- contained: b=0 direct via wedge-zero, suc b via construct-wedge) — then content uses (0,0), whose
-- divide = wedge-zero 0 = (0,0) reduces DEFINITIONALLY, and candidate (0,1) ≠ (0,0). `nu-step-unique`
-- (the bounded ≡-uniqueness) stays a separate layer. Class B CARE-HIGH.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.NuBackedGraded where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_)
open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Algebra.Wedge using (DivStr; quot; rem; ℕ-div; fromℕ-Wedge) renaming (Wedge to Wedgeℕ)
open import Substrate.Algebra.Nat.GCD.ConstructWedge using (construct-wedge)
open import Substrate.Algebra.Wedge.Coalgebra using (WedgeCoalg; divide)
open import Substrate.Category.UPArrowGraded using (UPArrowᴳ; mkUP)
open import Substrate.Category.UniversalProperty.BackedGraded using (BackedUPᴳ)

-- the concrete canonical ℕ-div coalgebra (self-contained, not the retiring NuRegistryEntry).
wedge-zero : (a : ℕ) → Wedgeℕ ℕ-div a 0
wedge-zero a = record { quot = 0 ; rem = a ; wedge-eq = refl }

ℕ-divide : (a b : ℕ) → Wedgeℕ ℕ-div a b
ℕ-divide a zero    = wedge-zero a
ℕ-divide a (suc b) = fromℕ-Wedge (construct-wedge a b)

ℕ-coalg : WedgeCoalg ℕ-div
ℕ-coalg = record { divide = ℕ-divide ; eq? = _≟_ }

-- solve: the coalgebra unfold returns (quotient, remainder).
nu-solve : ℕ × ℕ → ℕ × ℕ
nu-solve (a , b) = quot (divide ℕ-coalg a b) , rem (divide ℕ-coalg a b)

nu-arrowᴳ : UPArrowᴳ (λ _ → ℕ × ℕ) (λ _ → ℕ × ℕ)
nu-arrowᴳ = mkUP nu-solve

-- content at grade 0: divide ℕ-coalg 0 0 = wedge-zero 0 = (0,0) (definitional); candidate (0,1) ≠ it.
nu-backedᴳ : BackedUPᴳ (λ _ → ℕ × ℕ) (λ _ → ℕ × ℕ)
nu-backedᴳ = record
  { arrowᴳ  = nu-arrowᴳ
  ; content = 0 , (0 , 0) , (0 , 1) , λ ()
  }
