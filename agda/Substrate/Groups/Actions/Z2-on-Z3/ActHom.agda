------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActHom
--
-- act-hom: distributivity over Z/3 multiplication.
-- act h (n₁ ∙ n₂) ≈ act h n₁ ∙ act h n₂.
--
-- Case on canonical h. For c-ε: both sides ≈ n₁ ∙ n₂.
-- For c-a: uses Z₃.inv-distrib-canonical (Z/3 is abelian, so inv is
-- a homomorphism).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActHom where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)

-- Helper: act-letter h (n₁ ·₃ n₂) vs (act-letter h n₁) ·₃ (act-letter h n₂)
-- after normalize. 2 cases on canonical h.
act-letter-hom :
  ∀ {h} (c : Z₂.Canonical h)
    {n₁ n₂} (c-n₁ : Z₃.Canonical n₁) (c-n₂ : Z₃.Canonical n₂) →
  Z₃.normalize (act-letter h (n₁ Z₃G.· n₂)) ≡
  Z₃.normalize (act-letter h n₁ Z₃G.· act-letter h n₂)
act-letter-hom Z₂.c-ε {n₁} {n₂} c-n₁ c-n₂ =
  -- LHS: Z₃.normalize (n₁ ·₃ n₂) = Z₃.normalize (Z₃.normalize (n₁ ++ n₂)) = Z₃.normalize (n₁ ++ n₂).
  -- RHS: Z₃.normalize (n₁ ·₃ n₂) = same.
  refl
act-letter-hom Z₂.c-a {n₁} {n₂} c-n₁ c-n₂ =
  -- LHS evaluates to: Z₃.normalize (Z₃.inv (Z₃.normalize (n₁ ++ n₂))).
  -- RHS evaluates to: Z₃.normalize (Z₃.normalize (Z₃.inv n₁ ++ Z₃.inv n₂)).
  trans (Z₃.inv-distrib-canonical c-n₁ c-n₂)
        (sym (Z₃.normalize-idem (Z₃.inv n₁ ++ Z₃.inv n₂)))

act-hom : ∀ h n₁ n₂ → act h (n₁ Z₃G.· n₂) Z₃G.≈ (act h n₁ Z₃G.· act h n₂)
act-hom h n₁ n₂ =
  let
    c-h = Z₂.normalize-canonical h
    c-n₁ = Z₃.normalize-canonical n₁
    c-n₂ = Z₃.normalize-canonical n₂
    bridge-· : Z₃.normalize (n₁ Z₃G.· n₂) ≡ Z₃.normalize n₁ Z₃G.· Z₃.normalize n₂
    bridge-· = trans (Z₃.normalize-idem (n₁ ++ n₂)) (Z₃.normalize-distrib n₁ n₂)
  in
  trans (cong Z₃.normalize (cong (act-letter (Z₂.normalize h)) bridge-·))
        (act-letter-hom c-h c-n₁ c-n₂)
