------------------------------------------------------------------------
-- Substrate.WitnessTower.Wedge.Action
--
-- TIER 2 — the structural bridge: the WitnessTower's inductive ACTION
-- (Enumerate.insert-at) read AS a wedge `recon`, so the rung step is a
-- genuine wedge, not merely its count-shadow (Wedge.Factoradic).
--
-- THE INSIGHT REALIZED.  A rung-(n+1) perm τ : Perm (suc n) decomposes,
-- against the rung below, as
--   τ = insert-at p σ = p ∷ map (punchIn p) σ
-- for a base σ : Perm n and an insertion position p : Fin (suc n).  Read
-- as a wedge `a ≡ recon q b r`:
--   a = τ        the rung-(n+1) perm           (the dividend)
--   b = σ        the rung-n perm below it       (the divisor)
--   q = suc n    the insertion arity = [S_{n+1}:S_n] (the factoradic digit)
--   r = p        the Lehmer digit / insertion slot   (the REMAINDER)
-- and `recon (suc n) σ p = insert-at p σ` — so the wedge's `recon` IS the
-- inductive action, and its REMAINDER is the action's free datum (the
-- chosen slot).  "The inductive action as structure" = this identification.
--
-- WHY A PER-RUNG FAMILY, NOT A SINGLE DivStr (the obstruction, surfaced).
-- Algebra.Wedge.DivStr.recon : ℕ → C → C → C is NON-DEPENDENT in the
-- quotient q and uses ONE un-indexed carrier C.  But the action's remainder
-- is a `Fin (suc n)` and its base a `Perm n` — both indexed by the SAME n,
-- a link the un-indexed C cannot express, and which a non-dependent recon
-- cannot recover (it can manufacture no `Fin q`).  Collapsing into a single
-- carrier (e.g. Σ ℕ Perm) forces matching two independently-packed nat
-- indices, dragging in decidable equality + transport and an off-diagonal
-- default the wedge never exercises — impurity for no structural gain.
-- The clean green form is the per-rung wedge below: at each rung the
-- indices are FIXED by the parameter n, so `recon = insert-at` holds by
-- refl with no transport.  This is the honest shape of the bridge.
--
-- Zero postulates, zero holes, --safe --without-K.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Wedge.Action where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Vec using (Vec; []; _∷_; map)
open import Substrate.Foundation.Eq using (_≡_; refl; sym)

open import Substrate.WitnessTower.Enumerate using (Perm; insert-at)

------------------------------------------------------------------------
-- 1. The per-rung reconstruction = the inductive action.  At rung n→(n+1)
--    the carrier-below is Perm n, the remainder is a position Fin (suc n),
--    and recon re-performs the witnessing-insertion move.
------------------------------------------------------------------------

-- recon at rung n: q copies of the base glued at slot r.  Here, because the
-- division is EXACT with q = suc n (Factoradic.tower-quotient), the q copies
-- are precisely the (suc n) insertion slots, and the actual reconstruction
-- of a SINGLE perm needs only its own slot r — the wedge's remainder.
reconₙ : (n : ℕ) → Perm n → Fin (suc n) → Perm (suc n)
reconₙ n σ p = insert-at p σ

-- THE IDENTIFICATION: recon IS insert-at, definitionally.
recon-is-insert-at :
  (n : ℕ) (σ : Perm n) (p : Fin (suc n)) → reconₙ n σ p ≡ insert-at p σ
recon-is-insert-at n σ p = refl

------------------------------------------------------------------------
-- 2. The per-rung Wedge.  A rung-(n+1) perm τ that is `insert-at p σ`
--    wedges against its base σ with quotient (suc n) and remainder p, the
--    witness being refl (recon definitionally returns insert-at p σ = τ).
------------------------------------------------------------------------

-- the per-rung wedge record: a is the dividend perm, b = σ the divisor
-- below, quot the arity, rem the slot, and the witness a ≡ recon b rem.
record StepWedge (n : ℕ) (a : Perm (suc n)) (b : Perm n) : Set where
  field
    quot     : ℕ                       -- the insertion arity (= suc n)
    rem      : Fin (suc n)             -- the Lehmer digit / insertion slot
    wedge-eq : a ≡ reconₙ n b rem      -- a is reconstructed from b at slot rem

open StepWedge public

-- EVERY witnessing-insertion result wedges against its base: the canonical
-- step wedge, witness by refl.  This is the rung step founded as a wedge.
step-wedge :
  (n : ℕ) (σ : Perm n) (p : Fin (suc n)) → StepWedge n (insert-at p σ) σ
step-wedge n σ p = record { quot = suc n ; rem = p ; wedge-eq = refl }

------------------------------------------------------------------------
-- 3. The wedge reads (projections), matching Algebra.Wedge's three.
------------------------------------------------------------------------

-- FORGETFUL: evaluate the witness back to the dividend perm.
forgetStep : {n : ℕ} {a : Perm (suc n)} {b : Perm n} → StepWedge n a b → Perm (suc n)
forgetStep {n} {b = b} w = reconₙ n b (rem w)

forgetStep-correct :
  {n : ℕ} {a : Perm (suc n)} {b : Perm n}
  (w : StepWedge n a b) → forgetStep w ≡ a
forgetStep-correct w = sym (wedge-eq w)

-- PRESENTED: the remainder = the cell = the insertion slot.  Its kernel is
-- "same insertion slot" — the gauge datum of the inductive action.
cellStep : {n : ℕ} {a : Perm (suc n)} {b : Perm n} → StepWedge n a b → Fin (suc n)
cellStep w = rem w

-- the slot read of the canonical step wedge is the position we inserted at.
cellStep-canonical :
  (n : ℕ) (σ : Perm n) (p : Fin (suc n)) → cellStep (step-wedge n σ p) ≡ p
cellStep-canonical n σ p = refl

------------------------------------------------------------------------
-- 4. The arity read = the factoradic digit, agreeing with Factoradic.
------------------------------------------------------------------------

quotStep-is-suc :
  (n : ℕ) (σ : Perm n) (p : Fin (suc n)) → quot (step-wedge n σ p) ≡ suc n
quotStep-is-suc n σ p = refl

------------------------------------------------------------------------
-- 5. Round trip on the worked seam (rung 0→1).  The empty perm inserted at
--    its only slot gives the unique perm of Fin 1; the wedge recovers it.
------------------------------------------------------------------------

base-step : StepWedge 0 (insert-at zero []) []
base-step = step-wedge 0 [] zero

base-step-forget : forgetStep base-step ≡ (zero ∷ [])
base-step-forget = refl
