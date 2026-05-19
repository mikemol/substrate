------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin
--
-- The bijection between Z5-Coxeter's Canonical word forms and Fin 5.
--
-- Mirror of Z3-Coxeter-Fin and Z4-Coxeter-Fin at n=5.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin where

open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- N-1: canonical-to-Fin / Fin-to-canonical bijection.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₅.Gen} → Z₅.Canonical w → Fin 5
canonical-to-Fin Z₅.c-ε    = zero
canonical-to-Fin Z₅.c-a    = suc zero
canonical-to-Fin Z₅.c-aa   = suc (suc zero)
canonical-to-Fin Z₅.c-aaa  = suc (suc (suc zero))
canonical-to-Fin Z₅.c-aaaa = suc (suc (suc (suc zero)))

Fin-to-canonical : Fin 5 → Σ (Word Z₅.Gen) Z₅.Canonical
Fin-to-canonical zero                                  = [] , Z₅.c-ε
Fin-to-canonical (suc zero)                            = (Z₅.a ∷ []) , Z₅.c-a
Fin-to-canonical (suc (suc zero))                      = (Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aa
Fin-to-canonical (suc (suc (suc zero)))                = (Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaa
Fin-to-canonical (suc (suc (suc (suc zero))))          = (Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ Z₅.a ∷ []) , Z₅.c-aaaa

Fin-roundtrip : (i : Fin 5) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                                  = refl
Fin-roundtrip (suc zero)                            = refl
Fin-roundtrip (suc (suc zero))                      = refl
Fin-roundtrip (suc (suc (suc zero)))                = refl
Fin-roundtrip (suc (suc (suc (suc zero))))          = refl

canonical-roundtrip : {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₅.c-ε    = refl
canonical-roundtrip Z₅.c-a    = refl
canonical-roundtrip Z₅.c-aa   = refl
canonical-roundtrip Z₅.c-aaa  = refl
canonical-roundtrip Z₅.c-aaaa = refl
