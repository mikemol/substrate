{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.OrientationTowerDiv
--
-- ⟡rig-UP-residue-graded — the residue as a GRADE-RESPECTING object: instead of flattening the
-- grade into a Σ (the set1-is-grade-collapse anti-pattern of OrientationRigResidue's
-- DivStr (Σ ℕ LehmerPath)), TELL the division its residue. That is exactly
-- Substrate.Algebra.Wedge.Graded.GradedDivStr C R: the carrier C : ℕ → Set stays graded (index,
-- not Σ) and the RESIDUE family R : ℕ → Set is a PARAMETER — the residue "being flattened away",
-- here exposed. For the ordering tower the residue is the LEHMER DIGIT:
--
--   towerDiv : GradedDivStr LehmerPath (λ n → Fin (suc n))     recon n l d = l ◂ d
--
-- So `recon` IS the ◂-step and the remainder R n = Fin (suc n) IS the digit/orientation. This is
-- the PRINCIPLED ORIGIN the flat DivStr lacked: plain DivStr (C → C → C → C) is the GRADE-COLLAPSE
-- of this (flatten folds the grade into the residue count); the graded, residue-exposed form is
-- primary.
--
-- CLOSING THE LOOPS (the construction is cyclic — the residues generate the carrier — but covered):
--   (1) self-reference: `recon` has C in domain and codomain — benign, it is a graded operation.
--   (2) residue-recursion (the Free/term reading: a remainder has its own remainder): WELL-FOUNDED
--       on the grade — each ◂ lowers the grade by one, bottoming at `start` (grade 0). LehmerPath is
--       literally the inductive μ of this recon.
--   (3) the universal closure: a LehmerAlgebra IS a grade-0 point + this graded division
--       (alg→div below), and `fold-unique` (committed) is its INITIALITY — LehmerPath is the FREE
--       carrier on the digit-residues. That is what makes the cycle a fixpoint, not a regress.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

module Substrate.WitnessTower.Wedge.OrientationTowerDiv where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; base; step; fold; fold-unique)
open import Substrate.Algebra.Wedge.Graded
  using (GradedDivStr; GradedWedge; recon; rem; wedge-eq)

------------------------------------------------------------------------
-- 1. THE residue-exposed graded division: the ◂-tower. Residue R n = Fin (suc n) = the digit.
--    No Σ — the grade is the INDEX, the residue R is a PARAMETER told to the division.
------------------------------------------------------------------------

towerDiv : GradedDivStr LehmerPath (λ n → Fin (suc n))
towerDiv = record { recon = λ n l d → l ◂ d }

------------------------------------------------------------------------
-- 2. Every tower step IS its own wedge: (l ◂ p) decomposed over base l with remainder the digit
--    p. The residue is a Fin (suc n) — grade-RESPECTING, not a Σ-collapse. wedge-eq is refl
--    because recon towerDiv n l p reduces to l ◂ p definitionally.
------------------------------------------------------------------------

stepWedge : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
            GradedWedge towerDiv n (l ◂ p) l
stepWedge l p = record { rem = p ; wedge-eq = refl }

-- reading the residue off a step wedge gives back the digit (gcell / rem).
stepWedge-rem : ∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
                rem (stepWedge l p) ≡ p
stepWedge-rem l p = refl

------------------------------------------------------------------------
-- 3. THE LOOP CLOSES. A LehmerAlgebra is a grade-0 point (base) PLUS this graded division
--    (its `step` IS a GradedDivStr recon at R = Fin ∘ suc). So the graded division is not an
--    imported gadget — it is the tower step itself; and by `fold-unique` LehmerPath is the
--    INITIAL such carrier (the free structure on the digit-residues), which is what covers the
--    cyclic definition as a fixpoint.
------------------------------------------------------------------------

alg→div : ∀ {C : ℕ → Set} → LehmerAlgebra C → GradedDivStr C (λ n → Fin (suc n))
alg→div alg = record { recon = λ n c d → step alg c d }

-- towerDiv is the alg→div image of the IDENTITY algebra (base=start, step=◂): the tower's own
-- division. (refl — step (start,◂) = ◂ = towerDiv.recon.)
towerDiv-is-id-alg : towerDiv ≡ alg→div (record { base = start ; step = _◂_ })
towerDiv-is-id-alg = refl

-- the initiality that closes the loop: any g agreeing with fold on (base, the recon=step) IS
-- fold. Restated from the committed universal property — the residues (digits) determine the
-- unique map, so the free carrier on them is well-defined (no regress).
loop-closes : ∀ {C : ℕ → Set} (alg : LehmerAlgebra C) (g : ∀ {n} → LehmerPath n → C n) →
              (g start ≡ base alg) →
              (∀ {n} (l : LehmerPath n) (p : Fin (suc n)) →
                 g (l ◂ p) ≡ recon (alg→div alg) n (g l) p) →
              ∀ {n} (l : LehmerPath n) → g l ≡ fold alg l
loop-closes alg g g-base g-step = fold-unique alg g g-base g-step
