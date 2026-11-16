{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: lifted out of *P-assoc's where-block (scoping reproduced by a
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.AssocMain where
open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
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
import Substrate.Algebra.Polynomial.Graded.Laws.Distrib as A3
import Substrate.Algebra.Polynomial.Graded.Laws.Scalar as A4
import Substrate.Algebra.Polynomial.Graded.Laws.Basis as A5
import Substrate.Algebra.Polynomial.Graded.Laws.Linear as A6
import Substrate.Algebra.Polynomial.Graded.Laws.Monomial as A7
import Substrate.Algebra.Polynomial.Graded.Laws.MonomialDelta as A8
import Substrate.Algebra.Polynomial.Graded.Laws.Comm as A9
import Substrate.Algebra.Polynomial.Graded.Laws.Assoc as A10
import Substrate.Algebra.Polynomial.Graded.Laws.AssocMono as A11
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearP as LP
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearQ as LQ
import Substrate.Algebra.Polynomial.Graded.Laws.AssocLinearR as LR
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
  -- ⟡graded-laws-noreexport: ancestors bound directly and NON-publicly.
  open A0.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  -- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
  -- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
  -- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
  -- through the root. Each leaf carries its OWN minimal telescope, so the
  -- argument lists differ by leaf and are read from each header.
  open import Substrate.Algebra.Polynomial.Graded.Defs.TimesP _+_ _*_ 𝟘 𝟙
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
  open A11.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open LP.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open LQ.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  open LR.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  module _ {n m l : ℕ} where
    private
      ae : (n ℕ+ m) ℕ+ l ≡ n ℕ+ (m ℕ+ l)
      -- ⚑ `+ℕ-assoc`, NOT the telescope's `+-assoc` over `A`.  `n`/`m`/`l` are ℕ.
      ae = +ℕ-assoc n m l
      S : Poly ((n ℕ+ m) ℕ+ l) → Poly (n ℕ+ (m ℕ+ l))
      S = subst Poly ae
    agq : (i : Fin n) (j : Fin m) (r : Poly l) → S ((basis i *P basis j) *P r) ≡ basis i *P (basis j *P r)
    agq i j r = linear-extensionality (Lr'' i j) (Rr'' i j) (λ k → mono-assoc i j k) r
    agp : (i : Fin n) (q : Poly m) (r : Poly l) → S ((basis i *P q) *P r) ≡ basis i *P (q *P r)
    agp i q r = linear-extensionality (Lq' i r) (Rq' i r) (λ j → agq i j r) q
    *P-assoc : (p : Poly n) (q : Poly m) (r : Poly l)
             → subst Poly (+ℕ-assoc n m l) ((p *P q) *P r) ≡ p *P (q *P r)
    *P-assoc p q r = linear-extensionality (Lp q r) (Rp q r) (λ i → agp i q r) p
