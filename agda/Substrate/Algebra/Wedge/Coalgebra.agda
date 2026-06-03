------------------------------------------------------------------------
-- Substrate.Algebra.Wedge.Coalgebra
--
-- CONSTRUCTIVE COINDUCTION VIA THE WEDGE — no Agda `coinductive`. The wedge
-- has two directions: `recon` BUILDS (the inductive Free term, `Trace`);
-- `divide` UNFOLDS (the coalgebra). We did need the wedge to make this
-- possible: the residue (remainder) IS the coalgebra's next state.
--
-- Coinduction is then done as a BASTARDIZED SEQUITUR over an SPPF (per the
-- user): maintain a shared forest of residues; at each wedge step,
--   * if the residue is ALREADY constructible as a path through the SPPF,
--     discard it and CLOSE THE CYCLE (the coinductive loop is found);
--   * otherwise ADD it to the SPPF and continue.
-- The infinite object is never materialized — it is a FINITE cyclic graph,
-- built by finite wedge iterations. For the linear (continued-fraction)
-- unfold the SPPF specializes to the set of residues seen, and "already a
-- path" = "this residue already occurs" (decidable carrier equality, `eq?`).
-- The full SPPF (sharing across BRANCHES) generalizes this to branching
-- unfolds; the linear list is the one-child case.
--
-- READING THE OUTCOME (and the mathematics it lands on):
--   * halt  — the unfold reaches `z`: terminating CF = RATIONAL.
--   * loop  — a residue recurs: eventually-periodic CF = a QUADRATIC
--             IRRATIONAL (Lagrange's theorem), captured as a finite lasso.
--   * stop  — fuel exhausted: no cycle found yet (aperiodic so far); only a
--             bounded prefix is constructively observed.
--
-- The dedup decidability `eq?` is exactly the SPPF cycle-test — and it is the
-- same decidability that closes the Cauchy/Dedekind gap (`Located`, from the
-- thread): deciding whether a residue is "already a path" IS deciding
-- apartness. Constructive coinduction and the gap-closer are one requirement.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Wedge.Coalgebra where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Bool using (Bool; true; false)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Negation using (Dec; yes; no)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Wedge using (DivStr; C; z; Wedge; quot; rem)

------------------------------------------------------------------------
-- 1. The wedge as a coalgebra: `divide` (the unfold) + decidable residue
--    equality (the SPPF cycle-test).
------------------------------------------------------------------------

record WedgeCoalg (D : DivStr) : Set where
  field
    divide : (a b : C D) → Wedge D a b      -- the unfold step (dual to recon)
    eq?    : (x y : C D) → Dec (x ≡ y)       -- "already a path?" — the dedup test

open WedgeCoalg public

------------------------------------------------------------------------
-- 2. The SPPF (linear specialization): membership in the residues seen.
------------------------------------------------------------------------

seen? : {D : DivStr} (co : WedgeCoalg D) → C D → List (C D) → Bool
seen? co x []       = false
seen? co x (y ∷ ys) with eq? co x y
... | yes _ = true
... | no  _ = seen? co x ys

------------------------------------------------------------------------
-- 3. The outcome of an unfold.
------------------------------------------------------------------------

data Unfold : Set where
  halt : Unfold   -- reached z         (rational)
  loop : Unfold   -- residue recurred  (eventually periodic = quadratic irrational)
  stop : Unfold   -- fuel exhausted    (no cycle found yet)

------------------------------------------------------------------------
-- 4. The bastardized Sequitur: unfold the wedge, dedup residues against the
--    SPPF, close the cycle on recurrence. Finite — recursion is on the fuel.
--    Returns the partial quotients emitted (the CF prefix) + why it stopped.
------------------------------------------------------------------------

run : {D : DivStr} (co : WedgeCoalg D) → ℕ → List (C D) → (a b : C D) →
      List ℕ × Unfold
run     co zero    seen a b = [] , stop
run {D} co (suc f) seen a b with eq? co b (z D)
... | yes _ = [] , halt
... | no  _ = cont (divide co a b)
  where
    cont : Wedge D a b → List ℕ × Unfold
    cont w with seen? co (rem w) seen
    ... | true  = quot w ∷ [] , loop                 -- residue already a path: close the cycle
    ... | false = let r = run co f (rem w ∷ seen) b (rem w)
                  in quot w ∷ proj₁ r , proj₂ r       -- new residue: extend the SPPF
