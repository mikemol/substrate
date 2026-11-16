{-# OPTIONS --safe --without-K #-}
-- ⟡graded-shard: part 0 (Defs) of the graded-polynomial development, split out
-- so each module's elaboration peak stays under the 128MB cap. Re-exported by
-- `Substrate.Algebra.Polynomial.Graded` — the public API is unchanged.
module Substrate.Algebra.Polynomial.Graded.Defs where
-- ⚑ REPOINTED OFF THE DISSOLVED `Foundation.Nat` BARREL (⟡ban-decompose).  That
-- module provides NOTHING — `agda_defs --provides Substrate.Foundation.Nat` reports
-- 0 names over its 63 leaves — so the `using`/`renaming` above bound nothing and
-- `ℕ+` failed [NotInScope] at :51, blocking 85 modules.  The names live in
-- `Nat.Nat` (ℕ, zero, suc), `Nat.Plus` (_ℕ+_) and `Nat.Dec` (_≟_).
--
-- ⚑ AND THE RENAME IS NOT EARNED — a claim this comment used to make and which was
-- FALSE.  It argued the clash with `Over`'s carrier `_+_` made a `renaming` clause
-- unavoidable "because no split can separate a module parameter".  True about splits,
-- false about renames: naming ℕ's addition `_ℕ+_` AT SOURCE (`Nat.Plus`) stops the
-- import binding `_+_` at all, so the parameter binds it unambiguously and no filter
-- is needed.  The clause it defended is what let a tree-wide rename walk into this
-- telescope; the ban was right and the exemption was mine.
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Dec
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Vec using (Vec; []; _∷_; replicate)
-- ⚑ THREE MORE DISSOLVED BARRELS, SAME CLASS AS `Foundation.Nat` ABOVE.
-- `Foundation.Eq` survives but no longer exports sym/trans/cong/cong₂/subst (agda
-- warned -W[no]ModuleDoesntExport, which BINDS NOTHING and fails far away);
-- `Foundation.Negation` and `Foundation.Empty` have no source file at all.  Each
-- name is bound at the leaf that defines it, bare — no filter is earned here,
-- because these leaves export one or two names and nothing in scope clashes.
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Cong2
open import Substrate.Foundation.Eq.Subst
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Algebra.Module.Free.Basis using (basis-vec)
open import Substrate.Algebra.Medial using (medial)
import Substrate.Algebra.Polynomial.Graded.Base as Base
-- ⚑ THE CARRIER'S OPERATIONS AND LAWS, NOT ℕ's.  `rename_at_source` rewrote these
-- to `_ℕ+_`/`+ℕ-*` when it renamed `Nat.Plus._+_`, because THIS FILE carried a
-- `renaming (_+_ to _ℕ+_)` clause (added by hand earlier in the arc) that made
-- `_ℕ+_` look like the module's own spelling for the imported name.  A telescope
-- parameter is a BINDING, not a use site — the ℕ-domain suffix on it is a
-- category error: `A` is any carrier, and its addition is not ℕ's.
-- ⚑ ABOVE THE HEADER, NOT INSIDE THE TELESCOPE: a comment between `module Over
-- {A : Set}` and its first `(…)` group breaks the header span (`module_scopes`
-- masks comments to blanks) and `--telescope` reports the provider ABSENT.
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

  open import Substrate.Algebra.Polynomial.Graded.Defs.PlusP _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.C _+_ _*_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.XShift _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.PadEnd _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.ShiftToSucOnLeft _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.Outer _+_ _*_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.AntiDiagSum _+_ 𝟘 𝟙
  open import Substrate.Algebra.Polynomial.Graded.Defs.TimesP _+_ _*_ 𝟘 𝟙

  -- 1. The graded polynomial type and its operations (no laws needed).
  -- Poly / nth are single-sourced from the thin `Graded.Base` (a byte-table
  -- consumer deserialises just Base, not this whole ring tower).
  open Base.Over 𝟘 public using (Poly; nth)
