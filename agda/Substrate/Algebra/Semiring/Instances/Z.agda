{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.Semiring.Instances.Z — ⟡ℤ-semiring.
--
-- ℤ as a `Semiring`. PURE PACKAGING: every law is already proven in
-- `Algebra.Z.Properties.{Add,Mul,MulFull}`; this module only assembles them
-- into the record, reusing the `mk-monoid` costructure from the four-gauge
-- `Semiring.Instances`. ZERO new theory, zero postulates, zero holes.
--
-- ⚑ WHY A SEPARATE FILE from `Semiring.Instances`. That module is the FOUR
-- JOB GAUGES (ℕ counting · F₂ carrier · Bool routing · tropical cost) — a
-- curated story about semiring-VM placement. ℤ is not a fifth gauge; it is the
-- RING-side carrier, and the gauges' defining property is that their carriers
-- have NO additive inverses (see §4). Filing ℤ among them would blur exactly
-- the distinction the four-gauge split exists to make.
--
-- ⚑ THE SHARED ADDITIVE MONOID (load-bearing for the sequel). `ℤ-+-Monoid` is
-- a TOP-LEVEL definition, not inlined into the record. A `Ring ℤ` fields both
-- a `Semiring` and an additive `AbelianGroup`, with a `+-coherent` law saying
-- the two agree; if each side builds its own `mk-monoid` application those are
-- distinct terms and `+-coherent` cannot be `refl` — every downstream `subst`
-- then goes opaque. Sharing THIS term keeps it definitional.
--
-- ⚑ THE ARGUMENT ORDER MATCHES DIRECTLY, unlike ℕ. `Semiring.distrib-right`
-- wants `(a + b) * c ≡ (a * c) + (b * c)`, and `*ℤ-distribʳ-+` is stated in
-- exactly that shape — so no argument shuffle is needed here (contrast
-- `Instances.agda:78`, where ℕ's `*-distribʳ-+` needs `λ a b c → … c a b`).
--
-- ANCHORS (all pre-existing, verified): `+ℤ-assoc`/`+ℤ-identityˡ`/`ʳ`/
-- `+ℤ-inverseʳ` at `Z/Properties/Add.agda:71,85,89,97`; `*ℤ-assoc`/
-- `*ℤ-identityˡ`/`ʳ`/`*ℤ-zeroˡ`/`ʳ`/`*ℤ-distribˡ-+`/`ʳ-+` at
-- `Z/Properties/MulFull.agda:61,42,46,49,53,104,113`. (`*ℤ-comm` lives at
-- `Z/Properties/Mul.agda:59` — NOT consumed here; see §4.)
------------------------------------------------------------------------

module Substrate.Algebra.Semiring.Instances.Z where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.Monoid using (Monoid)
open import Substrate.Algebra.Semiring using (Semiring)
open import Substrate.Algebra.Semiring.Instances using (mk-monoid)

open import Substrate.Algebra.Z using (ℤ; +_; -suc_; 0ℤ; 1ℤ; -ℤ_)
open import Substrate.Algebra.Z.Arithmetic using (_+ℤ_; _*ℤ_)
open import Substrate.Algebra.Z.Properties.Add
  using (+ℤ-assoc; +ℤ-identityˡ; +ℤ-identityʳ; +ℤ-inverseʳ)
open import Substrate.Algebra.Z.Properties.MulFull
  using (*ℤ-assoc; *ℤ-identityˡ; *ℤ-identityʳ;
         *ℤ-zeroˡ; *ℤ-zeroʳ; *ℤ-distribˡ-+; *ℤ-distribʳ-+)

------------------------------------------------------------------------
-- 1. The additive monoid — (ℤ, +ℤ, 0ℤ).
--
--    ⚑ Defined ONCE and named, so a downstream `Ring ℤ` shares this exact
--    term between its `Semiring.+-monoid` and its `AbelianGroup.group.monoid`
--    (the `+-coherent = refl` discipline documented in the header).
------------------------------------------------------------------------

ℤ-+-Monoid : Monoid ℤ
ℤ-+-Monoid = mk-monoid _+ℤ_ 0ℤ +ℤ-assoc +ℤ-identityˡ +ℤ-identityʳ

------------------------------------------------------------------------
-- 2. The multiplicative monoid — (ℤ, *ℤ, 1ℤ).
--
--    `1ℤ = + 1` and `0ℤ = + 0` DEFINITIONALLY (Algebra/Z.agda:43-47), so the
--    laws — stated over `(+ 1)` / `(+ 0)` — apply at `1ℤ` / `0ℤ` on the nose.
------------------------------------------------------------------------

ℤ-*-Monoid : Monoid ℤ
ℤ-*-Monoid = mk-monoid _*ℤ_ 1ℤ *ℤ-assoc *ℤ-identityˡ *ℤ-identityʳ

------------------------------------------------------------------------
-- 3. THE SEMIRING.
------------------------------------------------------------------------

ℤ-semiring : Semiring ℤ
ℤ-semiring = record
  { +-monoid          = ℤ-+-Monoid
  ; *-monoid          = ℤ-*-Monoid
  ; distrib-left      = *ℤ-distribˡ-+
  ; distrib-right     = *ℤ-distribʳ-+
  ; zero-absorb-left  = *ℤ-zeroˡ
  ; zero-absorb-right = *ℤ-zeroʳ
  }

------------------------------------------------------------------------
-- 4. NON-VACUITY + the honest boundary.
--
-- A `Semiring` record is inhabited by degenerate structures (the one-point
-- carrier satisfies every field), so the instance alone proves little. These
-- three terms witness that THIS one is the real ℤ — and specifically that it
-- carries what the four job gauges do NOT: additive inverses.
------------------------------------------------------------------------

-- The additive monoid genuinely absorbs NEGATIVES (`2 + (-1) = 1`) — a
-- computation ℕ's counting gauge cannot express.
add-computes : (+ 2) +ℤ (-suc 0) ≡ (+ 1)
add-computes = refl

-- The multiplicative monoid carries the SIGN rule (`(-1)·(-1) = 1`) — this is
-- the arithmetic `Algebra.Q.JacobianCollision`'s ℚ evaluations and
-- `Algebra.Z.JacobianResidue`'s `detJac` coefficients actually run on.
mul-sign-computes : (-suc 0) *ℤ (-suc 0) ≡ (+ 1)
mul-sign-computes = refl

-- ⚑ THE POLE THAT MATTERS, AND THE FORWARD POINTER. `Semiring` has no
-- inverse field, so this fact is INVISIBLE in the record above — yet it is
-- exactly why ℤ is not a job gauge and why a `Ring ℤ` is reachable. Named
-- here so the omission is a stated boundary, not a silent one.
ℤ-additive-inverse : (x : ℤ) → x +ℤ (-ℤ x) ≡ 0ℤ
ℤ-additive-inverse = +ℤ-inverseʳ

-- HONEST BOUNDARY. `Semiring` fields neither COMMUTATIVITY (its own header,
-- `Semiring.agda:31-32`, says additive commutativity "is a separate field, not
-- here") nor NEGATION. Both are proven for ℤ already — `+ℤ-comm`
-- (`Z/Properties/Add.agda:57`), `*ℤ-comm` (`Z/Properties/Mul.agda:59`),
-- `+ℤ-inverseˡ`/`ʳ` (`:102,97`) — and they are what a `Ring ℤ` / `CommutativeRing ℤ`
-- will consume. This module claims ONLY the semiring structure; it does not
-- claim, and must not be cited for, the ring.
