{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 6 (Linear) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Linear where
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
  -- 7. The Linear record + linear-extensionality (the multilinear-extension bit
  --    that comm/assoc consume): two linear maps agreeing on the basis are equal.
  record Linear (d e : ℕ) : Set where
    field
      apply        : Poly d → Poly e
      preserves-+  : (u v : Poly d) → apply (u +P v) ≡ apply u +P apply v
      preserves-·c : (c : A) (v : Poly d) → apply (c ·c v) ≡ c ·c apply v
  open Linear public

  ·c-absorbˡ : (v : Poly n) → 𝟘 ·c v ≡ replicate n 𝟘
  ·c-absorbˡ []      = refl
  ·c-absorbˡ (x ∷ v) = cong₂ _∷_ (*-absorbˡ x) (·c-absorbˡ v)

  preserves-𝟎P : (L : Linear n m) → apply L (replicate n 𝟘) ≡ replicate m 𝟘
  preserves-𝟎P {n} L =
    trans (cong (apply L) (sym (·c-absorbˡ (replicate n 𝟘))))
          (trans (preserves-·c L 𝟘 (replicate n 𝟘))
                 (·c-absorbˡ (apply L (replicate n 𝟘))))

  preserves-sum : (L : Linear n m) (f : Fin k → Poly n)
                → apply L (sum f) ≡ sum (λ i → apply L (f i))
  preserves-sum {k = zero}  L f = preserves-𝟎P L
  preserves-sum {k = suc _} L f =
    trans (preserves-+ L (f fzero) (sum (λ i → f (fsuc i))))
          (cong (apply L (f fzero) +P_) (preserves-sum L (λ i → f (fsuc i))))

  linear-extensionality : (L M : Linear n m)
    → ((i : Fin n) → apply L (basis i) ≡ apply M (basis i))
    → (v : Poly n) → apply L v ≡ apply M v
  linear-extensionality {n} L M agree v =
    trans (cong (apply L) (basis-decomp v))
    (trans (preserves-sum L (λ (i : Fin n) → nth v (toℕ i) ·c basis i))
    (trans (sum-cong (λ (i : Fin n) → preserves-·c L (nth v (toℕ i)) (basis i)))
    (trans (sum-cong (λ (i : Fin n) → cong (nth v (toℕ i) ·c_) (agree i)))
    (trans (sum-cong (λ (i : Fin n) → sym (preserves-·c M (nth v (toℕ i)) (basis i))))
    (trans (sym (preserves-sum M (λ (i : Fin n) → nth v (toℕ i) ·c basis i)))
           (cong (apply M) (sym (basis-decomp v))))))))
