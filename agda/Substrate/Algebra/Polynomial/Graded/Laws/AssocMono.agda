{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 11 (AssocMono) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.AssocMono where
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
import Substrate.Algebra.Polynomial.Graded.Defs as A0
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as A1
import Substrate.Algebra.Polynomial.Graded.Laws.Conv as A2
import Substrate.Algebra.Polynomial.Graded.Laws.Distrib as A3
import Substrate.Algebra.Polynomial.Graded.Laws.Scalar as A4
import Substrate.Algebra.Polynomial.Graded.Laws.Basis as A5
import Substrate.Algebra.Polynomial.Graded.Laws.Linear as A6
import Substrate.Algebra.Polynomial.Graded.Laws.Monomial as A7
import Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta as A8
import Substrate.Algebra.Polynomial.Graded.Laws.Comm as A9
import Substrate.Algebra.Polynomial.Graded.Laws.Assoc as A10
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
  open A5.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A6.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A7.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A8.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A9.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A10.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  mono-assoc : ∀ {n m l} (i : Fin n) (j : Fin m) (k : Fin l)
             → subst Poly (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k)
               ≡ basis i *P (basis j *P basis k)
  mono-assoc {n} {m} {l} i j k = nth-ext _ _ (λ d →
    trans (nth-subst (+ℕ-assoc n m l) ((basis i *P basis j) *P basis k) d) (coeff d))
    where
      P : ℕ
      P = toℕ i ℕ+ (toℕ j ℕ+ toℕ k)
      rk : toℕ k ℕ+ (toℕ i ℕ+ toℕ j) ≡ P
      rk = trans (+ℕ-comm (toℕ k) (toℕ i ℕ+ toℕ j)) (+ℕ-assoc (toℕ i) (toℕ j) (toℕ k))
      lhsV : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                     ≡ nth (x-power (toℕ k) (basis i *P basis j)) d
      lhsV d = trans (nth-*P (basis i *P basis j) (basis k) d)
                     (convCoeff-basis-right (basis i *P basis j) k d)
      rhsV : (d : ℕ) → nth (basis i *P (basis j *P basis k)) d
                     ≡ nth (x-power (toℕ i) (basis j *P basis k)) d
      rhsV d = trans (nth-*P (basis i) (basis j *P basis k) d)
                     (convCoeff-basis-xpower i (basis j *P basis k) d)
      ijV : (b : ℕ) → nth (basis i *P basis j) b ≡ nth (x-power (toℕ i) (basis j)) b
      ijV b = trans (nth-*P (basis i) (basis j) b) (convCoeff-basis-xpower i (basis j) b)
      jkV : (b : ℕ) → nth (basis j *P basis k) b ≡ nth (x-power (toℕ j) (basis k)) b
      jkV b = trans (nth-*P (basis j) (basis k) b) (convCoeff-basis-xpower j (basis k) b)
      coeff : (d : ℕ) → nth ((basis i *P basis j) *P basis k) d
                      ≡ nth (basis i *P (basis j *P basis k)) d
      coeff d with d ≟ P
      ... | yes eq = trans lhs𝟙 (sym rhs𝟙)
        where
          rhs𝟙 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟙
          rhs𝟙 = subst (λ z → nth (basis i *P (basis j *P basis k)) z ≡ 𝟙) (sym eq)
                   (trans (rhsV P)
                    (trans (nth-xpower-add (toℕ i) (basis j *P basis k) (toℕ j ℕ+ toℕ k))
                     (trans (jkV (toℕ j ℕ+ toℕ k)) (nth-xpower-basis-peak (toℕ j) k))))
          lhs𝟙 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟙
          lhs𝟙 = subst (λ z → nth ((basis i *P basis j) *P basis k) z ≡ 𝟙) (sym eq)
                   (trans (lhsV P)
                    (subst (λ z → nth (x-power (toℕ k) (basis i *P basis j)) z ≡ 𝟙) rk
                      (trans (nth-xpower-add (toℕ k) (basis i *P basis j) (toℕ i ℕ+ toℕ j))
                       (trans (ijV (toℕ i ℕ+ toℕ j)) (nth-xpower-basis-peak (toℕ i) j)))))
      ... | no neq = trans lhs𝟘 (sym rhs𝟘)
        where
          rhs𝟘 : nth (basis i *P (basis j *P basis k)) d ≡ 𝟘
          rhs𝟘 = trans (rhsV d)
                   (nth-xpower-off (toℕ i) (basis j *P basis k) d
                     (λ b e → trans (jkV b)
                       (nth-xpower-basis-off (toℕ j) k b
                         (λ b-eq → neq (trans e (cong (toℕ i ℕ+_) b-eq))))))
          lhs𝟘 : nth ((basis i *P basis j) *P basis k) d ≡ 𝟘
          lhs𝟘 = trans (lhsV d)
                   (nth-xpower-off (toℕ k) (basis i *P basis j) d
                     (λ b e → trans (ijV b)
                       (nth-xpower-basis-off (toℕ i) j b
                         (λ b-eq → neq (trans (trans e (cong (toℕ k ℕ+_) b-eq)) rk)))))
