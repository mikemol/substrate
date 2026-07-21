{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Z.CommRing — ⟡ℤ-CommRing.
--
-- ℤ as a `CommutativeRing`. ROUTE A of ⟡jac-neg-three-routes: the RING GAUGE,
-- in which negation lives IN the carrier (`Group.inv = -ℤ_`).
--
-- ⚑ THREE ROUTES, ONE WEDGE — AND THE COVER IS THE DELIVERABLE. Route A is NOT
-- in competition with the others; it is one COORDINATE of a single identity,
-- alongside
--   B — the LOG/EXP gauge: negation is TRANSPORTED, never added to the carrier
--       (`ExpLogCodec.exp-⊕` carries additive inverses to multiplicative ones;
--       `ExpLogCodec.agda:47-56`, live instance `ℤ-power-codec`,
--       `GValueLSpace/Primes.agda:209`), and
--   C — the SEMIRING gauge: negation ELIMINATED by transposition (`det⁺ ≡ det⁻ ⊕ 2`).
-- Building only the "preferred" one and discarding the rest would destroy the
-- object worth having: the COVERING construction exhibiting all three as
-- readings of one wedge (⟡jac-neg-cover). Each route is kept; the equivalence
-- is the mathematics. (This module was once proposed for deletion on
-- efficiency grounds — that was the collapse the cover exists to prevent.)
--
-- ⚑ WHY `+-coherent = refl` TYPECHECKS — AND WHAT ACTUALLY MAKES IT FRAGILE.
-- `Ring` fields `+-coherent : monoid (group +-abelian) ≡ +-monoid semiring`
-- (`Ring.agda:31-36`).
--
-- ⚠ A CORRECTION, MEASURED. An earlier note (inherited from a saturation pass
-- and repeated in this arc's first two commits) said this is `refl` ONLY IF
-- both sides are the same term, and that two `mk-monoid` applications would be
-- DISTINCT. **That is false.** A probe with a fresh, unshared
-- `mk-monoid _+ℤ_ 0ℤ +ℤ-assoc +ℤ-identityˡ +ℤ-identityʳ` typechecks
-- `+-coherent = refl` perfectly well: `mk-monoid` is transparent, so identical
-- arguments normalize to identical records.
--
-- THE REAL CONDITION is definitional equality of the two monoids — same op,
-- same identity, and the same LAW PROOF TERMS. Proof-term drift is what breaks
-- it, and that IS reachable; measured with a propositionally-equal but
-- definitionally-different identityˡ:
--     idL' x = trans (+ℤ-comm 0ℤ x) (+ℤ-identityʳ x)
--   ⇒ error [UnequalTerms]:
--     trans (+ℤ-comm (+ 0) a) (+ℤ-identityʳ a) != +ℤ-identityˡ a
--
-- So sharing `ℤ-+-Monoid` (one top-level definition in `Semiring.Instances.Z`,
-- fed to `ℤ-semiring.+-monoid` there and `ℤ-+-Group.monoid` here) is still the
-- right move — not because rebuilding is fatal, but because it makes that drift
-- IMPOSSIBLE BY CONSTRUCTION: no later edit can supply a different-but-
-- equivalent proof on one side only. HOUSE PRECEDENT: `F2/AsField.agda:107,123`
-- shares `F₂-+-Monoid` the same way.
--
-- ANCHORS (all pre-existing): `+ℤ-inverseˡ`/`ʳ` `Z/Properties/Add.agda:102,97`;
-- `+ℤ-comm` `:57`; `*ℤ-comm` `Z/Properties/Mul.agda:59`; `-ℤ_` `Algebra/Z.agda:60`;
-- `ℤ-semiring`/`ℤ-+-Monoid` `Algebra/Semiring/Instances/Z.agda`.
--
-- Pure packaging: zero new theory, zero postulates, zero holes.
------------------------------------------------------------------------

module Substrate.Algebra.Z.CommRing where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Empty using (⊥)

open import Substrate.Algebra.Group using (Group)
open import Substrate.Algebra.AbelianGroup using (AbelianGroup)
open import Substrate.Algebra.Ring using (Ring)
open import Substrate.Algebra.CommutativeRing using (CommutativeRing)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_; -ℤ_)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-comm; +ℤ-inverseˡ; +ℤ-inverseʳ)
open import Substrate.Algebra.Z.Properties.Mul using (*ℤ-comm)
open import Substrate.Algebra.Semiring.Instances.Z
  using (ℤ-semiring; ℤ-+-Monoid)

------------------------------------------------------------------------
-- 1. The additive group — (ℤ, +ℤ, 0ℤ, -ℤ).
--
--    ⚑ `monoid = ℤ-+-Monoid` — THE SHARED TERM, not a fresh `mk-monoid`.
--    This line is what makes §3's `+-coherent = refl` go through.
------------------------------------------------------------------------

ℤ-+-Group : Group ℤ
ℤ-+-Group = record
  { monoid    = ℤ-+-Monoid
  ; inv       = -ℤ_
  ; inv-left  = +ℤ-inverseˡ
  ; inv-right = +ℤ-inverseʳ
  }

ℤ-+-AbelianGroup : AbelianGroup ℤ
ℤ-+-AbelianGroup = record
  { group  = ℤ-+-Group
  ; ·-comm = +ℤ-comm
  }

------------------------------------------------------------------------
-- 2. THE RING.
--
--    `+-coherent = refl` is a live REGRESSION TEST for proof-term drift (see
--    the header): it does not detect mere inlining — that stays definitional —
--    but if either side's additive-monoid LAW PROOFS are ever swapped for
--    different-but-equivalent ones, this line stops typechecking.
------------------------------------------------------------------------

ℤ-Ring : Ring ℤ
ℤ-Ring = record
  { semiring   = ℤ-semiring
  ; +-abelian  = ℤ-+-AbelianGroup
  ; +-coherent = refl
  }

------------------------------------------------------------------------
-- 3. THE COMMUTATIVE RING.
------------------------------------------------------------------------

ℤ-CommRing : CommutativeRing ℤ
ℤ-CommRing = record
  { ring   = ℤ-Ring
  ; *-comm = *ℤ-comm
  }

------------------------------------------------------------------------
-- 4. NON-VACUITY.
--
-- Both `Ring` and `CommutativeRing` are inhabited by the ONE-POINT ring (every
-- law holds when the carrier is trivial), so the instances alone prove little.
-- These witness that THIS one is the real ℤ.
------------------------------------------------------------------------

-- Negation actually crosses into the negative branch of the carrier.
neg-computes : -ℤ (+ 1) ≡ -suc 0
neg-computes = refl

-- ⚑ THE POLE THAT SEPARATES THIS GAUGE FROM F₂'s. In `F₂` negation is the
-- IDENTITY (`x + x ≡ 𝟘`, so `-x ≡ x`) — a ring whose additive inverse carries
-- no information. In ℤ it does: `-ℤ (+ 1)` is `-suc 0`, not `+ 1`. So Route A's
-- `Group.inv` is a genuine involution with content, which is exactly what
-- Route B must reproduce by TRANSPORT rather than by fielding it.
neg-is-not-identity : -ℤ (+ 1) ≡ (+ 1) → ⊥
neg-is-not-identity ()

------------------------------------------------------------------------
-- 5. HONEST SCOPE.
--
-- This module delivers Route A ONLY: the ring gauge, negation in the carrier.
-- It does NOT establish the equivalence of the three routes — that is
-- ⟡jac-neg-cover, whose apex is an `ExpLogCodec ℤ` with each route derived
-- THROUGH it (the `R.Trace.PeriodicCover` move: state the apex once, derive,
-- never restate). The cover additionally owes a MANDATORY vacuity pole: a
-- `trivial-codec` at G = ⊤ satisfies the apex's every field, so the apex ALONE
-- proves nothing and each route must exhibit a discrimination witness.
--
-- Nothing here is evidence about the Jacobian determinant; `Algebra.Z.JacobianResidue`
-- computes that, and this module supplies one of the three gauges in which its
-- `−2` may be read.
------------------------------------------------------------------------
