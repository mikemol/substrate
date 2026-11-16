------------------------------------------------------------------------
-- Substrate.Algebra.Nat.Mod.Cancel
--
-- MODULAR CANCELLATION — the one modular fact the `Mod` family was missing.
--
--   mod-cancel : (a ℕ+ c) mod-suc m ≡ (b ℕ+ c) mod-suc m
--              → a mod-suc m ≡ b mod-suc m
--
-- ⚑ WHY IT WAS ABSENT, AND WHY THAT IS STRUCTURAL RATHER THAN AN OVERSIGHT.
-- Every existing `Algebra.Nat.Mod.*` lemma is a CONGRUENCE or REDUCTION law —
-- `mod-+-left`/`mod-+-right`/`mod-add-hom`/`mod-*-left`/`mod-*-right`/
-- `mod-mult-hom` push `mod` through an operation, and `mod-suc-periodic` /
-- `mod-periodic-mult` erase multiples of the modulus.  Those all say how mod
-- INTERACTS with structure.  Cancellation says something different: that mod
-- REFLECTS an equation back — the one direction a homomorphism does not give
-- for free, and so the one shape the family could grow past without noticing.
-- (`--grep 'mod.*inj|inj.*mod|mod.*cancel|cancel.*mod'` → 0 names.)
--
-- ⚑ WHAT IT UNBLOCKS, both self-documented deferrals:
--   * `PontryaginDual/Sites/Zn.agda:46-51` — *"there is no group-law field on
--     PontryaginDual, so these definitions are not yet *proved* to satisfy the
--     abelian-group axioms here … A follow-on slice can add the law witnesses
--     (assoc / id / inv via the Mod arithmetic lemmas)."*
--   * `TorsorAtom (Fin (suc n))` for the cyclic wedge carrier `Cyc-div`
--     (`Algebra/Fin/Wedge.agda:61`), whose `fix→unit` is this lemma read through
--     `toℕ`.  Every carrier packaged before it (F₂, ℕ, ℤ, List) had cancellation
--     either definitional or group-theoretic; the cyclic one did not, which is
--     exactly why it was the expensive carrier.
--
-- ⚑ THE PROOF IS THE INVERSE ARGUMENT, AND A FIRST DRAFT TOOK THE WRONG ROUTE.
-- Peeling one `suc` at a time via `mod-suc-suc` looks shorter, and the step it
-- needs — from `(suc x) mod-suc m ≡ (suc y) mod-suc m` conclude `x ≡ y` — is
-- CIRCULAR: that IS cancellation, at c = 1.  (The draft reached for a
-- `postulate` there, which this repo forbids and which would have smuggled the
-- theorem in as an assumption.)  The honest route completes `c` to a multiple of
-- the modulus: add `suc m ∸ (c mod-suc m)`, use `∸-+-id` to collapse the sum to
-- `suc m`, and `mod-periodic-mult` to erase it.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.Mod.Cancel where

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Monus
open import Substrate.Foundation.Nat.Plus
open import Substrate.Foundation.Nat.Properties.Add.PlusIdentityR
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Add.PlusAssoc
open import Substrate.Foundation.Nat.Properties.Order using (<→≤)
open import Substrate.Foundation.Nat.Properties.Sub using (∸-+-id)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Algebra.Nat.Mod.Homomorphism using (mod-+-left; mod-+-right;
                                                          mod-periodic-mult)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong

------------------------------------------------------------------------
-- 1. THE COMPLETION.  For any c, adding `suc m ∸ (c mod-suc m)` makes the sum
--    invisible mod (suc m): the residue is completed to a full modulus.
--
--    (x ℕ+ c) ℕ+ (suc m ∸ (c mod-suc m))  ≡mod  x
------------------------------------------------------------------------

-- the residue is below the modulus, hence ≤ it — the hypothesis `∸-+-id` wants.
res≤mod : (c m : ℕ) → (c mod-suc m) ≤ suc m
res≤mod c m = <→≤ (mod-suc-bound c m)

-- completing the residue: (suc m ∸ c') ℕ+ c' ≡ suc m, one modulus exactly.
complete : (c m : ℕ) → ((suc m ∸ (c mod-suc m)) ℕ+ (c mod-suc m)) ≡ suc m
complete c m = ∸-+-id (suc m) (c mod-suc m) (res≤mod c m)

------------------------------------------------------------------------
-- 2. Adding the completion is invisible under the reduction.
--
--    ⚑ `mod-periodic-mult x k m : (x ℕ+ k * suc m) mod-suc m ≡ x mod-suc m`
--    at k = 1, with `x ℕ+ 1 * suc m` normalised to `x ℕ+ suc m`.
------------------------------------------------------------------------

add-modulus : (x m : ℕ) → (x ℕ+ suc m) mod-suc m ≡ x mod-suc m
add-modulus x m =
  trans (cong (λ k → (x ℕ+ k) mod-suc m) (sym (+ℕ-identityʳ (suc m))))
        (mod-periodic-mult x 1 m)

------------------------------------------------------------------------
-- 3. MODULAR CANCELLATION.
--
-- Both sides gain `d = suc m ∸ (c mod-suc m)`.  On each side the tail
-- `c ℕ+ d` reduces to a full modulus (via `mod-+-left` to expose `c mod-suc m`,
-- then `complete`), which `add-modulus` erases — leaving `a` and `b`.
------------------------------------------------------------------------

mod-cancel : (a b c m : ℕ) →
             (a ℕ+ c) mod-suc m ≡ (b ℕ+ c) mod-suc m →
             a mod-suc m ≡ b mod-suc m
mod-cancel a b c m eq = trans (sym (collapse a)) (trans lifted (collapse b))
  where
    d : ℕ
    d = suc m ∸ (c mod-suc m)

    -- ⚑ THE TAIL IS A FULL MODULUS, once c is read through its residue.
    --   (c mod-suc m) ℕ+ d ≡ suc m   —   `complete` with the summands swapped.
    tail≡mod : ((c mod-suc m) ℕ+ d) ≡ suc m
    tail≡mod = trans (+ℕ-comm (c mod-suc m) d) (complete c m)

    -- x ℕ+ (c ℕ+ d) reduces to x: expose c's residue with `mod-+-right`, sum it
    -- with d into one modulus, then erase the modulus.
    collapse : (x : ℕ) → ((x ℕ+ c) ℕ+ d) mod-suc m ≡ x mod-suc m
    collapse x =
      trans (cong (_mod-suc m) (+ℕ-assoc x c d))
      (trans (sym (mod-+-right x (c ℕ+ d) m))
      (trans (cong (λ k → (x ℕ+ k) mod-suc m)
                   (trans (sym (mod-+-left c d m))
                          (cong (_mod-suc m) tail≡mod)))
      (trans (mod-+-right x (suc m) m) (add-modulus x m))))

    -- the hypothesis with d added on the right of both sides.
    lifted : ((a ℕ+ c) ℕ+ d) mod-suc m ≡ ((b ℕ+ c) ℕ+ d) mod-suc m
    lifted =
      trans (sym (mod-+-left (a ℕ+ c) d m))
      (trans (cong (λ k → (k ℕ+ d) mod-suc m) eq)
             (mod-+-left (b ℕ+ c) d m))
