------------------------------------------------------------------------
-- Substrate.Algebra.F2.GF256.Ring  (was GF256 §AI-6f)
--
-- Capstone: `GF256-Ring : Ring (Vector 8)`. Climb the AsField ladder by
-- record-wiring the laws from §Mul/§MulLaws. ONE additive monoid is shared
-- by the semiring AND the abelian group ⇒ `+-coherent = refl`; char 2 makes
-- every element its own additive inverse (`inv = id`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.GF256.Ring where

open import Substrate.Foundation.Eq using (refl)
open import Substrate.Algebra.F2.Vector using (Vector; _+ⱽ_; 𝟎ⱽ; +ⱽ-identityˡ; +ⱽ-identityʳ;
  +ⱽ-comm; +ⱽ-assoc; +ⱽ-self-inverse)
open import Substrate.Algebra.Magma using (Magma)
open import Substrate.Algebra.Semigroup using (Semigroup)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.F2.GF256.Idempotent using (one₈)
open import Substrate.Algebra.F2.GF256.Mul using (gmul; gmul-distribˡ; gmul-distribʳ)
open import Substrate.Algebra.F2.GF256.MulLaws using (gmul-identityˡ; gmul-identityʳ;
  gmul-zeroˡ; gmul-zeroʳ; gmul-assoc)

-- ONE additive monoid, shared by the semiring AND the abelian group ⇒ +-coherent = refl.
+ⱽ-monoid : Monoid (Vector 8)
+ⱽ-monoid = record
  { semigroup = record { magma = record { _·_ = _+ⱽ_ } ; ·-assoc = +ⱽ-assoc }
  ; ε = 𝟎ⱽ ; ε-left = +ⱽ-identityˡ ; ε-right = +ⱽ-identityʳ }

-- char 2: every element is its own additive inverse (inv = id, inv-law = self-inverse).
+ⱽ-abelian : AbelianGroup (Vector 8)
+ⱽ-abelian = record
  { group = record { monoid = +ⱽ-monoid ; inv = λ v → v
                   ; inv-left = +ⱽ-self-inverse ; inv-right = +ⱽ-self-inverse }
  ; ·-comm = +ⱽ-comm }

gmul-monoid : Monoid (Vector 8)
gmul-monoid = record
  { semigroup = record { magma = record { _·_ = gmul } ; ·-assoc = gmul-assoc }
  ; ε = one₈ ; ε-left = gmul-identityˡ ; ε-right = gmul-identityʳ }

GF256-Semiring : Semiring (Vector 8)
GF256-Semiring = record
  { +-monoid = +ⱽ-monoid ; *-monoid = gmul-monoid
  ; distrib-left = gmul-distribˡ ; distrib-right = gmul-distribʳ
  ; zero-absorb-left = gmul-zeroˡ ; zero-absorb-right = gmul-zeroʳ }

GF256-Ring : Ring (Vector 8)
GF256-Ring = record { semiring = GF256-Semiring ; +-abelian = +ⱽ-abelian ; +-coherent = refl }
