------------------------------------------------------------------------
-- Substrate.Groups.StabNotNormal
--
-- The constructive ¬-witness that Stab(D) is NOT a normal subgroup of S₄ —
-- the △-tail (ŝ) the comment-overclaim arc recorded as a recipe in
-- Substrate.Groups.Subgroup (the old "Stab(X) is NOT normal" comment was an
-- unbacked negation; `Stab-conj-equivariant` proved the positive structure
-- and flagged this concrete witness).
--
-- Recipe: σ = (C S) ∈ Stab D (it fixes D); g = (D C); then the conjugate
-- (g · σ) · g⁻¹ sends D ↦ C ↦ S ↦ S = S ≠ D, so it does NOT fix D. Hence the
-- member-normal obligation `Stab D n → Stab D ((g·n)·g⁻¹)` (the field of an
-- S₄-NormalSubgroup over Stab-Subgroup D) is UNSATISFIABLE — a constructive
-- `→ ⊥`, not an absence-of-proof.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.StabNotNormal where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Axes using (Axis; D; C; S; W)
open import Substrate.Groups.S4 using (Permutation; _·_; _⁻¹; apply; invₐ; inv-l; inv-r)
open import Substrate.Groups.SemidirectProduct using (Stab)

-- the transposition (D C): swaps D, C; fixes S, W. Its own inverse.
swapDC : Permutation
swapDC = record
  { apply = λ { D → C ; C → D ; S → S ; W → W }
  ; invₐ  = λ { D → C ; C → D ; S → S ; W → W }
  ; inv-l = λ { D → refl ; C → refl ; S → refl ; W → refl }
  ; inv-r = λ { D → refl ; C → refl ; S → refl ; W → refl }
  }

-- the transposition (C S): swaps C, S; fixes D, W. Its own inverse.
swapCS : Permutation
swapCS = record
  { apply = λ { D → D ; C → S ; S → C ; W → W }
  ; invₐ  = λ { D → D ; C → S ; S → C ; W → W }
  ; inv-l = λ { D → refl ; C → refl ; S → refl ; W → refl }
  ; inv-r = λ { D → refl ; C → refl ; S → refl ; W → refl }
  }

-- distinct Axis constructors are not equal.
S≢D : S ≡ D → ⊥
S≢D ()

-- Stab(D) is NOT normal: the member-normal obligation cannot be met. The
-- conjugate (swapDC · swapCS) · swapDC⁻¹ applied to D computes (definitionally)
-- to S, so `Stab D ((g·n)·g⁻¹)` reduces to `S ≡ D`, which is absurd —
-- witnessed at g = (D C), n = (C S) ∈ Stab D.
StabD-not-normal :
  ¬ ({g n : Permutation} → Stab D n → Stab D ((g · n) · (g ⁻¹)))
StabD-not-normal normal = S≢D (normal {swapDC} {swapCS} refl)
