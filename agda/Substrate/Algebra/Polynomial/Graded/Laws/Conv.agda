{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 2 (Conv) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Conv where
open import Substrate.Foundation.Nat.Nat
-- ⚑ BARE — the ℕ names now carry their domain AT SOURCE (`Nat.Plus._ℕ+_`,
-- `Add.PlusComm.+ℕ-comm`), so no consumer-side filter is earned.  The clauses these
-- lines replace were self-renames (a clause renaming a name to itself) left behind when the
-- tree-wide rename rewrote both sides of a hand-added filter that should never have
-- been written.  The carrier's `_+_`/`+-comm` are the telescope's, below.
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
import Substrate.Algebra.Polynomial.Graded.Base as Base
import Substrate.Algebra.Polynomial.Graded.Defs as A0
import Substrate.Algebra.Polynomial.Graded.Laws.Nth as A1
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
-- ⚑ CARRIER NAMES, BARE — restored from 771283c8 via `agda_defs --at … --diff`.
-- A tree-wide `rename_at_source` on ℕ's `_+_`/`+-comm` walked into this telescope
-- because the file carried a hand-added `renaming (_+_ to _ℕ+_)`, which made `_ℕ+_`
-- look like this module's spelling for the imported name.  `A` is an ARBITRARY
-- carrier: a ℕ-domain suffix on its addition is a category error, and 13 sibling
-- shards pass a carrier operation into slot 0 regardless of what it is named here.
-- ⚑ AND THIS COMMENT SITS ABOVE THE HEADER, NOT INSIDE THE TELESCOPE: a comment
-- between `module Over {A : Set}` and its first `(…)` group breaks the header span
-- (`agda_lex.module_scopes` masks comments to blanks), and `--telescope` then reports
-- the provider as ABSENT — measured, one edit ago, on this very file.
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
  -- ⟡graded-laws-noreexport: bind each ancestor DIRECTLY and NON-publicly.
  -- The `public` chain made every link's .agdai carry the whole accumulated API
  -- (Defs 52KB → AssocMono 145KB, ~10KB/link); AssocLinearP/Q/R sit at 61-65KB
  -- purely because they dropped it. This link now re-exports only what it defines.
  open A0.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  -- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
  -- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
  -- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
  -- through the root. Each leaf carries its OWN minimal telescope, so the
  -- argument lists differ by leaf and are read from each header.
  open import Substrate.Algebra.Polynomial.Graded.Defs.C _+_ _*_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.PadEnd _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.ShiftToSucOnLeft _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.TimesP _+_ _*_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.XShift _+_ 𝟘 𝟙
  open A1.Over _+_ _*_ 𝟘 𝟙 +-assoc +-comm +-identityˡ +-identityʳ *-assoc *-comm *-identityˡ *-distribˡ *-absorbˡ *-absorbʳ
  -- 3. The convolution coefficient and the bridge `nth-*P` (the method).
  convCoeff : Poly n → Poly m → ℕ → A
  convCoeff []      q k       = 𝟘
  convCoeff (a ∷ p) q zero    = a * nth q zero
  convCoeff (a ∷ p) q (suc k) = (a * nth q (suc k)) + convCoeff p q k

  nth-*P : (p : Poly n) (q : Poly m) (k : ℕ) → nth (p *P q) k ≡ convCoeff p q k
  nth-*P {n = zero}  {m = m} []      q k       = nth-replicate m k
  nth-*P {n = suc n} {m = m} (a ∷ p) q zero    =
    trans (nth-+P lo hi zero)
          (trans (cong₂ _+_
                    (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) zero)
                           (trans (nth-pad-end (suc n) (a ·c q) zero) (nth-·c a q zero)))
                    (nth-x-shift-zero (p *P q)))
                 (+-identityʳ (a * nth q zero)))
    where
      lo : Poly (suc n ℕ+ m)
      lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
      hi : Poly (suc n ℕ+ m)
      hi = x-shift (p *P q)
  nth-*P {n = suc n} {m = m} (a ∷ p) q (suc k) =
    trans (nth-+P lo hi (suc k))
          (cong₂ _+_
             (trans (nth-subst (+ℕ-comm m (suc n)) (pad-end (suc n) (a ·c q)) (suc k))
                    (trans (nth-pad-end (suc n) (a ·c q) (suc k)) (nth-·c a q (suc k))))
             (trans (nth-x-shift-suc (p *P q) k) (nth-*P p q k)))
    where
      lo : Poly (suc n ℕ+ m)
      lo = shift-to-suc-on-left (pad-end (suc n) (a ·c q))
      hi : Poly (suc n ℕ+ m)
      hi = x-shift (p *P q)

  nth-ext : (u v : Poly n) → (∀ k → nth u k ≡ nth v k) → u ≡ v
  nth-ext []      []      _  = refl
  nth-ext (x ∷ u) (y ∷ v) eq = cong₂ _∷_ (eq zero) (nth-ext u v (λ k → eq (suc k)))
