------------------------------------------------------------------------
-- Substrate.Groups.Z3-Coxeter-Fin
--
-- The bijection between Z3-Coxeter's Canonical word forms and Fin 3.
--
-- Z₃'s 3 canonical word forms ([], [a], [a,a]) are in 1-1 correspondence
-- with Fin 3's three inhabitants. This module establishes the
-- bijection explicitly, both directions and roundtrips, so downstream
-- code can route between word-algebra reasoning (Z3-Coxeter's
-- normalize/insert/cube-identity) and Fin-indexed reasoning (the
-- substrate's existing Cycle3 / basis-permutation-Linear infrastructure).
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this bijection is
-- the bridge that lets the word algebra's `insert a` operation
-- correspond to the cyclic-shift on Fin 3 — making the Z₃-Coxeter
-- relation `a³ = ε` the SOURCE OF TRUTH for `σ₃-HasOrderPerm`.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z3-Coxeter-Fin where

open import Data.Fin using (Fin; zero; suc)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality using (_≡_; refl)

import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

------------------------------------------------------------------------
-- N-1: canonical-to-Fin — extract the Fin 3 index from a Canonical
-- word.
--
-- The three Canonical constructors map to the three Fin 3 inhabitants:
--   c-ε  → 0
--   c-a  → 1
--   c-aa → 2
------------------------------------------------------------------------

canonical-to-Fin : {w : Word Z₃.Gen} → Z₃.Canonical w → Fin 3
canonical-to-Fin Z₃.c-ε  = zero
canonical-to-Fin Z₃.c-a  = suc zero
canonical-to-Fin Z₃.c-aa = suc (suc zero)

------------------------------------------------------------------------
-- N-2: Fin-to-canonical — build a Canonical word from a Fin 3 index.
--
-- The reverse direction. Produces both the underlying word AND the
-- Canonical witness as a Σ-pair (since the witness type depends on
-- the word).
------------------------------------------------------------------------

Fin-to-canonical : Fin 3 → Σ (Word Z₃.Gen) Z₃.Canonical
Fin-to-canonical zero                = [] , Z₃.c-ε
Fin-to-canonical (suc zero)          = (Z₃.a ∷ []) , Z₃.c-a
Fin-to-canonical (suc (suc zero))    = (Z₃.a ∷ Z₃.a ∷ []) , Z₃.c-aa

------------------------------------------------------------------------
-- N-3: Roundtrip — Fin direction.
--
-- canonical-to-Fin (snd (Fin-to-canonical i)) ≡ i  for every i : Fin 3.
-- Three refl cases.
------------------------------------------------------------------------

Fin-roundtrip : (i : Fin 3) →
  canonical-to-Fin (proj₂ (Fin-to-canonical i)) ≡ i
Fin-roundtrip zero                = refl
Fin-roundtrip (suc zero)          = refl
Fin-roundtrip (suc (suc zero))    = refl

------------------------------------------------------------------------
-- N-4: Roundtrip — Canonical direction.
--
-- The reverse roundtrip: starting from a Canonical witness, going to
-- Fin and back yields the same word + witness. Three refl cases
-- (one per Canonical constructor).
------------------------------------------------------------------------

canonical-roundtrip : {w : Word Z₃.Gen} (c : Z₃.Canonical w) →
  Fin-to-canonical (canonical-to-Fin c) ≡ (w , c)
canonical-roundtrip Z₃.c-ε  = refl
canonical-roundtrip Z₃.c-a  = refl
canonical-roundtrip Z₃.c-aa = refl

------------------------------------------------------------------------
-- N-5: Capstone — Z3-Coxeter's canonical forms ↔ Fin 3.
--
-- After this slice:
--
--   * canonical-to-Fin     : Canonical → Fin 3
--   * Fin-to-canonical     : Fin 3 → Σ Word Canonical
--   * Fin-roundtrip        : canonical-to-Fin ∘ snd ∘ Fin-to-canonical ≡ id
--   * canonical-roundtrip  : Fin-to-canonical ∘ canonical-to-Fin ≡ id
--
-- The bijection is the structural bridge for downstream slices to
-- transport the Z₃-Coxeter relation `a³ = ε` into a `HasOrderPerm`
-- witness on Fin 3.
--
-- Per [[feedback-roll-our-own-via-word-algebra]]: this bridge IS the
-- substrate-native alternative to "compute mod 3 on Fin" — instead
-- of arithmetic, we route through the Coxeter word algebra's
-- canonical-form discipline.
------------------------------------------------------------------------
