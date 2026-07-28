------------------------------------------------------------------------
-- Substrate.Logic.Evidence.ElAtlas.OrbitCloud  (Ⓟ.1 — orbit-frame permutations as proved tables)
--
-- The orbit cloud (POINT_CLOUD §0): a generic cycle-space vector sent through
-- all (n+1)! vertex-permutation FRAMES gives the cloud, whose cardinality is the
-- combinatorial count (rung 2 → 2, rung 3 → 22-not-24, rung 4 → 120). The frames
-- are PERMUTATIONS — and a permutation IS a proved lookup table, exactly the AES
-- S-box shape (SBoxTable: a Vec of images + a banked correctness proof + cheap
-- `idx` lookups). This rung lays the proved-table foundation on the K₃ frames.
--
-- A frame = a PermTable (Vec of images) that is a BIJECTION, witnessed by an
-- inverse table whose round-trips reduce to the identity (the exhaustive `refl`-
-- per-input check — the lookup analog of SBoxTable's all-vec reflection). The
-- forcing is a table index, never a recomputed action.
--
-- Scope: Ⓟ.2 = all (n+1)! frames + the cycle-space action (vertex perm → edge
-- perm → Cpinv·P_edge·C on the cycle space) + the orbit CARDINALITY (rung 2 → 2
-- by sign; the generic-vector near-degeneracy for rung 3 → 22). Ⓟ.3 = rung 3/4
-- with the 24/120 action matrices as proved tables. Here: PermTable, the frame
-- bijection witness, and the K₃ rotation (order-3) + reflection frames proved.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.ElAtlas.OrbitCloud where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- A permutation as a lookup table; application is `lookup` (a table index).
------------------------------------------------------------------------

PermTable : ℕ → Set
PermTable n = Vec (Fin n) n

appT : {n : ℕ} → PermTable n → Fin n → Fin n
appT t i = lookup t i

------------------------------------------------------------------------
-- A FRAME is a proved-bijection table: an inverse table whose round-trips
-- reduce to the identity (the exhaustive refl-per-input check = the lookup
-- analog of SBoxTable's all-vec reflection).
------------------------------------------------------------------------

record IsFrame {n : ℕ} (σ : PermTable n) : Set where
  field
    inv      : PermTable n
    left-rt  : (i : Fin n) → appT inv (appT σ i) ≡ i
    right-rt : (i : Fin n) → appT σ (appT inv i) ≡ i

open IsFrame public

------------------------------------------------------------------------
-- K₃ orbit frames: vertex permutations of the triangle, as Fin-3 tables.
-- rot = the 3-cycle (0 1 2) (a rotation, even); swap = (0 1) (a reflection,
-- odd). Each proved a bijection by exhaustive round-trip (refl per Fin-3 case).
------------------------------------------------------------------------

rot : PermTable 3                                   -- 0↦1, 1↦2, 2↦0
rot = suc zero ∷ suc (suc zero) ∷ zero ∷ []

rot-frame : IsFrame rot
rot-frame = record
  { inv = suc (suc zero) ∷ zero ∷ suc zero ∷ []     -- the inverse 3-cycle (0 2 1)
  ; left-rt  = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }
  ; right-rt = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }
  }

-- rot has order 3 — it GENERATES the rotation subgroup of the K₃ frames
-- (the orbit-generating cyclic structure), proved by exhaustive lookup.
rot-order-3 : (i : Fin 3) → appT rot (appT rot (appT rot i)) ≡ i
rot-order-3 = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }

swap : PermTable 3                                  -- 0↔1, 2 fixed
swap = suc zero ∷ zero ∷ suc (suc zero) ∷ []

swap-frame : IsFrame swap
swap-frame = record
  { inv = swap                                      -- a transposition is its own inverse
  ; left-rt  = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }
  ; right-rt = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }
  }

-- swap has order 2 (involution) — the reflection frame.
swap-order-2 : (i : Fin 3) → appT swap (appT swap i) ≡ i
swap-order-2 = λ { zero → refl ; (suc zero) → refl ; (suc (suc zero)) → refl }
