-- ⟡leibniz-det-alg probe. (--guardedness: outside the library, no .agda-lib flags.)
{-# OPTIONS --safe --without-K --guardedness #-}

module leibniz-probe where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _*_; _+_)
open import Substrate.Foundation.Fin using (Fin; zero; suc)
open import Substrate.Foundation.Fin.Punctured using (punchIn)
open import Substrate.Foundation.Fin.Combine using (combine)
open import Substrate.Foundation.Fin.RemQuot using (remQuot)
open import Substrate.Foundation.Product using (proj₁; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.WitnessTower.LehmerPath using (LehmerPath; start; _◂_; decode)
open import Substrate.WitnessTower.Wedge.OrientationUniversal
  using (LehmerAlgebra; fold)

module Mono (A : Set) (_*A_ : A → A → A) (1A : A) where

  -- a flat n×n matrix: index Fin (n * n), row-major via combine / remQuot.
  Mat : ℕ → Set
  Mat n = Fin (n * n) → A

  MonoC : ℕ → Set
  MonoC n = Mat n → A

  -- the (0,p) MINOR at the flat index: drop row 0, drop column p.
  -- ⚑ the implicits of `combine` MUST be pinned: `Mat n = Fin (n * n) → A` hides
  -- n behind multiplication, which is not injective, so Agda cannot recover the
  -- grade from the carrier type (the `_m * suc n = n * suc n` blocked constraint).
  minor : {n : ℕ} → Fin (suc n) → Mat (suc n) → Mat n
  minor {n} p M k =
    M (combine {suc n} {suc n}
         (suc (proj₁ (remQuot {n} n k)))
         (punchIn p (proj₂ (remQuot {n} n k))))

  -- decode (l ◂ p) = insert-at p (decode l) = p ∷ map (punchIn p) (decode l),
  -- so the new factor is M[0,p] and the rest is the grade-n monomial on the minor.
  mono-alg : LehmerAlgebra MonoC
  mono-alg = record
    { base = λ _ → 1A
    ; step = λ {n} c p → λ M → M (combine {suc n} {suc n} zero p) *A c (minor {n} p M)
    }

  mono : {n : ℕ} → LehmerPath n → Mat n → A
  mono = fold mono-alg

------------------------------------------------------------------------
-- POLE: at grade 2 the two Lehmer paths give the two 2x2 products.
------------------------------------------------------------------------

open Mono ℕ _*_ 1

-- M = [[a,b],[c,d]] flat: 0↦a 1↦b 2↦c 3↦d
M2 : Mat 2
M2 zero                     = 2   -- a
M2 (suc zero)               = 3   -- b
M2 (suc (suc zero))         = 5   -- c
M2 (suc (suc (suc zero)))   = 7   -- d

idPath swapPath : LehmerPath 2
idPath   = start ◂ zero ◂ zero
swapPath = start ◂ zero ◂ suc zero

-- the identity permutation's monomial is a*d = 2*7 = 14
mono-id : mono idPath M2 ≡ 14
mono-id = refl

-- the transposition's monomial is b*c = 3*5 = 15
mono-swap : mono swapPath M2 ≡ 15
mono-swap = refl
