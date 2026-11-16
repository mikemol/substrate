------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.NthPower.Flat
--
-- The flat-iteration tower + bridge to the ·-tower.
--
--   apply-power-suc       : Word Gen → ℕ → Word Gen   -- w · w · … · w
--   apply-power-suc-flat  : Word Gen → ℕ → Word Gen   -- w ++ w ++ … ++ w
--   apply-power-suc-flatten        : normalize (·-tower) ≡ normalize (++-tower)
--   apply-power-suc-flat-normalize : argument can be canonicalized under normalize
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Nat

open import Substrate.Groups.Coxeter.Word using (Word; _++_)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Cong
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Core.NormalizeAppend.Left
open import Substrate.Groups.Coxeter.Core.NormalizeAppend.Right

module Substrate.Groups.Coxeter.Cyclic.NthPower.Flat (n : ℕ) where

-- ⚑ `normalize` IS NOT `Existential`'s (Ⓑ2c-BRIDGE10‴).  `--provides` shows
-- Existential exporting six names, none of them `normalize`; it arrived through
-- Existential's own `open ListPresentation`, two hops from anywhere it is named.
-- A `using` naming a non-export is only a WARNING, so this bound nothing and the
-- error landed at the use site.  Applied to the SAME five arguments `Core` uses,
-- so both see one instance — a differently-applied copy is a different type.
-- ⚑ ORDER MATTERS: `Base` supplies `Gen`/`insert`, `Existential` supplies
-- `Canonical-ex`/`c-ε`/`insert-canonical-ex`, and the ListPresentation
-- APPLICATION consumes all five — so it must come after both.  Agda binds from
-- the statement onward, which `agda_defs --late-imports` exists to catch.
open import Substrate.Groups.Coxeter.Cyclic.Base n
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Existential n
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex
open import Substrate.Groups.Coxeter.Cyclic.Core n using (_·_; normalize-idem; normalize-append; normalize-append-right)
-- ⚑ A THIRD DISSOLVED PARENT (Ⓑ2c-BRIDGE10‴).  `NthPower.Concat` was split into
-- the six leaves below by the same commit; its consumers were not rewired either.
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerConcatEq n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.NormalizePower n
open import Substrate.Groups.Coxeter.Cyclic.NthPower.Concat.PowerCyclicNormalize n

------------------------------------------------------------------------
-- 1. apply-power-suc / apply-power-suc-flat.
--
-- apply-power-suc w m = w · w · ... · w (m+1 copies via _·_).
-- apply-power-suc-flat w m = same but via ++ instead of ·.
------------------------------------------------------------------------

apply-power-suc : Word Gen → ℕ → Word Gen
apply-power-suc w zero    = w
apply-power-suc w (suc k) = (apply-power-suc w k) · w

apply-power-suc-flat : Word Gen → ℕ → Word Gen
apply-power-suc-flat w zero    = w
apply-power-suc-flat w (suc k) = apply-power-suc-flat w k ++ w

------------------------------------------------------------------------
-- 2. apply-power-suc-flatten: normalize commutes the · away to ++.
------------------------------------------------------------------------

apply-power-suc-flatten : (w : Word Gen) (m : ℕ) →
                       normalize (apply-power-suc w m) ≡
                       normalize (apply-power-suc-flat w m)
apply-power-suc-flatten w zero    = refl
apply-power-suc-flatten w (suc m) =
  trans (normalize-idem ((apply-power-suc w m) ++ w))
  (trans (normalize-append (apply-power-suc w m) w)
  (trans (cong (λ x → normalize (x ++ w)) (apply-power-suc-flatten w m))
         (sym (normalize-append (apply-power-suc-flat w m) w))))

------------------------------------------------------------------------
-- 3. apply-power-suc-flat-normalize: normalize commutes through the
-- argument of apply-power-suc-flat.
------------------------------------------------------------------------

apply-power-suc-flat-normalize : (w : Word Gen) (m : ℕ) →
                              normalize (apply-power-suc-flat w m) ≡
                              normalize (apply-power-suc-flat (normalize w) m)
apply-power-suc-flat-normalize w zero    = sym (normalize-idem w)
apply-power-suc-flat-normalize w (suc m) =
  trans (normalize-append (apply-power-suc-flat w m) w)
  (trans (cong (λ x → normalize (x ++ w))
               (apply-power-suc-flat-normalize w m))
  (trans (sym (normalize-append (apply-power-suc-flat (normalize w) m) w))
         (normalize-append-right (apply-power-suc-flat (normalize w) m) w)))
