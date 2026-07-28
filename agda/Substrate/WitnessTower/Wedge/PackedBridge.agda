------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.PackedBridge
--
-- THE INSTANCE (brick 1's goal): the capacity-2 (binary) graded carrier maps
-- to the witness tower's graded step, via the unified morphism layer
-- (Algebra.Wedge.Graded.Morphism).
--
-- The capacity-2 cell's content is a BINARY distinction (the detector's F₂
-- outcome / the two seats / the ℤ/2 swap). A sequence of such cell-choices is
-- `Vec (Fin 2) n` — the binary graded carrier `vec-graded (Fin 2)`. The witness
-- tower's step is `tower-graded` (recon = `insert-at`, digit `Fin (suc n)`). The
-- map `packed→witness` is a `GradedDivStrMorphism`: each binary digit picks a
-- witness insertion `slot`, and `decode` folds `insert-at` — so the cell IS a
-- component of the witness inductive step, with `respects-recon` holding by REFL.
--
-- Group actions: the cell's ℤ/2 (the seat-swap `fin2-swap`, = the detector's
-- F₂ flip) maps to the witness tower's S₂ slot-swap at grade 1 (`slot {1}` is
-- the identity, so the binary swap IS the grade-1 slot transposition). The F₂
-- generator extends to the V₄ = F₂² that debuts at the 3→4 seam
-- (WitnessTower.KleinCensus.v4-present-at-seam) — the binary cell is the V₄/F₂ⁿ
-- shadow of the witness tower.
--
-- Inherited readout / gluing: `decode` reads a binary digit-sequence as a
-- permutation; the witness tower's proven Lehmer bijection
-- (WitnessTower.Sn.enumerate / Decompose) is the gluing, ALWAYS unobstructed
-- (H¹ = 0) — the dual of the contextuality obstruction
-- (Algebra.Wedge.Contextuality, H¹ ≠ 0).
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.PackedBridge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙)
open import Substrate.Algebra.Wedge.Graded.Morphism using (GradedDivStrMorphism)
open import Substrate.Algebra.Wedge.VecGraded using (vec-graded)
open import Substrate.WitnessTower.Wedge.Graded using (tower-graded)
open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)

------------------------------------------------------------------------
-- 1. A binary digit picks a witness insertion slot (grade-aware).
------------------------------------------------------------------------

slot : {n : ℕ} → Fin 2 → Fin (suc n)
slot         fzero        = fzero
slot {zero}  (fsuc fzero) = fzero
slot {suc n} (fsuc fzero) = fsuc fzero

-- 2. Decode a binary digit-sequence into a permutation (fold insert-at).
decode : {n : ℕ} → Vec (Fin 2) n → Perm n
decode []      = []
decode (a ∷ v) = insert-at (slot a) (decode v)

------------------------------------------------------------------------
-- 3. THE MORPHISM: the binary carrier → the witness tower. respects-recon
--    holds by refl (decode is defined exactly as insert-at ∘ slot).
------------------------------------------------------------------------

packed→witness : GradedDivStrMorphism (vec-graded (Fin 2)) tower-graded
packed→witness = record
  { map-C = decode
  ; map-R = slot
  ; respects-recon = λ n v a → refl
  }

------------------------------------------------------------------------
-- 4. The cell's ℤ/2 group action (the detector flip / seat-swap) and its
--    image as the witness S₂ slot-swap at grade 1.
------------------------------------------------------------------------

-- the detector's F₂ outcome IS the binary digit.
f2→fin2 : F₂ → Fin 2
f2→fin2 𝟘 = fzero
f2→fin2 𝟙 = fsuc fzero

-- the ℤ/2 seat-swap (= detector flip).
fin2-swap : Fin 2 → Fin 2
fin2-swap fzero        = fsuc fzero
fin2-swap (fsuc fzero) = fzero

fin2-swap-invol : (a : Fin 2) → fin2-swap (fin2-swap a) ≡ a
fin2-swap-invol fzero        = refl
fin2-swap-invol (fsuc fzero) = refl

-- at grade 1 the binary digit IS the witness slot, so the cell's ℤ/2 swap is
-- exactly the witness tower's S₂ slot-transposition there.
slot-grade1-id : (a : Fin 2) → slot {1} a ≡ a
slot-grade1-id fzero        = refl
slot-grade1-id (fsuc fzero) = refl
