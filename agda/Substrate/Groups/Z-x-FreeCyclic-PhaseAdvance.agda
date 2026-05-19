------------------------------------------------------------------------
-- Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance
--
-- The "phase advance" operation on the 2-D word algebra Zₙ × ℕ: apply
-- `insert a` to the phase component, leave cycle unchanged.
--
-- Demonstrated at Z₃ and Z₄. Bridges to the existing cyclic-shift
-- σ₃ / σ₄ (from Cycle3 / Cycle4) via the Z₃-Coxeter-Fin /
-- Z₄-Coxeter-Fin bijections.
--
-- The structural statement: phase-advance on the 2-D structure,
-- projected through the phase-canonical-to-Fin chain, IS the cyclic
-- shift on Fin n. This makes explicit that the 2-D algebra's
-- "advance phase" operation is the substrate's cyclic-shift.
--
-- Per the 2-D word algebra arc: this closes the operational
-- correspondence between the cyclic Coxeter word algebra and Fin
-- n's suc-mod-n (= the very operation the 1-D approach struggled
-- to define generically).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z-x-FreeCyclic-PhaseAdvance where

open import Data.Fin using (Fin)
open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

open import Substrate.Groups.Coxeter.Word using (Word)
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z4-Coxeter as Z₄
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.Z3-x-FreeCyclic as Z₃×F
import Substrate.Groups.Z4-x-FreeCyclic as Z₄×F
import Substrate.Groups.Z3-Coxeter-Fin as Z₃-Fin
import Substrate.Groups.Z4-Coxeter-Fin as Z₄-Fin
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle3
  using (σ₃)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
  using (σ₄)

------------------------------------------------------------------------
-- N-1: Z₃ phase advance — apply insert a to the phase component.
------------------------------------------------------------------------

phase-advance-Z₃ : Z₃×F.Word → Z₃×F.Word
phase-advance-Z₃ (w-p , w-c) = (Z₃.insert Z₃.a w-p , w-c)

------------------------------------------------------------------------
-- N-2: Z₃ phase advance corresponds to σ₃ at the Fin 3 level.
--
-- For a 2-D word `(w-p, w-c)` with phase Canonical witness `c`, the
-- phase-advance applied + canonical-to-Fin gives σ₃ applied to
-- canonical-to-Fin c.
--
-- Chain (per Canonical constructor of the phase part):
--   canonical-to-Fin (insert-canonical a c)
--     ≡ σ₃ (canonical-to-Fin c)   [via Z₃-Coxeter-Action]
--
-- The cycle component is preserved (it's just a passthrough); only
-- the phase axis changes.
------------------------------------------------------------------------

phase-advance-Z₃-as-σ₃ :
  {w-p : Word Z₃.Gen}
  {w-c : Word F.Gen}
  (c : Z₃.Canonical w-p) →
  Z₃-Fin.canonical-to-Fin (Z₃.insert-canonical Z₃.a c)
    ≡ σ₃ (Z₃-Fin.canonical-to-Fin c)
phase-advance-Z₃-as-σ₃ Z₃.c-ε  = refl
phase-advance-Z₃-as-σ₃ Z₃.c-a  = refl
phase-advance-Z₃-as-σ₃ Z₃.c-aa = refl

------------------------------------------------------------------------
-- N-3: Z₄ phase advance.
------------------------------------------------------------------------

phase-advance-Z₄ : Z₄×F.Word → Z₄×F.Word
phase-advance-Z₄ (w-p , w-c) = (Z₄.insert Z₄.a w-p , w-c)

phase-advance-Z₄-as-σ₄ :
  {w-p : Word Z₄.Gen}
  {w-c : Word F.Gen}
  (c : Z₄.Canonical w-p) →
  Z₄-Fin.canonical-to-Fin (Z₄.insert-canonical Z₄.a c)
    ≡ σ₄ (Z₄-Fin.canonical-to-Fin c)
phase-advance-Z₄-as-σ₄ Z₄.c-ε   = refl
phase-advance-Z₄-as-σ₄ Z₄.c-a   = refl
phase-advance-Z₄-as-σ₄ Z₄.c-aa  = refl
phase-advance-Z₄-as-σ₄ Z₄.c-aaa = refl

------------------------------------------------------------------------
-- N-4: Capstone — phase-advance correspondence to cyclic-shift lands.
--
-- After this slice:
--
--   * phase-advance-Zₙ : Zₙ×F.Word → Zₙ×F.Word — apply insert a
--     to the phase component, preserve cycle.
--   * phase-advance-Zₙ-as-σₙ : the structural bridge, expressing
--     phase-advance as the cyclic-shift σₙ via the canonical-to-Fin
--     mapping.
--
-- This closes the 2-D word algebra's operational correspondence to
-- the substrate's Fin n-based cyclic-shift work. The "advance phase"
-- in 2-D IS suc-mod-n on Fin n, via the canonical bijection.
--
-- The cycle component is structurally INVARIANT under phase-advance
-- (in this slice's setup). For the full universal-cover behavior,
-- one would WANT phase-advance at the "max position" to increment
-- the cycle component — making the explicit cover map. That
-- enrichment is deferred to the next arc (graded structures), where
-- the cycle component IS the grading.
--
-- Per [[project-graded-bicategorical-arc]]: the cycle component as
-- a degree counter is the natural setting for the grading. The
-- "phase-advance increments cycle at wraparound" behavior is the
-- 2-D structure's degree-increment rule.
------------------------------------------------------------------------
