------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.ShiftRowsFace
--
-- Ⓐ.shiftrows — the PERMUTATION FACE of AES ShiftRows, in the Cryptographic-
-- Total-Space discipline: a new face + its by-construction invertibility + the
-- EQUIVALENCE morphism to the existing byte-face (`Round.ShiftRows`). Nothing is
-- eliminated; `Round.ShiftRows`/`shift-rt` stay — this adds the face that makes
-- the round-trip *inevitable* rather than a 256-cell `refl`.
--
-- THE FACE: ShiftRows is `out(i,j) = in((i+j) mod 4, j)` — each row cyclically
-- rotated by its index. So its per-cell index map is `cyclic-suc^j` — the EXACT
-- `Cyclic` machinery validated in the opacity experiment. `ShiftRows-cyc` builds
-- it from `cyclic-suc`; `shiftrows-cyc≡` proves it equals the FIPS byte-face.
--
-- THE BY-CONSTRUCTION INVERTIBILITY (the reusable shadow): `permV` (permute a Vec
-- by an index map) with `permV-rt` — a permutation's round-trip follows from its
-- index map having an inverse (`f ∘ g = id` ⟹ `permV g ∘ permV f = id`), proven
-- generically via `lookup∘tabulate` + `tabulate∘lookup`. ShiftRows' rotations
-- instantiate this: `cyclic-suc^j` is invertible by `cyclic-suc`'s order. (The
-- full 2-D assembly of `shift-rt` through `permV-rt` is the next increment; this
-- lands the face, the equivalence, and the generic by-construction primitive.)
--
-- Zero postulates, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.F2.AES.ShiftRowsFace where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; lookup; tabulate)
open import Substrate.Foundation.Vec.Properties
  using (lookup∘tabulate; tabulate∘lookup; tabulate-cong)
open import Substrate.Foundation.Eq using (_≡_; refl; trans; cong)
open import Substrate.Algebra.Nat.CyclicSuc using (cyclic-suc)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate using (σ-iterate)
open import Substrate.Algebra.F2.AES.Round using (State; ShiftRows)

private
  variable
    A : Set

------------------------------------------------------------------------
-- 1. The generic permutation face + BY-CONSTRUCTION invertibility (the shadow).
------------------------------------------------------------------------

permV : {n : ℕ} → (Fin n → Fin n) → Vec A n → Vec A n
permV σ v = tabulate (λ i → lookup v (σ i))

permV-∘ : {n : ℕ} (g f : Fin n → Fin n) (v : Vec A n) →
          permV g (permV f v) ≡ permV (λ i → f (g i)) v
permV-∘ g f v =
  tabulate-cong _ _ (λ i → lookup∘tabulate (λ k → lookup v (f k)) (g i))

-- the round-trip is INEVITABLE from the index map's inverse — never a per-cell scan.
permV-rt : {n : ℕ} (g f : Fin n → Fin n) (v : Vec A n) →
           ((i : Fin n) → f (g i) ≡ i) → permV g (permV f v) ≡ v
permV-rt g f v inv =
  trans (permV-∘ g f v)
        (trans (tabulate-cong _ _ (λ i → cong (lookup v) (inv i)))
               (tabulate∘lookup v))

------------------------------------------------------------------------
-- 2. ShiftRows as cyclic rotation (the face) — out(i,j) = in(cyclic-suc^j i, j).
------------------------------------------------------------------------

rot : Fin 4 → Fin 4 → Fin 4
rot i j = σ-iterate (toℕ j) cyclic-suc i        -- (i + j) mod 4, via the Cyclic machinery

ShiftRows-cyc : State → State
ShiftRows-cyc s = tabulate (λ i → tabulate (λ j → lookup (lookup s (rot i j)) j))

------------------------------------------------------------------------
-- 3. THE EQUIVALENCE: the cyclic face equals the FIPS byte-face (closure witness).
------------------------------------------------------------------------

shiftrows-cyc≡ : (s : State) → ShiftRows-cyc s ≡ ShiftRows s
shiftrows-cyc≡ ((b00 ∷ b01 ∷ b02 ∷ b03 ∷ []) ∷ (b10 ∷ b11 ∷ b12 ∷ b13 ∷ [])
              ∷ (b20 ∷ b21 ∷ b22 ∷ b23 ∷ []) ∷ (b30 ∷ b31 ∷ b32 ∷ b33 ∷ []) ∷ []) = refl
