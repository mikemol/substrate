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

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Nat.Properties.Add using (+-comm)
open import Substrate.Foundation.Nat.Properties.Mul using (*-identityʳ; *-suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)

open import Substrate.Groups.Coxeter.Word using (Word; []; _++_)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-periodic)

module Substrate.Groups.Coxeter.Cyclic.NthPower (n : ℕ) where

open import Substrate.Groups.Coxeter.Cyclic.Core n using (_≈_; ε)
open import Substrate.Groups.Coxeter.Cyclic.Existential n using (normalize; canonical-cover-ex; normalize-canonical)
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat n using (power-concat-eq; power-cyclic-normalize)
open import Substrate.Groups.Coxeter.Cyclic.Base n using (power; Gen)
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Flat n public


------------------------------------------------------------------------
-- 1. flat-power-eq: apply-power-suc-flat (power j) m ≡ power (j * suc m).
------------------------------------------------------------------------

flat-power-eq : (j m : ℕ) → apply-power-suc-flat (power j) m ≡ power (j * suc m)
flat-power-eq j zero    = cong power (sym (*-identityʳ j))
flat-power-eq j (suc m) =
  trans (cong (_++ power j) (flat-power-eq j m))
  (trans (power-concat-eq (j * suc m) j)
         (cong power (trans (+-comm (j * suc m) j) (sym (*-suc j (suc m))))))

------------------------------------------------------------------------
-- 2. mult-suc-n-mod: (k * suc n) mod-suc n ≡ 0.
--
-- Induction on k: zero case definitional; step case uses +-comm to
-- align with mod-suc-periodic, then IH.
------------------------------------------------------------------------

mult-suc-n-mod : (k : ℕ) → (k * suc n) mod-suc n ≡ 0
mult-suc-n-mod zero    = refl
mult-suc-n-mod (suc k) =
  trans (cong (_mod-suc n) (+-comm (suc n) (k * suc n)))
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
