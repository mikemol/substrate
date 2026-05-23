------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN
--
-- act-ε-N: act s e ≡ e (every action preserves V₄'s identity).
-- Proof via the canonical-case dispatcher act-ε-N-on-canonical
-- (6 refls covering the S₃ Cayley table).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Axioms.ActEpsilonN where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Foundation.Product using (_,_)
open import Substrate.Foundation.Fin.Literals using (₂; ₃; ₄)
open import Substrate.Foundation.Fin using (zero; suc)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Groups.Actions.S3-on-V4.Dispatch using (act; act-on-canonical)

act-ε-N-on-canonical : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h →
                       act-on-canonical n h e ≡ e
act-ε-N-on-canonical (Z₃.c-pos zero)  (Z₂.c-pos zero) = refl
act-ε-N-on-canonical (Z₃.c-pos (suc zero))  (Z₂.c-pos zero) = refl
act-ε-N-on-canonical (Z₃.c-pos ₂) (Z₂.c-pos zero) = refl
act-ε-N-on-canonical (Z₃.c-pos zero)  (Z₂.c-pos (suc zero)) = refl
act-ε-N-on-canonical (Z₃.c-pos (suc zero))  (Z₂.c-pos (suc zero)) = refl
act-ε-N-on-canonical (Z₃.c-pos ₂) (Z₂.c-pos (suc zero)) = refl

act-ε-N : ∀ s → act s e ≡ e
act-ε-N (n , h) = act-ε-N-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)
