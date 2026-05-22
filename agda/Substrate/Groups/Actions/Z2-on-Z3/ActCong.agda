------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActCong
--
-- act-cong: the action depends only on the Z₂-normalize of h and the
-- Z₃-normalize of n, so action equalities transport directly.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActCong where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Foundation.Eq using (cong; cong₂)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)

act-cong : ∀ {h₁ h₂ n₁ n₂} → h₁ Z₂G.≈ h₂ → n₁ Z₃G.≈ n₂ →
           act h₁ n₁ Z₃G.≈ act h₂ n₂
act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq =
  -- act h n = act-letter (Z₂.normalize h) (Z₃.normalize n).
  -- act h₁ n₁ ≡ act h₂ n₂ propositionally via cong on act-letter.
  -- ≈ on top: Z₃.normalize equality preserved by cong.
  cong Z₃.normalize (cong₂ act-letter h-eq n-eq)
