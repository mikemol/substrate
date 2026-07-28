{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 5 (Basis) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Basis where
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
open import Substrate.Algebra.Medial using (medial)
import Substrate.Algebra.Polynomial.Graded.Base as Base
import Substrate.Algebra.Polynomial.Graded.Defs as A0
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as A1
import Substrate.Algebra.Polynomial.Graded.Laws.Conv as A2
import Substrate.Algebra.Polynomial.Graded.Laws.Distrib as A3
import Substrate.Algebra.Polynomial.Graded.Laws.Scalar as A4
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
  -- ⟡graded-laws-noreexport: bind each ancestor DIRECTLY and NON-publicly. The `public`
  -- chain made every link's .agdai carry the whole accumulated API (Defs 52KB → AssocMono
  -- 145KB, ~10KB/link) — AssocLinearP/Q/R sit at 61-65KB purely because they dropped it.
  -- This link now re-exports only what it defines.
  open A0.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A1.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A2.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A3.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A4.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  -- 6. Basis machinery: canonical basis, Fin-indexed sums, basis-decomposition.
  basis : Fin n → Poly n
  basis {n} i = basis-vec {A} 𝟘 𝟙 {n} i

  -- the coefficient-level (A-valued) Fin sum, and its congruence / zero.
  sumA : (Fin n → A) → A
  sumA {zero}  _ = 𝟘
  sumA {suc _} g = g fzero + sumA (λ i → g (fsuc i))

  sumA-cong : {g h : Fin n → A} → (∀ i → g i ≡ h i) → sumA g ≡ sumA h
  sumA-cong {zero}  _  = refl
  sumA-cong {suc _} eq = cong₂ _+_ (eq fzero) (sumA-cong (λ i → eq (fsuc i)))

  sumA-zero : sumA {n} (λ _ → 𝟘) ≡ 𝟘
  sumA-zero {zero}   = refl
  sumA-zero {suc n'} = trans (cong (𝟘 +_) (sumA-zero {n'})) (+-identityˡ 𝟘)

  -- the polynomial-level Fin sum (fold +P), its congruence, and nth through it.
  sum : (Fin n → Poly m) → Poly m
  sum {zero}  {m} _ = replicate m 𝟘
  sum {suc _}     f = f fzero +P sum (λ i → f (fsuc i))

  sum-cong : {f g : Fin n → Poly m} → (∀ i → f i ≡ g i) → sum f ≡ sum g
  sum-cong {zero}  _  = refl
  sum-cong {suc _} eq = cong₂ _+P_ (eq fzero) (sum-cong (λ i → eq (fsuc i)))

  nth-sum : (f : Fin n → Poly m) (k : ℕ) → nth (sum f) k ≡ sumA (λ i → nth (f i) k)
  nth-sum {zero}  {m} f k = nth-replicate m k
  nth-sum {suc _}     f k =
    trans (nth-+P (f fzero) (sum (λ i → f (fsuc i))) k)
          (cong (nth (f fzero) k +_) (nth-sum (λ i → f (fsuc i)) k))

  -- basis i is the delta at toℕ i.
  nth-basis-same : (i : Fin n) → nth (basis i) (toℕ i) ≡ 𝟙
  nth-basis-same fzero     = refl
  nth-basis-same (fsuc i) = nth-basis-same i

  nth-basis-other : (i : Fin n) (k : ℕ) → ¬ (k ≡ toℕ i) → nth (basis i) k ≡ 𝟘
  nth-basis-other fzero       zero    neq = ⊥-elim (neq refl)
  nth-basis-other (fsuc i)   zero    _   = refl
  nth-basis-other {suc n'} fzero (suc k) _   = nth-replicate n' k
  nth-basis-other (fsuc i)   (suc k) neq = nth-basis-other i k (λ e → neq (cong suc e))

  -- the one-hot collapse: Σᵢ (nth v (toℕ i))·(δ_{toℕ i})_k ≡ nth v k.
  basis-collapse : (v : Poly n) (k : ℕ) → sumA (λ (i : Fin n) → (nth v (toℕ i)) * nth (basis i) k) ≡ nth v k
  basis-collapse []      k       = refl
  basis-collapse {suc n'} (x ∷ v) zero =
    trans (cong₂ _+_ (trans (*-comm x 𝟙) (*-identityˡ x))
                     (trans (sumA-cong {n'} (λ i → *-absorbʳ (nth v (toℕ i)))) (sumA-zero {n'})))
          (+-identityʳ x)
  basis-collapse {suc n'} (x ∷ v) (suc k) =
    trans (cong₂ _+_ (trans (cong (x *_) (nth-replicate n' k)) (*-absorbʳ x))
                     (basis-collapse v k))
          (+-identityˡ (nth v k))

  -- every polynomial IS the sum of its scaled basis vectors.
  basis-decomp : (v : Poly n) → v ≡ sum (λ (i : Fin n) → nth v (toℕ i) ·c basis i)
  basis-decomp {n} v = nth-ext v (sum f) (λ k →
    sym (trans (nth-sum f k)
        (trans (sumA-cong {n} (λ i → nth-·c (nth v (toℕ i)) (basis {n} i) k))
               (basis-collapse {n} v k))))
    where f : Fin n → Poly n
          f i = nth v (toℕ i) ·c basis {n} i
