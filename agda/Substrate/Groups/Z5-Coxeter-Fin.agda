------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Fin
--
-- The full Z₅-Coxeter ↔ Fin 5 chain in one module: bijection,
-- action-of-a, and HasOrderPerm derivation.
--
-- Mirror of Z3-Coxeter-Fin and Z4-Coxeter-Fin at n=5. All three
-- pieces (bijection + action + order-witness) live together.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Fin where

open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)

import Substrate.Groups.Z5-Coxeter as Z₅
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle5
  using (σ₅)

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

------------------------------------------------------------------------
-- N-2: action-of-a-is-σ₅.
------------------------------------------------------------------------

action-of-a-is-σ₅ :
  {w : Word Z₅.Gen} (c : Z₅.Canonical w) →
  canonical-to-Fin (Z₅.insert-canonical Z₅.a c) ≡ σ₅ (canonical-to-Fin c)
action-of-a-is-σ₅ Z₅.c-ε    = refl
action-of-a-is-σ₅ Z₅.c-a    = refl
action-of-a-is-σ₅ Z₅.c-aa   = refl
action-of-a-is-σ₅ Z₅.c-aaa  = refl
action-of-a-is-σ₅ Z₅.c-aaaa = refl

------------------------------------------------------------------------
-- N-3: σ₅-HasOrderPerm via the Coxeter route.
------------------------------------------------------------------------

σ₅-HasOrderPerm-from-Z5-Coxeter : HasOrderPerm σ₅ 5
σ₅-HasOrderPerm-from-Z5-Coxeter zero                                  = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc zero)                            = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc zero))                      = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc (suc zero)))                = refl
σ₅-HasOrderPerm-from-Z5-Coxeter (suc (suc (suc (suc zero))))          = refl

------------------------------------------------------------------------
-- N-4: Capstone — Z₅ word-algebra connection complete (combined).
--
-- Replaces the prior 3-file split (Z5-Coxeter-Fin / Z5-Coxeter-Action /
-- Z5-Coxeter-HasOrderPerm) with a single combined module, matching
-- Z3 and Z4.
------------------------------------------------------------------------
