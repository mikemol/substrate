{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 0 (Defs) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Defs where
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Fin using (Fin; toℕ) renaming (zero to fz; suc to fs)
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
open import Substrate.Algebra.Medial using (medial)
import Substrate.Algebra.Polynomial.Graded.Base as Base
module Over {A : Set}
  (_+_ : A → A → A) (_*_ : A → A → A) (𝟘 𝟙 : A)
  (+-assoc     : (a b c : A) → (a + b) + c ≡ a + (b + c))
  (+-comm      : (a b : A) → a + b ≡ b + a)
  (+-identityˡ : (a : A) → 𝟘 + a ≡ a)
  (+-identityʳ : (a : A) → a + 𝟘 ≡ a)
  (*-assoc     : (a b c : A) → (a * b) * c ≡ a * (b * c))
  (*-comm      : (a b : A) → a * b ≡ b * a)
  (*-identityˡ : (a : A) → 𝟙 * a ≡ a)
  (*-distribˡ  : (a b c : A) → a * (b + c) ≡ (a * b) + (a * c))
  (*-absorbˡ   : (a : A) → 𝟘 * a ≡ 𝟘)
  (*-absorbʳ   : (a : A) → a * 𝟘 ≡ 𝟘)
  where

  private variable n m k : ℕ

  -- 1. The graded polynomial type and its operations (no laws needed).
  -- Poly / nth are single-sourced from the thin `Graded.Base` (a byte-table
  -- consumer deserialises just Base, not this whole ring tower).
  open Base.Over 𝟘 public using (Poly; nth)

  infixl 6 _+P_
  _+P_ : Poly n → Poly n → Poly n
  []      +P []      = []
  (x ∷ u) +P (y ∷ v) = (x + y) ∷ (u +P v)

  infixl 7 _·c_
  _·c_ : A → Poly n → Poly n
  a ·c []      = []
  a ·c (x ∷ p) = (a * x) ∷ (a ·c p)

  x-shift : Poly n → Poly (suc n)
  x-shift p = 𝟘 ∷ p

  pad-end : (k : ℕ) → Poly n → Poly (n ℕ+ k)
  pad-end k []      = replicate k 𝟘
  pad-end k (x ∷ p) = x ∷ pad-end k p

  shift-to-suc-on-left : ∀ {n'} → Poly (m ℕ+ suc n') → Poly (suc n' ℕ+ m)
  shift-to-suc-on-left {m} {n'} p = subst Poly (+ℕ-comm m (suc n')) p

  outer : Poly n → Poly m → Vec (Poly m) n
  outer []      q = []
  outer (a ∷ p) q = (a ·c q) ∷ outer p q

  anti-diag-sum : Vec (Poly m) n → Poly (n ℕ+ m)
  anti-diag-sum {m} {zero}   []           = replicate m 𝟘
  anti-diag-sum {m} {suc n'} (row ∷ rows) =
    shift-to-suc-on-left (pad-end (suc n') row) +P x-shift (anti-diag-sum rows)

  infixl 7 _*P_
  _*P_ : Poly n → Poly m → Poly (n ℕ+ m)
  p *P q = anti-diag-sum (outer p q)
