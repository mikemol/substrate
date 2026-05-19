------------------------------------------------------------------------
-- Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection
--
-- Phase projection for Z₅ × ℕ. Mirror at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-x-FreeCyclic-PhaseProjection where

open import Data.Product using (_×_; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality using (_≡_; refl; cong)

import Substrate.Groups.Z5-Coxeter as Z₅
import Substrate.Groups.FreeCyclic-Coxeter as F
import Substrate.Groups.Z5-x-FreeCyclic as Z₅×F
open import Substrate.Groups.Coxeter.Word using (Word)

phase-project : Z₅×F.Word → Word Z₅.Gen
phase-project = proj₁

phase-project-ε : phase-project Z₅×F.ε ≡ Z₅.ε
phase-project-ε = refl

phase-project-· :
  (a b : Z₅×F.Word) →
  phase-project (a Z₅×F.· b) ≡ phase-project a Z₅.· phase-project b
phase-project-· (a₁ , a₂) (b₁ , b₂) = refl

phase-project-normalize :
  (w : Z₅×F.Word) →
  phase-project (Z₅×F.normalize w) ≡ Z₅.normalize (phase-project w)
phase-project-normalize (w₁ , w₂) = refl
