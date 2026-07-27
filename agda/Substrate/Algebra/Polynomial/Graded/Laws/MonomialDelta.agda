{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 8 (MonomialDelta) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta where
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
  nth-xpower-basis-peak : (d : ℕ) (j : Fin n) → nth (x-power d (basis j)) (d ℕ+ toℕ j) ≡ 𝟙
  nth-xpower-basis-peak d j = trans (nth-xpower-add d (basis j) (toℕ j)) (nth-basis-same j)

  nth-xpower-basis-off : (d : ℕ) (j : Fin n) (k : ℕ) → ¬ (k ≡ d ℕ+ toℕ j)
                       → nth (x-power d (basis j)) k ≡ 𝟘
  nth-xpower-basis-off zero    j k       neq = nth-basis-other j k neq
  nth-xpower-basis-off (suc d) j zero    _   = refl
  nth-xpower-basis-off (suc d) j (suc k) neq = nth-xpower-basis-off d j k (λ e → neq (cong suc e))

  -- the two monomials xⁱ·basis j and xʲ·basis i agree at every coefficient (both = δ at i+j).
  xpower-basis-symm : (i : Fin n) (j : Fin m) (k : ℕ)
                    → nth (x-power (toℕ i) (basis j)) k ≡ nth (x-power (toℕ j) (basis i)) k
  xpower-basis-symm i j k with k ≟ (toℕ i ℕ+ toℕ j)
  ... | yes eq = trans (subst (λ z → nth (x-power (toℕ i) (basis j)) z ≡ 𝟙) (sym eq)
                              (nth-xpower-basis-peak (toℕ i) j))
                       (sym (subst (λ z → nth (x-power (toℕ j) (basis i)) z ≡ 𝟙)
                              (sym (trans eq (+ℕ-comm (toℕ i) (toℕ j))))
                              (nth-xpower-basis-peak (toℕ j) i)))
  ... | no neq = trans (nth-xpower-basis-off (toℕ i) j k neq)
                       (sym (nth-xpower-basis-off (toℕ j) i k
                              (λ e → neq (trans e (+ℕ-comm (toℕ j) (toℕ i))))))

  -- basis-level commutativity of *P (coefficient form) — the bottom of *P-comm.
  convCoeff-basis-comm : (i : Fin n) (j : Fin m) (k : ℕ)
                       → convCoeff (basis i) (basis j) k ≡ convCoeff (basis j) (basis i) k
  convCoeff-basis-comm i j k =
    trans (convCoeff-basis-xpower i (basis j) k)
          (trans (xpower-basis-symm i j k) (sym (convCoeff-basis-xpower j (basis i) k)))

  -- multiplicative identity (graded / nth form): basis fz = the polynomial 1.
  *P-identityˡ-nth : ∀ {n m} (q : Poly m) (k : ℕ) → nth (basis {suc n} fz *P q) k ≡ nth q k
  *P-identityˡ-nth q k = trans (nth-*P (basis fz) q k) (convCoeff-basis-fz q k)
