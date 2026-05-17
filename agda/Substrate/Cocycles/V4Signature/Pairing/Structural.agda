------------------------------------------------------------------------
-- Substrate.Cocycles.V4Signature.Pairing.Structural
--
-- N-3 of the M-12 DBE plan. The bijection
--   Pairing ↔ V4-Nonzero
-- bundled as a `Bijection` (universal-property record).
--
-- Pairing is the bare 3-ctor enumeration in V4Signature.agda
-- (α-pair / β-pair / γ-pair). V4-Nonzero is the structural Fin 3 +
-- F₂² coords form. The bridge ↔ exposes the structural identification
-- so that downstream consumers can transport between the two.
--
-- All round-trips close by `refl`: the case-by-case forward/backward
-- are inverse-on-the-nose.
--
-- The structural identification is fixed once here (and documented
-- per [[feedback_ordering_is_chirality_choice]]):
--   α-pair ↔ v4nz-α (Fin-zero, coords = (𝟙, 𝟘))
--   β-pair ↔ v4nz-β (Fin-suc-zero, coords = (𝟘, 𝟙))
--   γ-pair ↔ v4nz-γ (Fin-suc-suc, coords = (𝟙, 𝟙))
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Cocycles.V4Signature.Pairing.Structural where

open import Data.Fin using (zero; suc)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

open import Substrate.Foundations.Bijection
open import Substrate.Algebra.F2.V4-Nonzero
open import Substrate.Cocycles.V4Signature using (Pairing; α-pair; β-pair; γ-pair)

------------------------------------------------------------------------
-- Forward: Pairing → V4-Nonzero.
------------------------------------------------------------------------

Pairing→V4-Nonzero : Pairing → V4-Nonzero
Pairing→V4-Nonzero α-pair = v4nz-α
Pairing→V4-Nonzero β-pair = v4nz-β
Pairing→V4-Nonzero γ-pair = v4nz-γ

------------------------------------------------------------------------
-- Backward: V4-Nonzero → Pairing.
--
-- The `suc (suc _)` catch-all is forced by Fin 3's structure: the
-- only inhabitant is `suc (suc zero) = v4nz-γ`.
------------------------------------------------------------------------

V4-Nonzero→Pairing : V4-Nonzero → Pairing
V4-Nonzero→Pairing zero          = α-pair
V4-Nonzero→Pairing (suc zero)    = β-pair
V4-Nonzero→Pairing (suc (suc _)) = γ-pair

------------------------------------------------------------------------
-- Round-trips.
------------------------------------------------------------------------

to-from-Pairing : (v : V4-Nonzero) → Pairing→V4-Nonzero (V4-Nonzero→Pairing v) ≡ v
to-from-Pairing zero          = refl
to-from-Pairing (suc zero)    = refl
to-from-Pairing (suc (suc zero)) = refl

from-to-Pairing : (p : Pairing) → V4-Nonzero→Pairing (Pairing→V4-Nonzero p) ≡ p
from-to-Pairing α-pair = refl
from-to-Pairing β-pair = refl
from-to-Pairing γ-pair = refl

------------------------------------------------------------------------
-- The Bijection bundle.
------------------------------------------------------------------------

Pairing↔V4-Nonzero : Bijection Pairing V4-Nonzero
Pairing↔V4-Nonzero = record
  { to      = Pairing→V4-Nonzero
  ; from    = V4-Nonzero→Pairing
  ; to-from = to-from-Pairing
  ; from-to = from-to-Pairing
  }
