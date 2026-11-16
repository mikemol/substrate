-- ⟡leibniz-det-of-perm-matrix probe. Concrete poles: det (P σ) ≡ sign σ.
{-# OPTIONS --safe --without-K --guardedness #-}

module permmat-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_)
open import Substrate.Foundation.Fin using (Fin; zero; suc; _≟_)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.TowerCocycleGraded using (signF)
import Substrate.WitnessTower.LeibnizDet as LD

open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Semiring.Instances.Z using (ℤ-semiring; mul-sign-computes)

open LD.Det ℤ ℤ-semiring using (Mat)
open LD.Det.WithSign ℤ ℤ-semiring (-suc 0) mul-sign-computes using (det; signVal)

------------------------------------------------------------------------
-- The permutation matrix, FLAT: P σ [i,j] = 1 iff j ≡ σ i, else 0.
-- (row i has its 1 in column σ i, so Πⱼ P σ[j, τ j] = 1 iff τ = σ.)
------------------------------------------------------------------------

Pmat : {n : ℕ} → Perm n → Mat n
Pmat {n} σ k with proj₁ (remQuot {n} n k) | proj₂ (remQuot {n} n k)
... | i | j with j ≟ lookup σ i
...   | yes _ = + 1
...   | no  _ = + 0

------------------------------------------------------------------------
-- POLES at n = 2, 3. The RHS is signVal (signF σ) (+ 1) — the sign as ±1.
------------------------------------------------------------------------

id2 swap2 : Perm 2
id2   = zero ∷ suc zero ∷ []
swap2 = suc zero ∷ zero ∷ []

-- det (P id) = +1  (identity is even)
det-P-id2 : det {2} (Pmat id2) ≡ signVal (signF id2) (+ 1)
det-P-id2 = refl

-- det (P swap) = -1  (a transposition is odd)
det-P-swap2 : det {2} (Pmat swap2) ≡ signVal (signF swap2) (+ 1)
det-P-swap2 = refl

-- and the RHS really are ±1:
sign-id2-is-+1   : signVal (signF id2)   (+ 1) ≡ + 1
sign-id2-is-+1   = refl
sign-swap2-is-−1 : signVal (signF swap2) (+ 1) ≡ -suc 0
sign-swap2-is-−1 = refl

id3 tp3 cyc3 : Perm 3
id3  = zero ∷ suc zero ∷ suc (suc zero) ∷ []
tp3  = suc zero ∷ zero ∷ suc (suc zero) ∷ []          -- a transposition (odd)
cyc3 = suc zero ∷ suc (suc zero) ∷ zero ∷ []          -- a 3-cycle (even)

det-P-id3  : det {3} (Pmat id3)  ≡ signVal (signF id3)  (+ 1)
det-P-id3  = refl
det-P-tp3  : det {3} (Pmat tp3)  ≡ signVal (signF tp3)  (+ 1)
det-P-tp3  = refl
det-P-cyc3 : det {3} (Pmat cyc3) ≡ signVal (signF cyc3) (+ 1)
det-P-cyc3 = refl
