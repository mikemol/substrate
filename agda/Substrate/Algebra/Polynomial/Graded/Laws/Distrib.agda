{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 3 (Distrib) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Distrib where
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityL
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusSuc
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
open import Substrate.Algebra.Medial using (medial)
import Substrate.Algebra.Polynomial.Graded.Base as Base
import Substrate.Algebra.Polynomial.Graded.Defs as A0
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as A1
import Substrate.Algebra.Polynomial.Graded.Laws.Conv as A2
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
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
  -- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
  -- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
  -- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
  -- through the root. Each leaf carries its OWN minimal telescope, so the
  -- argument lists differ by leaf and are read from each header.
  open import Substrate.Algebra.Polynomial.Graded.Defs.PlusP _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.TimesP _+_ _*_ 𝟘 𝟙
  open A1.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open A2.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  -- 4. Bilinear distributivity (nth-ext + nth-*P + the per-coordinate identity).
  ·-distribʳ : (x y z : A) → (x + y) * z ≡ (x * z) + (y * z)
  ·-distribʳ x y z = trans (*-comm (x + y) z)
                     (trans (*-distribˡ z x y) (cong₂ _+_ (*-comm z x) (*-comm z y)))

  -- Ⓜ: the 4-term rearrange = the medial law (Algebra.Medial) at A's `+`.
  rearrange : (w x y z : A) → (w + x) + (y + z) ≡ (w + y) + (x + z)
  rearrange = medial _+_ +-assoc +-comm

  convCoeff-distrib : (p q : Poly n) (r : Poly m) (k : ℕ)
                    → convCoeff (p +P q) r k ≡ (convCoeff p r k) + (convCoeff q r k)
  convCoeff-distrib []      []      r k       = sym (+-identityˡ 𝟘)
  convCoeff-distrib (a ∷ p) (b ∷ q) r zero    = ·-distribʳ a b (nth r zero)
  convCoeff-distrib (a ∷ p) (b ∷ q) r (suc k) =
    trans (cong₂ _+_ (·-distribʳ a b (nth r (suc k))) (convCoeff-distrib p q r k))
          (rearrange (a * nth r (suc k)) (b * nth r (suc k)) (convCoeff p r k) (convCoeff q r k))

  *P-distribʳ : (p q : Poly n) (r : Poly m) → (p +P q) *P r ≡ (p *P r) +P (q *P r)
  *P-distribʳ p q r = nth-ext _ _ (λ k →
    trans (nth-*P (p +P q) r k)
    (trans (convCoeff-distrib p q r k)
    (trans (cong₂ _+_ (sym (nth-*P p r k)) (sym (nth-*P q r k)))
           (sym (nth-+P (p *P r) (q *P r) k)))))

  convCoeff-distribˡ : (r : Poly n) (p q : Poly m) (k : ℕ)
                     → convCoeff r (p +P q) k ≡ (convCoeff r p k) + (convCoeff r q k)
  convCoeff-distribˡ []      p q k       = sym (+-identityˡ 𝟘)
  -- ⚑ `a *_`, NOT `a *P_`: `a : A` is a CARRIER SCALAR, and `_*P_` is polynomial
  -- multiplication (`Poly n → Poly m → Poly (n + m)`), so `a *P_` demanded
  -- `a : Poly _` and failed [UnequalTerms] `A !=< Vec A _n`.  The very next
  -- argument (`*-distribˡ a (nth p zero) …`) is the CARRIER distributivity law
  -- over `_*_`, and the parallel clause at :58 uses `·-distribʳ` at `A` — both
  -- witness that this coordinate is scalar, not polynomial.
  convCoeff-distribˡ (a ∷ r) p q zero    =
    trans (cong (a *_) (nth-+P p q zero)) (*-distribˡ a (nth p zero) (nth q zero))
  convCoeff-distribˡ (a ∷ r) p q (suc k) =
    trans (cong₂ _+_ (trans (cong (a *_) (nth-+P p q (suc k)))
                            (*-distribˡ a (nth p (suc k)) (nth q (suc k))))
                     (convCoeff-distribˡ r p q k))
          (rearrange (a * nth p (suc k)) (a * nth q (suc k)) (convCoeff r p k) (convCoeff r q k))

  *P-distribˡ : (r : Poly n) (p q : Poly m) → r *P (p +P q) ≡ (r *P p) +P (r *P q)
  *P-distribˡ r p q = nth-ext _ _ (λ k →
    trans (nth-*P r (p +P q) k)
    (trans (convCoeff-distribˡ r p q k)
    (trans (cong₂ _+_ (sym (nth-*P r p k)) (sym (nth-*P r q k)))
           (sym (nth-+P (r *P p) (r *P q) k)))))
