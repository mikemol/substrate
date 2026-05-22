------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3.ActDot
--
-- act-∙: composition compatibility. act (h₁ ∙ h₂) n ≈ act h₁ (act h₂ n).
--
-- Strategy: bridge LHS through Z₂.normalize-idem + normalize-distrib
-- to the (Z₂.normalize h₁, Z₂.normalize h₂) form, then apply
-- act-letter-compose by case-analysis on canonical Z₂ pair.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3.ActDot where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Groups.Coxeter.Word using (_++_)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; sym; cong)

open import Substrate.Groups.Actions.Z2-on-Z3.Act using (act; act-letter)
open import Substrate.Groups.Actions.Z2-on-Z3.Canonical using (act-letter-canonical)

-- Helper: when canonical proofs of Z₂.normalize h are known, reduce
-- act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) X to
-- act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) X) for
-- canonical Z₃ X.
act-letter-compose :
  ∀ {h₁ h₂} (c₁ : Z₂.Canonical h₁) (c₂ : Z₂.Canonical h₂)
    {x} (c-x : Z₃.Canonical x) →
  act-letter (Z₂.normalize (h₁ ++ h₂)) x ≡
  act-letter h₁ (act-letter h₂ x)
act-letter-compose Z₂.c-ε Z₂.c-ε c-x = refl
act-letter-compose Z₂.c-ε Z₂.c-a c-x = refl
act-letter-compose Z₂.c-a Z₂.c-ε {x} c-x =
  -- LHS: act-letter (Z₂.normalize ([a] ++ [])) x = act-letter [a] x = Z₃.inv x.
  -- RHS: act-letter [a] (act-letter [] x) = act-letter [a] x = Z₃.inv x.
  refl
act-letter-compose Z₂.c-a Z₂.c-a {x} c-x =
  -- LHS: act-letter (Z₂.normalize ([a] ++ [a])) x = act-letter [] x = x.
  -- RHS: act-letter [a] (act-letter [a] x) = Z₃.inv (Z₃.inv x).
  -- For canonical x: Z₃.inv (Z₃.inv x) = x via inv-inv-canonical.
  sym (Z₃.inv-inv-canonical c-x)

act-∙ : ∀ h₁ h₂ n → act (h₁ Z₂G.· h₂) n Z₃G.≈ act h₁ (act h₂ n)
act-∙ h₁ h₂ n =
  let
    inner-n = Z₃.normalize n
    c-n = Z₃.normalize-canonical n
    c₁ = Z₂.normalize-canonical h₁
    c₂ = Z₂.normalize-canonical h₂
    bridge-h : Z₂.normalize (Z₂.normalize (h₁ ++ h₂)) ≡
               Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)
    bridge-h = trans (Z₂.normalize-idem (h₁ ++ h₂))
                     (Z₂.normalize-distrib h₁ h₂)
    composed : act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) inner-n ≡
               act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) inner-n)
    composed = act-letter-compose c₁ c₂ c-n
    inner-canonical : Z₃.normalize (act-letter (Z₂.normalize h₂) inner-n) ≡
                      act-letter (Z₂.normalize h₂) inner-n
    inner-canonical = Z₃.canonical-is-fixed (act-letter-canonical c₂ c-n)
  in
  trans (cong (λ x → Z₃.normalize (act-letter x inner-n)) bridge-h)
  (trans (cong Z₃.normalize composed)
         (sym (cong (λ x → Z₃.normalize (act-letter (Z₂.normalize h₁) x))
                    inner-canonical)))
