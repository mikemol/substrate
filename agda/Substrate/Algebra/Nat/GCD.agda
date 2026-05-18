------------------------------------------------------------------------
-- Substrate.Algebra.Nat.GCD
--
-- Substrate-native ℕ-level Greatest Common Divisor + Least Common
-- Multiple via the **Wedge + EEATrace** technique.
--
-- Per the structural conversation: modulo is a wedge — it decomposes
-- `a` into `(quotient, remainder)` at modulus `b` with the
-- reconstruction `a ≡ quotient * b + remainder`. The EEA recursion
-- is a chain of wedges; the trace data type captures the chain
-- structurally, with downstream properties (divides-left,
-- divides-right) proved by induction on the trace.
--
-- Termination of trace CONSTRUCTION uses Acc/well-founded recursion
-- (encapsulated in `compute-trace`); all downstream USES of the
-- trace are pure structural induction.
--
-- Avoids `Data.Nat.GCD`'s higher-level abstractions; uses
-- `Data.Nat.Divisibility` and `Data.Nat.DivMod` as base
-- infrastructure (these aren't "the GCD module").
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Nat.GCD where

open import Data.Nat
  using (ℕ; zero; suc; _+_; _*_; _<_; NonZero)
open import Data.Nat.Divisibility
  using (_∣_; divides; divides-refl; ∣-refl; ∣-trans;
         ∣m∣n⇒∣m+n; m∣m*n; n∣m*n)
open import Data.Nat.DivMod
  using (_%_; _/_; m%n<n; m≡m%n+[m/n]*n)
open import Data.Nat.Induction using (<-wellFounded-fast)
open import Data.Nat.Properties using (+-comm; <-cmp)
open import Data.Product using (Σ; _,_; proj₁; proj₂)
open import Induction.WellFounded using (Acc; acc)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; sym; trans; cong; subst)

------------------------------------------------------------------------
-- N-1: Wedge — modulo as a structural decomposition.
--
-- A Wedge a b packages the decomposition `a = quotient * b + remainder`
-- with `remainder < b`. This IS the "modulo is a wedge" framing:
-- both the quotient AND remainder are essential structural data;
-- together they reconstruct a.
------------------------------------------------------------------------

record Wedge (a b : ℕ) : Set where
  field
    quotient  : ℕ
    remainder : ℕ
    wedge-eq  : a ≡ quotient * b + remainder
    r<b       : remainder < b

open Wedge public

------------------------------------------------------------------------
-- N-2: construct-wedge — build a Wedge a (suc b) from Data.Nat.DivMod.
--
-- Bridges to stdlib's `_/_` and `_%_` operations. The stdlib lemma
-- `m≡m%n+[m/n]*n` provides the structural reconstruction equation
-- (modulo a +-comm rearrangement).
------------------------------------------------------------------------

construct-wedge : (a b : ℕ) → Wedge a (suc b)
construct-wedge a b = record
  { quotient  = a / suc b
  ; remainder = a % suc b
  ; wedge-eq  =
      trans (m≡m%n+[m/n]*n a (suc b))
            (+-comm (a % suc b) ((a / suc b) * suc b))
  ; r<b       = m%n<n a (suc b)
  }

------------------------------------------------------------------------
-- N-3: EEATrace — the structural recursion of the Euclidean algorithm.
--
-- EEATrace a b g asserts: gcd(a, b) = g, via a chain of wedge steps.
--
--   base : gcd(a, 0) = a (terminating case).
--   step : if (a, suc b) wedges to (q, r) with r < suc b, and we
--          have EEATrace (suc b) r g, then EEATrace a (suc b) g.
--
-- All downstream properties (divides-left, divides-right) become
-- structural induction on this data type.
------------------------------------------------------------------------

data EEATrace : ℕ → ℕ → ℕ → Set where
  base : ∀ a → EEATrace a 0 a
  step : ∀ {a g} (b : ℕ) (w : Wedge a (suc b)) →
         EEATrace (suc b) (remainder w) g →
         EEATrace a (suc b) g

------------------------------------------------------------------------
-- N-4: compute-trace — construct a trace via Acc (encapsulated).
--
-- The Acc-based recursion is hidden inside this constructor; all
-- downstream code uses the trace structurally.
------------------------------------------------------------------------

compute-trace-acc :
  (a b : ℕ) → Acc _<_ b → Σ ℕ (EEATrace a b)
compute-trace-acc a zero    _         = a , base a
compute-trace-acc a (suc b) (acc rec) =
  let w        = construct-wedge a b
      r-fits   = r<b w
      sub      = compute-trace-acc (suc b) (remainder w) (rec r-fits)
      sub-g    = proj₁ sub
      sub-trace = proj₂ sub
  in sub-g , step b w sub-trace

compute-trace : (a b : ℕ) → Σ ℕ (EEATrace a b)
compute-trace a b = compute-trace-acc a b (<-wellFounded-fast b)

------------------------------------------------------------------------
-- N-5: gcd-ℕ — extract the gcd value from the trace.
------------------------------------------------------------------------

gcd-ℕ : ℕ → ℕ → ℕ
gcd-ℕ a b = proj₁ (compute-trace a b)

------------------------------------------------------------------------
-- N-6: Divisibility properties — via structural induction on EEATrace.
--
-- trace-divides-right: g ∣ b. Direct from the trace's index structure.
--   At base: g = a, b = 0, and g ∣ 0 trivially.
--   At step: by IH on sub-trace at index (suc b, r), g ∣ suc b
--     (= g ∣ first arg of sub-trace, which is g ∣ second arg here).
--
-- trace-divides-left: g ∣ a. Uses the wedge reconstruction.
--   At base: g = a, g ∣ a trivially.
--   At step: a = q * suc b + r (wedge-eq). By IH on sub-trace,
--     g ∣ r and g ∣ suc b (the latter from trace-divides-right).
--     Then g ∣ q * suc b (from g ∣ suc b via m∣m*n + ∣-trans).
--     Then g ∣ q * suc b + r = a (via ∣m∣n⇒∣m+n + subst).
------------------------------------------------------------------------

mutual
  trace-divides-left : ∀ {a b g} → EEATrace a b g → g ∣ a
  trace-divides-left (base _)         = ∣-refl
  trace-divides-left {a} {.(suc b)} (step b w sub-trace) =
    let q     = quotient w
        r     = remainder w
        eq    = wedge-eq w               -- a ≡ q * suc b + r
        g∣r   = trace-divides-left  sub-trace   -- g ∣ r (first arg of sub-trace)
        g∣sb  = trace-divides-right sub-trace   -- wait, this gives g ∣ remainder, not g ∣ suc b
        -- Actually: sub-trace : EEATrace (suc b) r g.
        -- trace-divides-left  sub-trace : g ∣ suc b  (divides FIRST arg)
        -- trace-divides-right sub-trace : g ∣ r      (divides SECOND arg)
        -- So let me swap:
        g∣sb' : _ ∣ suc b
        g∣sb' = trace-divides-left sub-trace
        g∣r'  : _ ∣ r
        g∣r'  = trace-divides-right sub-trace
        g∣qsb : _ ∣ q * suc b
        g∣qsb = ∣-trans g∣sb' (n∣m*n q)
        g∣sum : _ ∣ (q * suc b + r)
        g∣sum = ∣m∣n⇒∣m+n g∣qsb g∣r'
    in subst (_ ∣_) (sym eq) g∣sum

  trace-divides-right : ∀ {a b g} → EEATrace a b g → g ∣ b
  trace-divides-right (base a)              = divides-refl 0
  trace-divides-right (step b w sub-trace)  =
    -- sub-trace : EEATrace (suc b) r g.
    -- trace-divides-left sub-trace : g ∣ suc b. This is the result we want
    -- (the result type is g ∣ suc b, since the step is at second-arg suc b).
    trace-divides-left sub-trace

------------------------------------------------------------------------
-- N-7: User-facing divisibility.
------------------------------------------------------------------------

gcd-divides-left  : ∀ a b → gcd-ℕ a b ∣ a
gcd-divides-left  a b = trace-divides-left  (proj₂ (compute-trace a b))

gcd-divides-right : ∀ a b → gcd-ℕ a b ∣ b
gcd-divides-right a b = trace-divides-right (proj₂ (compute-trace a b))

------------------------------------------------------------------------
-- N-8: lcm-ℕ — defined as a * b (loose bound).
--
-- The tight `lcm = a * b / gcd` requires NonZero handling for gcd.
-- The loose `lcm = a * b` is structurally divisible by both a and b
-- (via n∣m*n and m∣m*n + *-comm) and suffices for the
-- HasOrder-compose-commute lcm-style bound (which still tightens
-- substantially over k₁ * k₂ when k₁ and k₂ share a common factor —
-- but the tight bound needs the full gcd-quotient lemma).
--
-- For substrate's HasOrder-compose-commute purposes, lcm-ℕ a b =
-- a * b is sufficient: every multiple of a is a multiple of a · b
-- (since a | a*b). Tighter lcm-via-gcd-quotient deferred.
------------------------------------------------------------------------

lcm-ℕ : ℕ → ℕ → ℕ
lcm-ℕ a b = a * b

a-divides-lcm : ∀ a b → a ∣ lcm-ℕ a b
a-divides-lcm a b = m∣m*n b

b-divides-lcm : ∀ a b → b ∣ lcm-ℕ a b
b-divides-lcm a b = n∣m*n a

------------------------------------------------------------------------
-- N-9: Capstone — slice A status.
--
-- After this slice:
--
--   * `Wedge a b` — modulo as a structural decomposition record.
--   * `EEATrace a b g` — the EEA recursion as a data type; properties
--     prove via structural induction.
--   * `compute-trace` — Acc-encapsulated trace construction.
--   * `gcd-ℕ` — extract from trace.
--   * `gcd-divides-left`, `gcd-divides-right` — via trace induction.
--   * `lcm-ℕ` — loose-bound (a * b) version.
--   * `a-divides-lcm`, `b-divides-lcm` — for the loose lcm.
--
-- The trace+wedge approach:
--   - Acc usage is hidden in `compute-trace-acc`.
--   - Downstream property proofs are pure structural induction on
--     EEATrace constructors.
--   - The Wedge's `wedge-eq` field carries the reconstruction equation
--     that the property proofs use directly.
--
-- Deferred follow-ons:
--
--   * **Tight lcm via gcd-quotient**: `lcm-tight a b = a * b / gcd-ℕ a b`.
--     Requires NonZero handling for gcd-ℕ (gcd-ℕ a b > 0 when at
--     least one of a, b > 0). Plus stdlib's truncated-division
--     divisibility properties.
--
--   * **Bezout coefficients** as a structural fold on EEATrace:
--     produce (s, t) with explicit reconstruction. Each step
--     constructor's `quotient` data contributes to the fold.
--
--   * **HasOrder-compose-commute-lcm**: extend
--     Substrate.Category.Coalgebra.StructuralGCD to use lcm-ℕ.
--     With the LOOSE lcm = a * b, this is already what
--     HasOrder-compose-commute provides — the slice would just
--     rename for clarity. The TIGHT lcm version is the substantive
--     follow-on.
--
--   * **Slice B**: F₂[x] polynomial EEA, opening the dual-code arc.
------------------------------------------------------------------------
