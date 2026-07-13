------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PyAstRigGround
--
-- ⟡pyrig-ground (residue face) — GROUND the PyAstRig orbit residue in the
-- witness tower's OWN residue, rather than treat it as new. The whole arc named
-- one invariant — the wedge residue `a = recon q b r`, residue = the orientation
-- / Lehmer digit — and the tower ALREADY models it:
--
--   OrientationTowerDiv.towerDiv : GradedDivStr LehmerPath (λ n → Fin (suc n))
--       recon n l d = l ◂ d       -- recon IS the ◂-step; the residue R n = Fin(suc n) IS the digit.
--
-- PyAstRig's `pyRecon rep r = act (decode r) rep` reconstructs a point of an
-- orbit from a residue COORDINATE `r : LehmerPath n`. This module shows that
-- residue coordinate IS towerDiv's: a point reconstructed with a top Lehmer digit
-- d is the SPPF-carrier action of the tower's OWN digit-step `insert-at`,
-- DEFINITIONALLY (decode (l ◂ d) = insert-at d (decode l)). So `pyRecon` is
-- `act ∘ decode` over towerDiv's residue-recon — the residue is not re-derived,
-- it is the tower's Lehmer digit.
--
-- HONEST SCOPE (the verified trunk). The RESIDUE face grounds as a clean,
-- DEFINITIONAL instance (verified: the theorem is `refl`). The other three faces
-- (⟡pyrig-ground-{action,initiality,cospan}) all route through the SAME different
-- CARRIER — SPPF over pyast positions, not LehmerPath/Perm — so whether each is a
-- clean instance or a genuinely-new construction is a PER-FACE question, not
-- settled here. The obstructions observed (not exhaustively verified): `act` is
-- over `Objpy`, and the object-monoid ⊗obj on SPPF lands in a grade the free term
-- does not carry (the ⊗-on-SPPF wall); `cata`/`pyEval` fold an ARBITRARY generator
-- set, of which LehmerRig's `foldR` is the walking-generator special case; the
-- cospan is the structural (not algebraic/CrossMul) reading. So the VERIFIED
-- result is narrower than the retrospective's "re-derived all four": ONLY the
-- residue is confirmed the tower's-own; the rest is a related pattern on a new
-- carrier, to be settled face by face.
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PyAstRigGround where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (insert-at)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; _◂_; decode)
open import Substrate.Algebra.Wedge.Graded using (recon)
open import Substrate.WitnessTower.Wedge.OrientationTowerDiv using (towerDiv)
open import Substrate.WitnessTower.Wedge.PyAstRig using (Objpy; act; pyRecon)

-- THE GROUNDING: pyRecon consumes towerDiv's residue-recon; a top Lehmer digit d acts by the
-- tower's own step `insert-at d`. Definitional — the residue IS the Lehmer digit, not a new thing.
pyRecon-is-towerDiv-residue :
  {n : ℕ} (rep : Objpy (suc n)) (l : LehmerPath n) (d : Fin (suc n)) →
  pyRecon rep (recon towerDiv n l d) ≡ act (insert-at d (decode l)) rep
pyRecon-is-towerDiv-residue rep l d = refl
