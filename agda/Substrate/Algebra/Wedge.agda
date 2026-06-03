------------------------------------------------------------------------
-- Substrate.Algebra.Wedge
--
-- THE GENERIC WEDGE — the keystone operator. A wedge of `a` against `b`
-- is the triple (quotient, remainder, witness : a = recon q b r): "a built
-- as q copies of b, plus a remainder r." Over a carrier that supplies only
-- a reconstruction `recon : ℕ → C → C → C` ("q copies of b, then r").
--
-- The three universal properties are the three PROJECTIONS of this triple
-- (see [[project_center_free_universal_property]]):
--   * Forgetful  = read the witness, evaluate back to the element  (`forget`)
--   * Presented  = keep the remainder, drop the quotient (kernel ≡ mod b) (`cell`)
--   * Free       = keep everything and recurse on the remainder = the TERM
--                  (the `Trace` data type; EEATrace is its ℕ instance)
-- and `=` is the corner `quot = 1, rem = z` where the term IS the element.
-- keep-q = Free (the term); forget-q = Forgetful (the value); the keep/forget
-- axis IS Free ⊣ Forgetful, and the adjunction's triangle identity is the
-- witness `a = recon q b r` itself.
--
-- THE TEST OF THE INTERFACE (why this file exists): the substrate's existing
-- ℕ wedge (Algebra.Nat.GCD.Wedge) and the Euclidean trace (EEATrace) are
-- re-obtained as INSTANCES — `fromℕ-Wedge`, `fromEEATrace` typecheck — so the
-- generic interface is provably right, not merely well-drawn.
--
-- SCOPED OUT (deliberately, the next lifts):
--   * the canonicality refinement `rem < b` (smallness) — that is the
--     UNIQUENESS / no-gauge certificate (the certified, natural wedge);
--     this loose wedge keeps the triple, not its canonical representative.
--   * Quot = ℕ is baked (the count = iterated combine = Peano); lifting the
--     quotient type is itself a deformation to track later.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)
import Substrate.Algebra.Nat.GCD.Wedge as N
import Substrate.Algebra.Nat.GCD.EEATrace as NT

------------------------------------------------------------------------
-- 1. The carrier interface: what a type needs to host a wedge.
------------------------------------------------------------------------

record DivStr : Set₁ where
  field
    C     : Set
    z     : C                 -- the terminal divisor (the recursion stops here)
    recon : ℕ → C → C → C     -- recon q b r = "q copies of b, then the remainder r"

open DivStr public

------------------------------------------------------------------------
-- 2. The generic wedge: the triple (quotient, remainder, witness).
------------------------------------------------------------------------

record Wedge (D : DivStr) (a b : C D) : Set where
  field
    quot     : ℕ
    rem      : C D
    wedge-eq : a ≡ recon D quot b rem

open Wedge public

------------------------------------------------------------------------
-- 3. The three reads — projections of the one triple.
------------------------------------------------------------------------

-- FORGETFUL: read the witness, evaluate the term back to the element.
forget : {D : DivStr} {a b : C D} → Wedge D a b → C D
forget {D} {b = b} w = recon D (quot w) b (rem w)

forget-correct : {D : DivStr} {a b : C D} (w : Wedge D a b) → forget w ≡ a
forget-correct w = sym (wedge-eq w)

-- PRESENTED: keep the remainder = the cell (its kernel is "≡ mod b").
cell : {D : DivStr} {a b : C D} → Wedge D a b → C D
cell w = rem w

-- FREE: keep everything and recurse on the remainder = the term (the trace).
data Trace (D : DivStr) : C D → C D → C D → Set where
  done : (a : C D) → Trace D a (z D) a
  more : {a g : C D} (b : C D) (w : Wedge D a b) →
         Trace D b (rem w) g → Trace D a b g

-- the forgetful (annihilating) read of the WHOLE term: collapse to g (the
-- divisor at the end of the chain — the gcd index). The free read is the
-- Trace itself, kept; a richer keeping-fold into a coefficient target is the
-- Bézout read (Algebra.Nat.GCD.Fold: gcd-fold vs bezout-ℤ are these two).
collapse : {D : DivStr} {a b g : C D} → Trace D a b g → C D
collapse {g = g} _ = g

------------------------------------------------------------------------
-- 4. THE INTERFACE TEST: ℕ instance, and the existing wedge + trace fall out.
------------------------------------------------------------------------

ℕ-div : DivStr
ℕ-div = record { C = ℕ ; z = zero ; recon = λ q b r → q * b + r }

-- the existing ℕ wedge is a generic wedge (forgetting only `rem < b`).
fromℕ-Wedge : {a b : ℕ} → N.Wedge a b → Wedge ℕ-div a b
fromℕ-Wedge w = record
  { quot = N.quotient w ; rem = N.remainder w ; wedge-eq = N.wedge-eq w }

-- the Euclidean trace is a generic trace.
fromEEATrace : {a b g : ℕ} → NT.EEATrace a b g → Trace ℕ-div a b g
fromEEATrace (NT.base a)       = done a
fromEEATrace (NT.step b w rec) = more (suc b) (fromℕ-Wedge w) (fromEEATrace rec)
