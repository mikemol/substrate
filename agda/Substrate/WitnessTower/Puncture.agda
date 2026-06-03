------------------------------------------------------------------------
-- Substrate.WitnessTower.Puncture
--
-- BUILD (not assert): the witnessing step PUNCTURES the simplex of the
-- higher rung — the witness occupies one cell, the simplex it witnesses
-- occupies the remaining cells.
--
-- This discharges the §8(b) open seam ("∷ lifts a simplicial dimension")
-- of the witness-tower dossier — using machinery already in the tree:
-- the punctured-finite-set bijection Fin (suc n) ∖ {w} ≅ Fin n
-- (Foundation.Fin.Punctured, built earlier this session).
--
-- Cell-counting. A rung-k simplex has k+1 cells (vertices), indexed by
-- Fin (suc k). The witnessing step makes a rung-(k+1) simplex with k+2
-- cells, indexed by Fin (suc (suc k)). Choosing the witness = choosing
-- one cell w : Fin (suc (suc k)) to PUNCTURE OUT; the remaining k+1 cells
-- are exactly the rung-k simplex, embedded by `punchIn w`:
--
--   Fin (suc (suc k))  =  {w}  ⊎  punchIn w (Fin (suc k))
--   ╰─ rung-(k+1) cells    ╰witness  ╰── rung-k simplex (the witnessed) ──╯
--
-- "Lift a dimension" IS this puncture: k+1 cells → k+2 cells, the extra
-- cell being the witness, the rest being the witnessed rung below — a
-- partition, proved by the punctured round-trips.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Puncture where

open import Substrate.Foundation.Nat using (ℕ; suc)
open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Negation using (¬_)
open import Substrate.Foundation.Eq using (_≡_)
open import Substrate.Foundation.Fin.Punctured
  using (punchIn; punchIn-≢; punchOut; punchOut-punchIn; punchIn-punchOut)

------------------------------------------------------------------------
-- 1. Cell indices of a rung. A rung-k simplex has k+1 cells.
------------------------------------------------------------------------

Cells : ℕ → Set
Cells k = Fin (suc k)

------------------------------------------------------------------------
-- 2. The puncture of a witnessing step from rung k to rung (k+1).
--
-- A witness is a choice of cell in the HIGHER rung (k+2 cells):
--   witness-cell : Cells (suc k)            -- = Fin (suc (suc k))
-- The witnessed simplex (rung k, k+1 cells) embeds into the higher rung
-- by punching at the witness — every witnessed cell lands in a cell that
-- is NOT the witness:
--   embed-witnessed : Cells k → Cells (suc k)
------------------------------------------------------------------------

module _ {k : ℕ} (witness-cell : Cells (suc k)) where

  -- the witnessed rung-k cells, embedded into the higher rung, skipping
  -- the witness cell.
  embed-witnessed : Cells k → Cells (suc k)
  embed-witnessed = punchIn witness-cell

  -- no witnessed cell coincides with the witness: the witness occupies a
  -- cell DISJOINT from the witnessed simplex. (The "one cell vs the
  -- remainder" disjointness.)
  witnessed-avoids-witness :
    (c : Cells k) → ¬ (embed-witnessed c ≡ witness-cell)
  witnessed-avoids-witness = punchIn-≢ witness-cell

  -- recover a witnessed cell from a higher-rung cell that is not the
  -- witness: the remainder IS rung k.
  recover-witnessed : {c : Cells (suc k)} → ¬ (c ≡ witness-cell) → Cells k
  recover-witnessed {c} c≢w = punchOut {k = witness-cell} {i = c} c≢w

  -- round trip 1: embedding then recovering returns the original
  -- witnessed cell (the witnessed simplex is faithfully the remainder).
  recover-embed :
    (c : Cells k) →
    recover-witnessed (witnessed-avoids-witness c) ≡ c
  recover-embed = punchOut-punchIn witness-cell

  -- round trip 2: any non-witness cell of the higher rung is the
  -- embedding of a witnessed cell — so the higher rung's cells partition
  -- exactly as {witness} ⊎ embed-witnessed (rung k).
  embed-recover :
    {c : Cells (suc k)} (c≢w : ¬ (c ≡ witness-cell)) →
    embed-witnessed (recover-witnessed c≢w) ≡ c
  embed-recover {c} c≢w = punchIn-punchOut {k = witness-cell} {i = c} c≢w
