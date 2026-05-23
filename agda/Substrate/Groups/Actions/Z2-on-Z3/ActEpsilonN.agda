------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN
--
-- act-ε-N: every Z/2 element fixes Z/3's identity.
--
-- For canonical h ∈ {[], [a]}: act-letter h [] is either [] (identity)
-- or Z₃.inv [] = [] (inversion of identity). Both = [] = Z₃G.ε.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActEpsilonN where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Groups.Coxeter.Word using ([])
open import Substrate.Foundation.Eq using (_≡_; refl; cong)
open import Substrate.Foundation.Fin.Literals using (₁; ₂; ₃)
open import Substrate.Foundation.Fin using (zero; suc)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)

act-letter-ε : ∀ {h} → Z₂.Canonical h → act-letter h [] ≡ []
act-letter-ε (Z₂.c-pos zero) = refl
act-letter-ε (Z₂.c-pos ₁) = refl

act-ε-N : ∀ h → act h Z₃G.ε Z₃G.≈ Z₃G.ε
act-ε-N h =
  -- act h [] = act-letter (Z₂.normalize h) (Z₃.normalize []) = act-letter (Z₂.normalize h) [].
  -- Z₃.normalize of this = Z₃.normalize [] = [] via act-letter-ε.
  cong Z₃.normalize (act-letter-ε (Z₂.normalize-canonical h))
