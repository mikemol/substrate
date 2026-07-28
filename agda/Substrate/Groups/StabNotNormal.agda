------------------------------------------------------------------------
-- Substrate.Groups.StabNotNormal
--
-- The NEGATIVE POLE of the orbit-stabiliser characterization
-- (Substrate.Groups.StabNormalCharacterization): Stab(D) is NOT normal.
--
-- This is NOT a free-standing ¬. It is `member-normal→fixes-orbit` (the ⟹
-- direction of the characterising iff) read at a CONCRETE orbit-fixing
-- FAILURE: if Stab(D)'s obligation held, every element of Stab(D) would fix
-- every point of orbit(D); but swapCS = (C S) ∈ Stab D (it fixes D) MOVES the
-- orbit point C = apply (D C) D — sending it to S. So normality would force
-- S ≡ C. The non-normality IS that orbit-fixing failure, transported through
-- the positive characterization — the degenerate (negative) reading of the
-- same structure whose positive reading is fixed→member-normal.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.StabNotNormal where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Empty using (⊥)
open import Substrate.Axes.Axis using (Axis; D; C; S; W)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.StabNormalCharacterization
  using (member-normal; member-normal→fixes-orbit)

-- the orbit-mover (D C): sends D ↦ C, exhibiting C ∈ orbit(D). Its own inverse.
swapDC : Permutation
swapDC = record
  { apply = λ { D → C ; C → D ; S → S ; W → W }
  ; invₐ  = λ { D → C ; C → D ; S → S ; W → W }
  ; inv-l = λ { D → refl ; C → refl ; S → refl ; W → refl }
  ; inv-r = λ { D → refl ; C → refl ; S → refl ; W → refl }
  }

-- swapCS = (C S) ∈ Stab D (fixes D) but does NOT fix the orbit point C. Self-inverse.
swapCS : Permutation
swapCS = record
  { apply = λ { D → D ; C → S ; S → C ; W → W }
  ; invₐ  = λ { D → D ; C → S ; S → C ; W → W }
  ; inv-l = λ { D → refl ; C → refl ; S → refl ; W → refl }
  ; inv-r = λ { D → refl ; C → refl ; S → refl ; W → refl }
  }

-- distinct Axis constructors are not equal.
S≢C : S ≡ C → ⊥
S≢C ()

-- Stab(D) is NOT normal — the negative pole. member-normal→fixes-orbit would
-- make swapCS (∈ Stab D, witnessed by refl : apply swapCS D ≡ D) fix the
-- orbit point apply swapDC D = C; but apply swapCS C = S, so it reduces to
-- S ≡ C, which is absurd.
StabD-not-normal : ¬ (member-normal D)
StabD-not-normal mn = S≢C (member-normal→fixes-orbit {D} mn swapDC swapCS refl)
