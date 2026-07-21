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
-- ⚑ THE SHARED ADDITIVE MONOID. `ℤ-+-Monoid` is a TOP-LEVEL definition, not
-- inlined into the record, so any downstream structure fielding both this
-- semiring and the same additive monoid (e.g. `Ring ℤ`, whose `+-coherent`
-- relates them) gets ONE term on both sides.
--
-- ⚠ CORRECTION, MEASURED. This module first claimed that rebuilding via a
-- second `mk-monoid` application would yield DISTINCT terms and break such a
-- coherence law. **That is false** — `mk-monoid` is transparent, so identical
-- arguments normalize identically and `refl` goes through either way. What
-- actually breaks definitional equality is LAW-PROOF DRIFT (a
-- propositionally-equal but definitionally-different identity/assoc proof on
-- one side). Sharing this term is still right, but as drift-PROOFING, not
-- because rebuilding is fatal. Full probe + the failing case:
-- `Algebra/Z/CommRing.agda` header.
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

-- ⚑ THE POLE THAT MATTERS — AND IT IS THE CODEC'S `invˡ`, NOT A RING POINTER.
-- This is EXACTLY the hypothesis `ExpLogCodec.Inverse` takes (`ExpLogCodec.agda:
-- 66-68`: `invˡ : (x : L) → x ⊕ neg x ≡ 𝟘`) at L = ℤ, ⊕ = `_+ℤ_`, neg = `-ℤ_`,
-- 𝟘 = 0ℤ. Supplying it is what makes every `expL x` a UNIT with inverse
-- `expL (neg x)` (`codec-inverse`, `:73-77`). ℤ is the LOG side of the live
-- instance `ℤ-power-codec : ExpLogCodecℚ ℤ` (`GValueLSpace/Primes.agda:209`;
-- `Properties.agda:137` — "L=ℤ a GROUP via `_+ℤ_`"), so this term is the ℤ-side
-- entry point to that codec, not a waypoint toward a ring.
ℤ-additive-inverse : (x : ℤ) → x +ℤ (-ℤ x) ≡ 0ℤ
ℤ-additive-inverse = +ℤ-inverseʳ

-- ⚑ WHAT THE RECORD DOES NOT FIELD IS THE DISCIPLINE, NOT A GAP.
-- `Semiring` fields neither commutativity nor negation because THIS SUBSTRATE
-- DOES NOT STUFF STRUCTURE INTO RECORDS — it takes it as MODULE PARAMETERS and
-- lets the consumer name it. `ExpLogCodec.agda:30-33` performs exactly this move
-- for exactly this reason ("the additive L-space carrier was a `L : Set` field,
-- forcing Set₁; taking it as the module parameter keeps the record in Set, and
-- the CONSUMER names it"). So the absent fields are a design commitment, and
-- reading them as a deficiency the way a `Ring` would repair is backwards.
--
-- ⚑ AND NEGATION IS AVAILABLE IN A SEMIRING — VIA log / involute-over-1 / antilog.
-- You do NOT add inverses to the carrier (that is what the four gauges decline,
-- §4 above). You TRANSPORT: `exp-⊕ : expL (a ⊕ b) ≈ expL a · expL b` carries the
-- additive side to the multiplicative side, the involution about 𝟙 (reciprocal)
-- acts there, and the antilog returns. `ExpLogCodec.agda:47-56` states the result
-- outright — "the reciprocal involution IS the additive negation transported by
-- exp; no multiplicative-inverse axiom is needed, it is DERIVED."
-- ADDITIVE COMMUTATIVITY IS THE SAME BRIDGE: `a ⊕ b` and `b ⊕ a` cross to
-- `expL a · expL b` and `expL b · expL a`, which `*-comm` identifies — so ⊕-comm
-- is read off the multiplicative side, not fielded.
--
-- HONEST SCOPE. Those two transports are the ROUTE, stated here because this
-- module's §4 previously mis-pointed them at `Ring`/`CommutativeRing`; they are
-- NOT built in this file. Building them at ℤ is ⟡jac-neg-three-routes Route B
-- (the ruled-PREFERRED route). `+ℤ-comm` (`Z/Properties/Add.agda:57`) and
-- `*ℤ-comm` (`Z/Properties/Mul.agda:59`) are proven and available; this module
-- claims only the semiring structure.
