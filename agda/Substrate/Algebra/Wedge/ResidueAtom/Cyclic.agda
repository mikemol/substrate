------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.ResidueAtom.Cyclic
--
-- ℤ/(suc n) AS A TORSOR ATOM — the carrier Ⓒ3′ declined, now reachable.
--
-- ⚑ THIS WAS THE EXPENSIVE CARRIER, AND THE COST WAS ONE MISSING LEMMA.
-- Every carrier packaged before it had cancellation for free: ℕ and ℤ by the
-- group/monoid laws, `List` by a length argument, F₂ definitionally.  The
-- cyclic one had none — `Algebra.Nat.Mod` was congruence and reduction laws
-- only, so `add-mod n g x ≡ x → g ≡ zero` had nothing to reduce to.  That gap
-- is now `Algebra.Nat.Mod.Cancel.mod-cancel`, and this module is three lines
-- of plumbing on top of it.
--
-- ⚑ THE OPERATION ALREADY EXISTED AND IS NOT REDEFINED HERE.
-- `PontryaginDual.Sites.Zn.add-mod` is cyclic addition on `Fin (suc n)`, and
-- `Algebra/Fin/Wedge.agda:16` already names it as THE choice of cyclic
-- carrier.  Writing a second `_+Fin_` beside it would have been the
-- reinvention the reuse-search exists to catch — the operation is imported,
-- and only the LAW is new.
--
-- ⚑ WHAT THE PROOF ACTUALLY DOES: it moves the obligation across `toℕ`.
-- `add-mod` is `fromℕ< (mod-suc-bound (toℕ g ℕ+ toℕ x) n)`, so
-- `toℕ-fromℕ<` reads it back as `(toℕ g ℕ+ toℕ x) mod-suc n`, and
-- `toℕ-injective` turns the Fin-equation into a ℕ-equation.  What is left is
-- exactly `mod-cancel`'s shape with `c = toℕ x` — the residue `toℕ g` is
-- cancelled against itself, leaving `toℕ g mod-suc n ≡ 0`.  `mod-suc-id`
-- collapses the reduction (g is already below the modulus) and
-- `toℕ-injective` lands back in `Fin (suc n)`.
--
-- ⚑ AND THIS IS WHY THE `Zn` DEFERRAL AND THIS ONE WERE THE SAME DEFERRAL.
-- `Sites/Zn.agda:47-51` records *"there is no group-law field on
-- PontryaginDual, so these definitions are not yet *proved* to satisfy the
-- abelian-group axioms here … A follow-on slice can add the law witnesses
-- (assoc / id / inv via the Mod arithmetic lemmas)."*  The `fix→unit` law
-- below is the first of those witnesses to land; it is the inv/id law read
-- through the torsor interface rather than the group one.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.ResidueAtom.Cyclic where

open import Substrate.Foundation.Empty.Bot
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Plus
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
open import Substrate.Algebra.Nat.Mod.Cancel
open import Substrate.Algebra.PontryaginDual.Sites.Zn
open import Substrate.Category.Lawvere
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. `add-mod` read through `toℕ`.
--
-- The definitional content of `add-mod`, stated as an equation so the proof
-- below never has to unfold `fromℕ<` again.
------------------------------------------------------------------------

toℕ-add-mod : (n : ℕ) (a b : Fin (suc n)) →
              toℕ (add-mod n a b) ≡ (toℕ a ℕ+ toℕ b) mod-suc n
toℕ-add-mod n a b = toℕ-fromℕ< (mod-suc-bound (toℕ a ℕ+ toℕ b) n)

------------------------------------------------------------------------
-- 2. Cancellation on the cyclic carrier.
--
-- `mod-cancel` with b := 0 and c := toℕ x.  The right-hand side needs
-- `(0 ℕ+ toℕ x) mod-suc n`, which is `(toℕ x) mod-suc n` definitionally
-- (`_ℕ+_` reduces on its first argument), so the hypothesis transports with
-- no rewriting.
------------------------------------------------------------------------

cyc-fix : (n : ℕ) (g x : Fin (suc n)) →
          add-mod n g x ≡ x → g ≡ zero
cyc-fix n g x eq = toℕ-injective (trans (sym (mod-suc-id (toℕ g) n (toℕ-bound g))) reduced)
  where
    -- the hypothesis, moved across toℕ and past add-mod's definition.
    ℕ-eq : (toℕ g ℕ+ toℕ x) mod-suc n ≡ toℕ x
    ℕ-eq = trans (sym (toℕ-add-mod n g x)) (cong toℕ eq)

    -- x is below the modulus, so `toℕ x` IS its own residue — which is what
    -- puts the hypothesis into mod-cancel's `(b ℕ+ c) mod-suc m` shape at b = 0.
    x-fixed : (zero ℕ+ toℕ x) mod-suc n ≡ (toℕ g ℕ+ toℕ x) mod-suc n
    x-fixed = trans (mod-suc-id (toℕ x) n (toℕ-bound x)) (sym ℕ-eq)

    reduced : toℕ g mod-suc n ≡ toℕ (zero {n})
    reduced = mod-cancel (toℕ g) zero (toℕ x) n (sym x-fixed)

------------------------------------------------------------------------
-- 3. The torsor atom, and the residue flip it licenses.
------------------------------------------------------------------------

Cyclic-torsor : (n : ℕ) → TorsorAtom (Fin (suc n))
Cyclic-torsor n = record
  { _∙_      = add-mod n
  ; e        = zero
  ; fix→unit = cyc-fix n
  }

-- translation by any NON-ZERO residue is fixed-point-free on ℤ/(suc n): the
-- cyclic reading of "a non-trivial residue is a genuine distinction".
Cyclic-residue-fpf : (n : ℕ) (g : Fin (suc n)) →
                     (g ≡ zero → ⊥) → FixedPointFree (Fin (suc n))
Cyclic-residue-fpf n g g≢0 = translate-fpf (Cyclic-torsor n) g g≢0

-- the canonical witness on ℤ/(suc (suc n)): the generator 1, non-zero by
-- constructor disjointness, so the instance closes with nothing to discharge.
Cyclic-residue-fpf-one : (n : ℕ) → FixedPointFree (Fin (suc (suc n)))
Cyclic-residue-fpf-one n = Cyclic-residue-fpf (suc n) (suc zero) (λ ())
