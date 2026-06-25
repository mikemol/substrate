------------------------------------------------------------------------
-- Substrate.Algebra.Wedge
--
-- THE GENERIC WEDGE — the keystone operator. A wedge of `a` against `b`
-- is the triple (quotient, remainder, witness : a = recon q b r): "a built
-- as q·b, plus a remainder r." Over a carrier that supplies only a
-- reconstruction `recon : C → C → C → C` ("q·b, then r"), where the quotient q
-- is itself a CARRIER REPRESENTATIVE (an element of C), not a bare ℕ count — so
-- a POLYNOMIAL quotient (F₂[x] division) is an instance, not a parallel
-- construction, and a Bridge's `translate` maps the quotient like any element.
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
-- NO LONGER scoped out: the quotient is now a CARRIER REPRESENTATIVE (recon's
--   first argument is a `C`, was a baked ℕ count). Ring carriers (ℕ, ℤ, F₂[x])
--   use their own element as the quotient; the old ℕ count was a FROZEN COORDINATE
--   ([[feedback_coordinate_to_geometry]]). Count carriers (free-monoid List, the
--   product slices) keep a count via their representative; their mature home is
--   the grade index of `GradedDivStr`, of which the flat form is the shadow.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _*_)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans; cong)
import Substrate.Algebra.Nat.GCD.Wedge as N
import Substrate.Algebra.Nat.GCD.EEATrace as NT

------------------------------------------------------------------------
-- 1. The carrier interface: what a type needs to host a wedge.
------------------------------------------------------------------------

record DivStr : Set₁ where
  field
    C     : Set
    z     : C                 -- the terminal divisor (the recursion stops here)
    recon : C → C → C → C     -- recon q b r = "q·b, then the remainder r"; the quotient q
                              -- is a CARRIER REPRESENTATIVE (an element of C), not a count.

open DivStr public

------------------------------------------------------------------------
-- 2. The generic wedge: the triple (quotient, remainder, witness).
------------------------------------------------------------------------

record Wedge (D : DivStr) (a b : C D) : Set where      -- ⟦shape:478f66a6 quot,rem,wedge-eq⟧
  field
    quot     : C D
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

-- THE GENERIC FOLD = the Trace recursor, named so targets are swappable (the
-- carrier-uniform lift of Algebra.Nat.GCD.Fold.eea-fold: any target T over the
-- trace is computed structurally). gcd / Bézout / mod are its instances; the ℕ
-- EEATrace and the F₂[x] PolyEEATrace both fold through it once they are traces.
trace-fold :
  {D : DivStr} {T : C D → C D → C D → Set}
  (base-interp : (a : C D) → T a (z D) a)
  (step-interp : {a g : C D} (b : C D) (w : Wedge D a b) → T b (rem w) g → T a b g) →
  {a b g : C D} → Trace D a b g → T a b g
trace-fold bi si (done a)      = bi a
trace-fold bi si (more b w tr) = si b w (trace-fold bi si tr)

-- the forgetful fold IS collapse: returning the gcd index g.
collapse-fold : {D : DivStr} {a b g : C D} → Trace D a b g → C D
collapse-fold {D} = trace-fold {D} {T = λ _ _ _ → C D} (λ a → a) (λ _ _ rec → rec)

collapse-fold≡collapse : {D : DivStr} {a b g : C D} (t : Trace D a b g) →
                         collapse-fold t ≡ collapse t
collapse-fold≡collapse (done a)      = refl
collapse-fold≡collapse (more b w tr) = collapse-fold≡collapse tr

------------------------------------------------------------------------
-- THE UNIVERSAL PROPERTY of the generic wedge-trace fold (Ⓤ.trace-fold-unique):
-- `Trace D` is the INITIAL ALGEBRA of the (done/more) functor; `trace-fold bi
-- si` is the UNIQUE algebra morphism out — any `h` agreeing with `bi` on `done`
-- and `si` on `more` IS it. The generic PARENT the per-trace uniqueness lemmas
-- instantiate: `Algebra.Nat.GCD.Fold.eea-fold-unique` (and the polynomial
-- variant) are this at a specific `D`. Same idiom as the family
-- (Category.UniversalProperty.Eval.foldUPTerm-unique, FreeMonoid.extend-unique);
-- the DUAL of the terminal-coalgebra `R.Trace.Final.ana-unique`.
------------------------------------------------------------------------

trace-fold-unique :
  {D : DivStr} {T : C D → C D → C D → Set}
  (base-interp : (a : C D) → T a (z D) a)
  (step-interp : {a g : C D} (b : C D) (w : Wedge D a b) → T b (rem w) g → T a b g)
  (h : {a b g : C D} → Trace D a b g → T a b g)
  (h-done : (a : C D) → h (done a) ≡ base-interp a)
  (h-more : {a g : C D} (b : C D) (w : Wedge D a b) (tr : Trace D b (rem w) g) →
            h (more b w tr) ≡ step-interp b w (h tr)) →
  {a b g : C D} (t : Trace D a b g) →
  h t ≡ trace-fold {D} {T} base-interp step-interp t
trace-fold-unique bi si h h-done h-more (done a)       = h-done a
trace-fold-unique {D} {T} bi si h h-done h-more {a = a} {g = g} (more b w tr) =
  trans (h-more b w tr)
        (cong (si {a} {g} b w) (trace-fold-unique {D} {T} bi si h h-done h-more tr))

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
