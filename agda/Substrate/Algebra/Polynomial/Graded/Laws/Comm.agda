{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 9 (Comm) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Comm where
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
import Substrate.Algebra.Polynomial.Graded.Laws.Scalar as A4
import Substrate.Algebra.Polynomial.Graded.Laws.Basis as A5
import Substrate.Algebra.Polynomial.Graded.Laws.Linear as A6
import Substrate.Algebra.Polynomial.Graded.Laws.Monomial as A7
import Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta as A8
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
  -- 9. *P-comm via nested linear-extensionality, bottoming at convCoeff-basis-comm.
  --    `_*P q` and `subst ∘ (q *P_)` (same codomain via +ℕ-comm) as Linear maps, etc.
  Lq : ∀ {n m} (q : Poly m) → Linear n (n ℕ+ m)
  Lq q = record { apply = _*P q
                ; preserves-+  = λ u v → *P-distribʳ u v q
                ; preserves-·c = λ c v → *P-scalarˡ c v q }
  Mq : ∀ {n m} (q : Poly m) → Linear n (n ℕ+ m)
  Mq {n} {m} q = record
    { apply = λ p → subst Poly (+ℕ-comm m n) (q *P p)
    ; preserves-+  = λ u v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-distribˡ q u v))
                                   (subst-+P (+ℕ-comm m n) (q *P u) (q *P v))
    ; preserves-·c = λ c v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-scalarʳ c q v))
                                   (subst-·c (+ℕ-comm m n) c (q *P v)) }
  Li : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
  Li i = record { apply = λ q → basis i *P q
                ; preserves-+  = λ u v → *P-distribˡ (basis i) u v
                ; preserves-·c = λ c v → *P-scalarʳ c (basis i) v }
  Mi : ∀ {n m} (i : Fin n) → Linear m (n ℕ+ m)
  Mi {n} {m} i = record
    { apply = λ q → subst Poly (+ℕ-comm m n) (q *P basis i)
    ; preserves-+  = λ u v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-distribʳ u v (basis i)))
                                   (subst-+P (+ℕ-comm m n) (u *P basis i) (v *P basis i))
    ; preserves-·c = λ c v → trans (cong (subst Poly (+ℕ-comm m n)) (*P-scalarˡ c v (basis i)))
                                   (subst-·c (+ℕ-comm m n) c (v *P basis i)) }

  agree-i : ∀ {n m} (i : Fin n) (q : Poly m)
          → basis i *P q ≡ subst Poly (+ℕ-comm m n) (q *P basis i)
  agree-i {n} {m} i q = linear-extensionality (Li i) (Mi i) basis-pair q
    where
      basis-pair : (j : Fin m) → basis i *P basis j ≡ subst Poly (+ℕ-comm m n) (basis j *P basis i)
      basis-pair j = nth-ext _ _ (λ k →
        trans (nth-*P (basis i) (basis j) k)
        (trans (convCoeff-basis-comm i j k)
        (trans (sym (nth-*P (basis j) (basis i) k))
               (sym (nth-subst (+ℕ-comm m n) (basis j *P basis i) k)))))

  *P-comm : ∀ {n m} (p : Poly n) (q : Poly m) → p *P q ≡ subst Poly (+ℕ-comm m n) (q *P p)
  *P-comm p q = linear-extensionality (Lq q) (Mq q) (λ i → agree-i i q) p
