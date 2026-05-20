------------------------------------------------------------------------
-- Eliza.Recorder
--
-- The persistence layer. Aggregates per-session traces into long-lived
-- counters and grammar tables backed by SQLite (in the Python).
--
-- The substrate-honest view: the Recorder is a Database-typed
-- accumulator that observes the Engine's per-turn outputs and updates
-- the relevant tables. Each turn produces:
--
--   * chamber-visits[chamber_to] += 1
--   * edge-traversals[chamber_from][generator] += 1
--   * trigrams[c₁][c₂][c₃] += 1
--   * holonomy-closes / drifts running totals
--
-- Plus per-turn diagnostics inserted into a `turns` event log.
--
-- The skeleton names the contract; the SQLite-specific machinery
-- lives in the Python `Store` class.
------------------------------------------------------------------------

{-# OPTIONS --without-K #-}

module Eliza.Recorder where

open import Eliza.Prelude   using (ℕ; _×_; Bool)
open import Eliza.Alphabets using (Char; Gen; Chamber; Orbit)
open import Eliza.Word      using (Word)

------------------------------------------------------------------------
-- 1. The Database — postulated. In Python: a SQLite connection.
------------------------------------------------------------------------

postulate
  Database : Set

------------------------------------------------------------------------
-- 2. Per-turn event payload. The structural data the Engine produces
-- per char that the Recorder persists.
------------------------------------------------------------------------

record Turn : Set where
  field
    user-char     : Char
    generator     : Gen
    chamber-from  : Chamber
    chamber-to    : Chamber
    holonomy-closes : Bool
    -- continuous-valued fields (fiedler, turbulence, kappa, surprise)
    -- elided in the skeleton; their types are ℝ per Predictor/Holonomy.

------------------------------------------------------------------------
-- 3. The Recorder interface.
------------------------------------------------------------------------

postulate
  open-recorder  : Database → Database
  close-recorder : Database → Database

  start-session  : Database → Database
  end-session    : Database → Database

  record-turn    : Database → Turn → Database

------------------------------------------------------------------------
-- 4. Query interface (read-only aggregate state).
------------------------------------------------------------------------

postulate
  get-visits   : Database → Chamber → ℕ
  get-edge     : Database → Chamber → Gen → ℕ
  get-trigram  : Database → Char → Char → Char → ℕ
  get-holonomy : Database → ℕ × ℕ   -- (closes, drifts)

------------------------------------------------------------------------
-- 5. Monotonicity contract: `record-turn` only ever INCREMENTS
-- counters; never decrements. The substrate's "catalogue thickens
-- forward" principle at runtime.
------------------------------------------------------------------------

postulate
  record-turn-monotone :
    (db : Database) (t : Turn) (x : Chamber) →
    -- get-visits (record-turn db t) x ≥ get-visits db x
    -- (using ≥ on ℕ, omitted for skeleton)
    Set

------------------------------------------------------------------------
-- 6. Cross-session continuity contract: closing and re-opening the
-- database preserves all aggregate state. The Python's SQLite + WAL
-- realises this.
------------------------------------------------------------------------

postulate
  persistence :
    (db : Database) →
    -- For all x, get-visits (open-recorder (close-recorder db)) x
    --          ≡ get-visits db x
    Set
