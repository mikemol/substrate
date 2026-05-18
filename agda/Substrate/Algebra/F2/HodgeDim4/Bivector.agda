------------------------------------------------------------------------
-- Substrate.Algebra.F2.HodgeDim4.Bivector
--
-- N-1 + N-2 of M-11.dim4. The bivector space Λ²(F₂⁴) and its
-- complement involution.
--
-- Λ²(F₂⁴) has dim C(4,2) = 6 over F₂; we represent bivectors as
-- `Bivector = Vector 6`. Each coordinate is the F₂ coefficient of one
-- of the 6 basis 2-blades `e_i ∧ e_j` for `0 ≤ i < j ≤ 3`.
--
-- Basis 2-blade index encoding (lex-order on (i, j) for i < j):
--
--   Fin 6 index | 2-blade   | Complement | Complement index
--   ------------|-----------|------------|-----------------
--   0           | e₀ ∧ e₁  | e₂ ∧ e₃   | 5
--   1           | e₀ ∧ e₂  | e₁ ∧ e₃   | 4
--   2           | e₀ ∧ e₃  | e₁ ∧ e₂   | 3
--   3           | e₁ ∧ e₂  | e₀ ∧ e₃   | 2
--   4           | e₁ ∧ e₃  | e₀ ∧ e₂   | 1
--   5           | e₂ ∧ e₃  | e₀ ∧ e₁   | 0
--
-- The `complement` map is therefore the **index-reversal involution**
-- on Fin 6: 0↔5, 1↔4, 2↔3. Three fixed-point-free pairs.
--
-- This involution will serve as the basis-image data for the
-- Hodge ★ Linear 6 6 in N-3.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.HodgeDim4.Bivector where

open import Data.Fin using (Fin; zero; suc)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl)

open import Substrate.Algebra.F2
open import Substrate.Algebra.F2.Vector

------------------------------------------------------------------------
-- The bivector type.
------------------------------------------------------------------------

Bivector : Set
Bivector = Vector 6

------------------------------------------------------------------------
-- Named Fin 6 indices for the 6 basis 2-blades (convenience).
------------------------------------------------------------------------

b₀₁ b₀₂ b₀₃ b₁₂ b₁₃ b₂₃ : Fin 6
b₀₁ = zero                                  -- e₀ ∧ e₁
b₀₂ = suc zero                              -- e₀ ∧ e₂
b₀₃ = suc (suc zero)                        -- e₀ ∧ e₃
b₁₂ = suc (suc (suc zero))                  -- e₁ ∧ e₂
b₁₃ = suc (suc (suc (suc zero)))            -- e₁ ∧ e₃
b₂₃ = suc (suc (suc (suc (suc zero))))      -- e₂ ∧ e₃

------------------------------------------------------------------------
-- The complement map: each basis 2-blade index → its Hodge-dual index.
------------------------------------------------------------------------

complement : Fin 6 → Fin 6
complement zero                                  = b₂₃   -- {0,1} ↔ {2,3}
complement (suc zero)                            = b₁₃   -- {0,2} ↔ {1,3}
complement (suc (suc zero))                      = b₁₂   -- {0,3} ↔ {1,2}
complement (suc (suc (suc zero)))                = b₀₃   -- {1,2} ↔ {0,3}
complement (suc (suc (suc (suc zero))))          = b₀₂   -- {1,3} ↔ {0,2}
complement (suc (suc (suc (suc (suc _)))))       = b₀₁   -- {2,3} ↔ {0,1}

------------------------------------------------------------------------
-- The complement is an involution: complement (complement i) ≡ i.
--
-- 6 cases, each closing by refl.
------------------------------------------------------------------------

complement-involution : (i : Fin 6) → complement (complement i) ≡ i
complement-involution zero                                  = refl
complement-involution (suc zero)                            = refl
complement-involution (suc (suc zero))                      = refl
complement-involution (suc (suc (suc zero)))                = refl
complement-involution (suc (suc (suc (suc zero))))          = refl
complement-involution (suc (suc (suc (suc (suc zero)))))    = refl
