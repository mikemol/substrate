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
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; _◂_; decode)
open import Substrate.WitnessTower.FirstAppearance using (id-perm; compose)
open import Substrate.WitnessTower.SnGroup using (compose-id-left; compose-id-right)
open import Substrate.WitnessTower.CyclicGrounding using (compose-assoc)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Wedge.Graded using (recon)
open import Substrate.WitnessTower.Wedge.OrientationTowerDiv using (towerDiv)
open import Substrate.WitnessTower.Wedge.PyAstRig using (Objpy; act; pyRecon)

-- THE GROUNDING: pyRecon consumes towerDiv's residue-recon; a top Lehmer digit d acts by the
-- tower's own step `insert-at d`. Definitional — the residue IS the Lehmer digit, not a new thing.
pyRecon-is-towerDiv-residue :
  {n : ℕ} (rep : Objpy (suc n)) (l : LehmerPath n) (d : Fin (suc n)) →
  pyRecon rep (recon towerDiv n l d) ≡ act (insert-at d (decode l)) rep
pyRecon-is-towerDiv-residue rep l d = refl

------------------------------------------------------------------------
-- ⟡pyrig-ground-action (VERIFIED SPLIT, not a clean instance).
--
-- CONSTRUCTIVE POSITIVE: raw `Perm n` IS the witness tower's compose-MONOID
-- (the tower proves compose-assoc / compose-id but keeps them LOOSE — never
-- bundles them). Assembled here from the tower's own lemmas. `act` is its action
-- on the SPPF carrier `Objpy`, and act's laws are ALREADY grounded in the tower:
-- `act-id`/`act-∘` (PyAstRig) are built directly from `SnGroup.apply-id` /
-- `apply-compose` — so `act` is the free-functor lift of the tower's `apply`
-- action. Nothing new to prove for the laws.
--
-- VERIFIED NEGATIVE (reuse-search): `act` does NOT instantiate the tree's only
-- action record `Algebra.GroupAction.Actionᴳ` — which requires a *strict* `Group
-- A`. Raw `Perm n` is the transformation MONOID Tₙ (no inverse on the bare Vec:
-- only the IsPerm subset is invertible), and the genuine Sₙ is
-- `Groups.Symmetric` = a *SetoidGroup* (`≈`, over a record carrier, reached via
-- `SymBridge`), not a strict `Group`. There is no `MonoidAction` record. So the
-- action face is grounded at the LEMMA level (SnGroup) but is genuinely-new at
-- the RECORD level — the monoid-action of Tₙ on a carrier, which the tree has no
-- generic home for. (A clean `Actionᴳ`/`Torsor` instance would need: restrict to
-- Sₙ = Σ Perm IsPerm, a strict-Group repackage of `Groups.Symmetric`, and
-- transport `act` across `SymBridge` — a real bridge, filed as ⟡pyrig-ground-action-bridge.)
------------------------------------------------------------------------

permMonoid : (n : ℕ) → Monoid (Perm n)
permMonoid n = record
  { semigroup = record { magma = record { _·_ = compose } ; ·-assoc = compose-assoc }
  ; ε        = id-perm n
  ; ε-left   = compose-id-left
  ; ε-right  = compose-id-right
  }
