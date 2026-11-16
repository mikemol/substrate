{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 1 (Nth) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Laws.Nth where
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
import Substrate.Algebra.Polynomial.Graded.Base as Base
import Substrate.Algebra.Polynomial.Graded.Defs as A0
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
-- ⚑ `_+_`/`_*_`, NOT `_+P_`/`_*P_`.  The telescope bound the P-spelling while every
-- law below states itself in the BARE one, and the `open A0.Over _+_ _*_ …` applies
-- the bare spelling — so the P names bound nothing any consumer referenced and `+`
-- failed [NotInScope].  `Defs`, the module this one is a shard of, binds bare.
-- ⚑ AND THE LAW NAMES ARE CARRIER LAWS: `+ℕ-assoc` here was a tree-wide
-- `rename_at_source` walking into the telescope.  `A` is an arbitrary carrier; a
-- ℕ-domain suffix on its laws is a category error.
-- ⚑ THIS COMMENT SITS ABOVE THE HEADER.  Between `module Over {A : Set}` and its
-- first `(…)` group it breaks the header span (`module_scopes` masks comments to
-- blanks) and `--telescope` reports the provider ABSENT — measured on THIS file,
-- which sat invisible to the census for an hour after being annotated in place.
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
  open import Substrate.Algebra.Polynomial.Graded.Defs.PlusP _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.XShift _+_ 𝟘 𝟙
  -- 2. Coefficient extraction `nth` (from Base above) and its homomorphism lemmas.
  nth-replicate : (k i : ℕ) → nth (replicate k 𝟘) i ≡ 𝟘
  nth-replicate zero    _       = refl
  nth-replicate (suc _) zero    = refl
  nth-replicate (suc k) (suc i) = nth-replicate k i

  nth-subst : ∀ {a b} (eq : a ≡ b) (v : Poly a) (i : ℕ)
            → nth (subst Poly eq v) i ≡ nth v i
  nth-subst refl v i = refl

  nth-pad-end : (k : ℕ) (v : Poly n) (i : ℕ) → nth (pad-end k v) i ≡ nth v i
  nth-pad-end k []      i       = nth-replicate k i
  nth-pad-end k (x ∷ v) zero    = refl
  nth-pad-end k (x ∷ v) (suc i) = nth-pad-end k v i

  nth-x-shift-zero : (v : Poly n) → nth (x-shift v) zero ≡ 𝟘
  nth-x-shift-zero v = refl
  nth-x-shift-suc : (v : Poly n) (i : ℕ) → nth (x-shift v) (suc i) ≡ nth v i
  nth-x-shift-suc v i = refl

  nth-+P : (u v : Poly n) (i : ℕ) → nth (u +P v) i ≡ nth u i + nth v i
  nth-+P []      []      i       = sym (+-identityˡ 𝟘)
  nth-+P (x ∷ u) (y ∷ v) zero    = refl
  nth-+P (x ∷ u) (y ∷ v) (suc i) = nth-+P u v i

  nth-·c : (a : A) (v : Poly n) (i : ℕ) → nth (a ·c v) i ≡ a * nth v i
  nth-·c a []      i       = sym (*-absorbʳ a)
  nth-·c a (x ∷ v) zero    = refl
  nth-·c a (x ∷ v) (suc i) = nth-·c a v i
