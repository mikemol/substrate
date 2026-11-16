------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower
--
-- The generic (suc n)-power identity for cyclic Coxeter groups:
--
--   ∀ (w : Word Gen) → apply-power-suc w n ≈ ε
--
-- where apply-power-suc w m = w · w · ... · w (m+1 copies via the
-- Coxeter `_·_`). This is the generic form of per-Zₙ's cube-identity /
-- fourth-power-identity / fifth-power-identity / seventh-power-identity.
--
-- Submodule layering:
--   Concat   — power-concat-eq + normalize/iter/power-cyclic-normalize chain.
--   Flat     — apply-power-suc / apply-power-suc-flat + flatten + flat-normalize.
--   (here)   — flat-power-eq + mult-suc-n-mod + nth-power-canonical + nth-power-identity.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Times
open import Substrate.Foundation.Nat.Properties.Add.PlusComm
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityʳ; *-suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To

open import Substrate.Groups.Coxeter.Word using (Word; []; _++_)
open import Substrate.Foundation.Nat.Nat.ModSuc
open import Substrate.Algebra.Nat.Mod.ModSucBound
open import Substrate.Algebra.Nat.Mod.ModSucId
open import Substrate.Algebra.Nat.Mod.ModSucPeriodic
open import Substrate.Algebra.Nat.Mod.ModSucSuc
open import Substrate.Algebra.Nat.Mod.SucModSucLt
open import Substrate.Algebra.Nat.Mod.SucModSucSelf
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen

module Substrate.Groups.Coxeter.Cyclic.NthPower (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Core n using (_≈_; ε)
-- ⚑ TWO OF THE THREE NAMES WERE NOT `Existential`'s (Ⓑ2c-BRIDGE10‴).
-- `canonical-cover-ex` is; `normalize` and `normalize-canonical` belong to
-- `ListPresentation` and arrived through Existential's own open — so this clause
-- named two non-exports, bound nothing, and failed at the use site as a warning.
-- ⚑ ORDER: Base then Existential, THEN the application that consumes both.
open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
-- ⚑ A THIRD DISSOLVED PARENT (Ⓑ2c-BRIDGE10‴) — `NthPower.Concat`, split into
-- leaves by the same commit.  The two names this file used sit in two of them.
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Flat n public


------------------------------------------------------------------------
-- 1. flat-power-eq: apply-power-suc-flat (power j) m ≡ power (j * suc m).
------------------------------------------------------------------------

flat-power-eq : (j m : ℕ) → apply-power-suc-flat (power j) m ≡ power (j * suc m)
flat-power-eq j zero    = cong power (sym (*-identityʳ j))
flat-power-eq j (suc m) =
  trans (cong (_++ power j) (flat-power-eq j m))
  (trans (power-concat-eq (j * suc m) j)
         (cong power (trans (+ℕ-comm (j * suc m) j) (sym (*-suc j (suc m))))))

------------------------------------------------------------------------
-- 2. mult-suc-n-mod: (k * suc n) mod-suc n ≡ 0.
--
-- Induction on k: zero case definitional; step case uses +ℕ-comm to
-- align with mod-suc-periodic, then IH.
------------------------------------------------------------------------

mult-suc-n-mod : (k : ℕ) → (k * suc n) mod-suc n ≡ 0
mult-suc-n-mod zero    = refl
mult-suc-n-mod (suc k) =
  trans (cong (_mod-suc n) (+ℕ-comm (suc n) (k * suc n)))
  (trans (mod-suc-periodic (k * suc n) n)
         (mult-suc-n-mod k))

------------------------------------------------------------------------
-- 3. nth-power-canonical: the canonical case (via canonical-cover-ex).
------------------------------------------------------------------------

nth-power-canonical : (k : Fin (suc n)) →
                      normalize (apply-power-suc-flat (power (toℕ k)) n) ≡ []
nth-power-canonical k =
  trans (cong normalize (flat-power-eq (toℕ k) n))
  (trans (power-cyclic-normalize (toℕ k * suc n))
         (cong power (mult-suc-n-mod (toℕ k))))

------------------------------------------------------------------------
-- 4. nth-power-identity: ∀ (w : Word Gen) → apply-power-suc w n ≈ ε.
--
-- Chain:
--   apply-power-suc-flatten        : ·-tower ↔ ++-tower under normalize
--   apply-power-suc-flat-normalize : argument can be canonicalized
--   canonical-cover-ex             : dispatch on normalize w's canonical form
--   nth-power-canonical            : per-position power case
------------------------------------------------------------------------

nth-power-identity : (w : Word Gen) → apply-power-suc w n ≈ ε
nth-power-identity w =
  trans (apply-power-suc-flatten w n)
  (trans (apply-power-suc-flat-normalize w n)
         (canonical-cover-ex
            (λ {w'} _ → normalize (apply-power-suc-flat w' n) ≡ [])
            nth-power-canonical
            (normalize-canonical w)))
