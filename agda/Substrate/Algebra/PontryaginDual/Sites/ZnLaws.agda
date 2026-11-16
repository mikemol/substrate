------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.ZnLaws
--
-- THE LAW WITNESSES `Sites/Zn` DEFERRED — ℤ/(suc n) as a proved AbelianGroup.
--
-- `Sites/Zn.agda:47-51` records the gap precisely: *"there is no group-law
-- field on PontryaginDual, so these definitions are not yet *proved* to
-- satisfy the abelian-group axioms here; they are the correct operations as
-- DATA.  A follow-on slice can add the law witnesses (assoc / id / inv via the
-- Mod arithmetic lemmas)."*  This is that slice.  All six obligations —
-- assoc, ε-left, ε-right, inv-left, inv-right, comm — land on the EXISTING
-- `add-mod` / `neg-mod` / `zero`, which are not redefined here.
--
-- ⚑ WHY THIS COULD NOT BE WRITTEN BEFORE `mod-cancel`, AND WHY IT NO LONGER
-- NEEDS IT.  The deferral outlived its cause.  `Algebra.Nat.Mod` was
-- congruence and reduction laws only, so the CYCLIC TORSOR's `fix→unit`
-- (`Wedge/ResidueAtom/Cyclic`) had nothing to reduce to and `Mod.Cancel` was
-- built for it.  The GROUP laws turn out not to need cancellation at all —
-- they need `mod-+-left`/`mod-+-right` to push the reduction around, which
-- existed the whole time.  Both deferrals were logged together and read as one
-- blocker; only one of them actually was.
--
-- ⚑ THE WHOLE FILE IS ONE MOVE APPLIED SIX TIMES: transport to ℕ, work there,
-- transport back.  `toℕ-injective` reduces every Fin-equation to a ℕ-equation;
-- `toℕ-add-mod` (proved in `Wedge/ResidueAtom/Cyclic`, imported not repeated)
-- reads `add-mod` as a `mod-suc`; the ℕ-level fact is then one of the standard
-- Mod homomorphism lemmas.  No law below does arithmetic of its own.
--
-- ⚑ AND `neg-mod` IS NOT `Z.Residue.negmod`, DESPITE THE NAME AND THE SHAPE.
--   negmod x m = (suc m ∸ (x mod-suc m)) mod-suc m      -- Z.Residue:38
--   neg-mod n a = fromℕ< (mod-suc-bound (suc n ∸ toℕ a) n)
-- The first reduces its ARGUMENT before subtracting; the second does not.
-- They agree only because `toℕ a < suc n` already, so `toℕ a mod-suc n ≡
-- toℕ a` — which is `mod-suc-id`, proved, not assumed.  `negmod-inverse` is
-- therefore NOT directly reusable as `inv-left`: it is the same theorem about
-- a different function.  Reaching for it would have been a name-match, not a
-- reuse.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.ZnLaws where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Order using (<→≤)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.From2
open import Substrate.Foundation.Fin.Properties
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism
open import Substrate.Algebra.PontryaginDual.Sites.Zn
open import Substrate.Algebra.Wedge.ResidueAtom.Cyclic using (toℕ-add-mod)
open import Substrate.Algebra.Magma
open import Substrate.Algebra.Semigroup
open import Substrate.Algebra.Monoid
open import Substrate.Algebra.Group
open import Substrate.Algebra.AbelianGroup
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. The transport.
--
-- Every element of `Fin (suc n)` is already below the modulus, so reducing it
-- is the identity.  This is the fact that makes all six laws mechanical: it
-- lets a `toℕ` of a Fin be introduced into, or erased from, a `mod-suc`
-- position at will.
------------------------------------------------------------------------

toℕ-mod-id : (n : ℕ) (a : Fin (suc n)) → toℕ a mod-suc n ≡ toℕ a
toℕ-mod-id n a = mod-suc-id (toℕ a) n (toℕ-bound a)

-- `neg-mod` read through `toℕ`, the companion of `toℕ-add-mod`.
toℕ-neg-mod : (n : ℕ) (a : Fin (suc n)) →
              toℕ (neg-mod n a) ≡ (suc n ∸ toℕ a) mod-suc n
toℕ-neg-mod n a = toℕ-fromℕ< (mod-suc-bound (suc n ∸ toℕ a) n)

------------------------------------------------------------------------
-- 2. Associativity.
--
-- Both sides reduce to `(toℕ a ℕ+ toℕ b ℕ+ toℕ c) mod-suc n`; the two
-- bracketings differ only in WHICH summand carries an inner reduction, which
-- `mod-+-left` / `mod-+-right` erase.
------------------------------------------------------------------------

add-mod-assoc : (n : ℕ) (a b c : Fin (suc n)) →
                add-mod n (add-mod n a b) c ≡ add-mod n a (add-mod n b c)
add-mod-assoc n a b c = toℕ-injective
  (trans (toℕ-add-mod n (add-mod n a b) c)
  (trans (cong (λ k → (k ℕ+ toℕ c) mod-suc n) (toℕ-add-mod n a b))
  (trans (mod-+-left (toℕ a ℕ+ toℕ b) (toℕ c) n)
  (trans (cong (_mod-suc n) (+ℕ-assoc (toℕ a) (toℕ b) (toℕ c)))
  (trans (sym (mod-+-right (toℕ a) (toℕ b ℕ+ toℕ c) n))
  (trans (cong (λ k → (toℕ a ℕ+ k) mod-suc n) (sym (toℕ-add-mod n b c)))
         (sym (toℕ-add-mod n a (add-mod n b c)))))))))

------------------------------------------------------------------------
-- 3. Identity.
--
-- `toℕ (zero {n})` is `0` definitionally, so ε-left is `0 ℕ+ x` reducing on
-- its first argument and ε-right is `+ℕ-identityʳ`.  Both then need only
-- `toℕ-mod-id` to erase the outer reduction.
------------------------------------------------------------------------

add-mod-ε-left : (n : ℕ) (a : Fin (suc n)) → add-mod n zero a ≡ a
add-mod-ε-left n a = toℕ-injective
  (trans (toℕ-add-mod n zero a) (toℕ-mod-id n a))

add-mod-ε-right : (n : ℕ) (a : Fin (suc n)) → add-mod n a zero ≡ a
add-mod-ε-right n a = toℕ-injective
  (trans (toℕ-add-mod n a zero)
  (trans (cong (_mod-suc n) (+ℕ-identityʳ (toℕ a))) (toℕ-mod-id n a)))

------------------------------------------------------------------------
-- 4. Inverses.
--
-- `(suc n ∸ toℕ a) ℕ+ toℕ a ≡ suc n` by `∸-+-id` (the bound `toℕ a ≤ suc n`
-- comes from `toℕ-bound`), and `suc-mod-suc-self` sends `suc n` to `0`.  The
-- inner reduction on the left summand is erased by `mod-+-left` first.
------------------------------------------------------------------------

add-mod-inv-left : (n : ℕ) (a : Fin (suc n)) →
                   add-mod n (neg-mod n a) a ≡ zero
add-mod-inv-left n a = toℕ-injective
  (trans (toℕ-add-mod n (neg-mod n a) a)
  (trans (cong (λ k → (k ℕ+ toℕ a) mod-suc n) (toℕ-neg-mod n a))
  (trans (mod-+-left (suc n ∸ toℕ a) (toℕ a) n)
  (trans (cong (_mod-suc n) (∸-+-id (suc n) (toℕ a) (<→≤ (toℕ-bound a))))
         (suc-mod-suc-self n)))))

add-mod-inv-right : (n : ℕ) (a : Fin (suc n)) →
                    add-mod n a (neg-mod n a) ≡ zero
add-mod-inv-right n a = toℕ-injective
  (trans (toℕ-add-mod n a (neg-mod n a))
  (trans (cong (_mod-suc n) (+ℕ-comm (toℕ a) (toℕ (neg-mod n a))))
  (trans (sym (toℕ-add-mod n (neg-mod n a) a))
         (cong toℕ (add-mod-inv-left n a)))))

------------------------------------------------------------------------
-- 5. Commutativity — `+ℕ-comm` under the reduction.
------------------------------------------------------------------------

add-mod-comm : (n : ℕ) (a b : Fin (suc n)) →
               add-mod n a b ≡ add-mod n b a
add-mod-comm n a b = toℕ-injective
  (trans (toℕ-add-mod n a b)
  (trans (cong (_mod-suc n) (+ℕ-comm (toℕ a) (toℕ b)))
         (sym (toℕ-add-mod n b a))))

------------------------------------------------------------------------
-- 6. The ladder instances.
--
-- M1 → M5 on the carrier `Fin (suc n)`, each rung built from the one below.
-- `ℤ/n-as-Self-Dual`'s three operations are now backed by proofs rather than
-- carried as data.
------------------------------------------------------------------------

Zn-Magma : (n : ℕ) → Magma (Fin (suc n))
Zn-Magma n = record { _·_ = add-mod n }

Zn-Semigroup : (n : ℕ) → Semigroup (Fin (suc n))
Zn-Semigroup n = record
  { magma   = Zn-Magma n
  ; ·-assoc = add-mod-assoc n
  }

Zn-Monoid : (n : ℕ) → Monoid (Fin (suc n))
Zn-Monoid n = record
  { semigroup = Zn-Semigroup n
  ; ε         = zero
  ; ε-left    = add-mod-ε-left n
  ; ε-right   = add-mod-ε-right n
  }

Zn-Group : (n : ℕ) → Group (Fin (suc n))
Zn-Group n = record
  { monoid    = Zn-Monoid n
  ; inv       = neg-mod n
  ; inv-left  = add-mod-inv-left n
  ; inv-right = add-mod-inv-right n
  }

Zn-AbelianGroup : (n : ℕ) → AbelianGroup (Fin (suc n))
Zn-AbelianGroup n = record
  { group  = Zn-Group n
  ; ·-comm = add-mod-comm n
  }
