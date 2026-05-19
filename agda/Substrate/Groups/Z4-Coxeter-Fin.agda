------------------------------------------------------------------------
-- Substrate.Groups.Z4-Coxeter-Fin
--
-- The full Z₄-Coxeter ↔ Fin 4 chain in one module: bijection,
-- action-of-a, and HasOrderPerm derivation.
--
-- Mirrors the Z₃ chain (Z3-Coxeter-Fin / Z3-Coxeter-Action /
-- Z3-Coxeter-HasOrderPerm) at n=4. The split-vs-combined granularity
-- is a presentation choice; here we keep all three pieces together
-- to demonstrate the mechanical reusability of the pattern.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: Z₄-Coxeter's relation
-- `a⁴ = ε` (insert-fourth-power) is the structural source of truth
-- for σ₄'s order on Fin 4.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z4-Coxeter-Fin where

open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z4-Coxeter as Z₄
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cycle4
  using (σ₄)

------------------------------------------------------------------------
-- N-1: canonical-to-Fin / Fin-to-canonical bijection.
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₄.Gen} → Z₄.Canonical w → Fin 4
canonical-to-Fin Z₄.c-ε   = zero
canonical-to-Fin Z₄.c-a   = suc zero
canonical-to-Fin Z₄.c-aa  = suc (suc zero)
canonical-to-Fin Z₄.c-aaa = suc (suc (suc zero))

Fin-to-canonical : Fin 4 → Σ (Word Z₄.Gen) Z₄.Canonical
Fin-to-canonical zero                            = [] , Z₄.c-ε
Fin-to-canonical (suc zero)                      = (Z₄.a ∷ []) , Z₄.c-a
Fin-to-canonical (suc (suc zero))                = (Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aa
Fin-to-canonical (suc (suc (suc zero)))          = (Z₄.a ∷ Z₄.a ∷ Z₄.a ∷ []) , Z₄.c-aaa

Fin-roundtrip : (i : Fin 4) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                            = refl
Fin-roundtrip (suc zero)                      = refl
Fin-roundtrip (suc (suc zero))                = refl
Fin-roundtrip (suc (suc (suc zero)))          = refl

canonical-roundtrip : {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₄.c-ε   = refl
canonical-roundtrip Z₄.c-a   = refl
canonical-roundtrip Z₄.c-aa  = refl
canonical-roundtrip Z₄.c-aaa = refl

------------------------------------------------------------------------
-- N-2: action-of-a-is-σ₄ — Z₄-Coxeter's `insert a` corresponds to σ₄
-- on Fin 4 via the bijection.
------------------------------------------------------------------------

action-of-a-is-σ₄ :
  {w : Word Z₄.Gen} (c : Z₄.Canonical w) →
  canonical-to-Fin (Z₄.insert-canonical Z₄.a c) ≡ σ₄ (canonical-to-Fin c)
action-of-a-is-σ₄ Z₄.c-ε   = refl
action-of-a-is-σ₄ Z₄.c-a   = refl
action-of-a-is-σ₄ Z₄.c-aa  = refl
action-of-a-is-σ₄ Z₄.c-aaa = refl

------------------------------------------------------------------------
-- N-3: σ₄-HasOrderPerm-from-Z4-Coxeter — order witness via the
-- Coxeter route at n=4.
--
-- Mirror of σ₃-HasOrderPerm-from-Z3-Coxeter. Per inhabitant of Fin 4,
-- the proof is refl after unfolding through the bridge + insert-fourth-
-- power. Source of truth: Z₄-Coxeter's relation `a⁴ = ε`.
------------------------------------------------------------------------

σ₄-HasOrderPerm-from-Z4-Coxeter : HasOrderPerm σ₄ 4
σ₄-HasOrderPerm-from-Z4-Coxeter zero                            = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc zero)                      = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc (suc zero))                = refl
σ₄-HasOrderPerm-from-Z4-Coxeter (suc (suc (suc zero)))          = refl

------------------------------------------------------------------------
-- N-4: Capstone — Z₄ word-algebra connection complete.
--
-- After this slice, the substrate has both Z₃ and Z₄ examples
-- demonstrating the word-algebra → Fin n → basis-permutation-Linear
-- → HasOrder chain. The pattern is mechanical: any future Zₙ-Coxeter
-- instance gets the same chain via the same proof structure.
--
-- The 10-slice arc closes with:
--
--   * Z₃, Z₄, Z₅ Coxeter modules + Group adapters (Block A).
--   * Z₃ bijection + action + HasOrderPerm route (Block B).
--   * HasOrderPerm-multiple-Linear + HasLagrangeOrder-from-multiples
--     (Block C — Linear-level closures).
--   * Z₄ full chain in this module (Block D capstone).
--
-- Z₅ chain is deferred but structurally identical; can be added when
-- a concrete order-5 use site appears.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this completes the
-- substrate-native cyclic-torsion architecture. Stdlib's
-- Data.Fin.Permutation / Data.Nat.DivMod are not used; the Coxeter
-- Word framework's canonical-form discipline is the substrate's
-- alternative.
--
-- Deferred follow-ons:
--
--   * **σ₃-from-Coxeter** / **σ₄-from-Coxeter**: redefine the
--     cyclic-shift functions structurally via the bijection + action
--     rather than as per-case pattern matches. Makes the Cycle3/Cycle4
--     modules derived rather than parallel.
--
--   * **Z₅ chain**: bijection + action + HasOrderPerm at n=5,
--     mirroring this module's pattern.
--
--   * **Generic-Zₙ-Fin via length-indexed Canonical**: a generic-
--     over-n version where Canonical is indexed by Fin n (length
--     witness) and the bijection is structural. Substantial design
--     work; deferred until a use site demands it.
------------------------------------------------------------------------
