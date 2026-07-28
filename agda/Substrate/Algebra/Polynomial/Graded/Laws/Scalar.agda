{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 4 (Scalar) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Scalar where
open import Substrate.Foundation.Nat using (ℕ; zero; suc; _≟_) renaming (_+_ to _ℕ+_)
open import Substrate.Foundation.Nat.Properties.Add using () renaming (+-comm to +ℕ-comm; +-assoc to +ℕ-assoc)
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong; cong₂; subst)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Negation using (¬_; yes; no)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
open import Substrate.Algebra.Medial using (medial)
import Substrate.Algebra.Polynomial.Graded.Base as Base
import Substrate.Algebra.Polynomial.Graded.Defs as A0
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as A1
import Substrate.Algebra.Polynomial.Graded.Laws.Conv as A2
import Substrate.Algebra.Polynomial.Graded.Laws.Distrib as A3
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
  -- 5. Scalar-linearity (preserves-·c in each argument) + subst-linearity.
  swap-· : (a c x : A) → a * (c * x) ≡ c * (a * x)
  swap-· a c x = trans (sym (*-assoc a c x)) (trans (cong (_* x) (*-comm a c)) (*-assoc c a x))

  convCoeff-scalarˡ : (c : A) (p : Poly n) (q : Poly m) (k : ℕ)
                    → convCoeff (c ·c p) q k ≡ c * convCoeff p q k
  convCoeff-scalarˡ c []      q k       = sym (*-absorbʳ c)
  convCoeff-scalarˡ c (a ∷ p) q zero    = *-assoc c a (nth q zero)
  convCoeff-scalarˡ c (a ∷ p) q (suc k) =
    trans (cong₂ _+_ (*-assoc c a (nth q (suc k))) (convCoeff-scalarˡ c p q k))
          (sym (*-distribˡ c (a * nth q (suc k)) (convCoeff p q k)))

  *P-scalarˡ : (c : A) (p : Poly n) (q : Poly m) → (c ·c p) *P q ≡ c ·c (p *P q)
  *P-scalarˡ c p q = nth-ext _ _ (λ k →
    trans (nth-*P (c ·c p) q k)
    (trans (convCoeff-scalarˡ c p q k)
    (trans (cong (c *_) (sym (nth-*P p q k))) (sym (nth-·c c (p *P q) k)))))

  convCoeff-scalarʳ : (c : A) (p : Poly n) (q : Poly m) (k : ℕ)
                    → convCoeff p (c ·c q) k ≡ c * convCoeff p q k
  convCoeff-scalarʳ c []      q k       = sym (*-absorbʳ c)
  convCoeff-scalarʳ c (a ∷ p) q zero    =
    trans (cong (a *_) (nth-·c c q zero)) (swap-· a c (nth q zero))
  convCoeff-scalarʳ c (a ∷ p) q (suc k) =
    trans (cong₂ _+_ (trans (cong (a *_) (nth-·c c q (suc k))) (swap-· a c (nth q (suc k))))
                     (convCoeff-scalarʳ c p q k))
          (sym (*-distribˡ c (a * nth q (suc k)) (convCoeff p q k)))

  *P-scalarʳ : (c : A) (p : Poly n) (q : Poly m) → p *P (c ·c q) ≡ c ·c (p *P q)
  *P-scalarʳ c p q = nth-ext _ _ (λ k →
    trans (nth-*P p (c ·c q) k)
    (trans (convCoeff-scalarʳ c p q k)
    (trans (cong (c *_) (sym (nth-*P p q k))) (sym (nth-·c c (p *P q) k)))))

  subst-+P : ∀ {a b} (eq : a ≡ b) (u v : Poly a)
           → subst Poly eq (u +P v) ≡ (subst Poly eq u) +P (subst Poly eq v)
  subst-+P refl u v = refl
  subst-·c : ∀ {a b} (eq : a ≡ b) (c : A) (v : Poly a)
           → subst Poly eq (c ·c v) ≡ c ·c (subst Poly eq v)
  subst-·c refl c v = refl
