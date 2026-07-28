{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 10 (Assoc) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Assoc where
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
import Substrate.Algebra.Polynomial.Graded.Laws.Basis as A5
import Substrate.Algebra.Polynomial.Graded.Laws.Linear as A6
import Substrate.Algebra.Polynomial.Graded.Laws.Monomial as A7
import Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta as A8
import Substrate.Algebra.Polynomial.Graded.Laws.Comm as A9
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
  -- 10. *P-assoc via 3× nested linear-extensionality, bottoming at mono-assoc (all-basis).
  convCoeff-comm : ∀ {n m} (p : Poly n) (q : Poly m) (d : ℕ) → convCoeff p q d ≡ convCoeff q p d
  convCoeff-comm {n} {m} p q d =
    trans (sym (nth-*P p q d))
    (trans (cong (λ z → nth z d) (*P-comm p q))
    (trans (nth-subst (+ℕ-comm m n) (q *P p) d) (nth-*P q p d)))

  convCoeff-basis-right : ∀ {n m} (p : Poly n) (k : Fin m) (d : ℕ)
                        → convCoeff p (basis k) d ≡ nth (x-power (toℕ k) p) d
  convCoeff-basis-right p k d = trans (convCoeff-comm p (basis k) d) (convCoeff-basis-xpower k p d)

  nth-xpower-off : ∀ a {m} (q : Poly m) (d : ℕ)
                 → (∀ b → d ≡ a ℕ+ b → nth q b ≡ 𝟘) → nth (x-power a q) d ≡ 𝟘
  nth-xpower-off zero    q d       h = h d refl
  nth-xpower-off (suc a) q zero    _ = refl
  nth-xpower-off (suc a) q (suc d) h = nth-xpower-off a q d (λ b e → h b (cong suc e))
