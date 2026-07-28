{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- FUSepQCR — ⟡FU-sep-Q-CR: the CAPSTONE. Newman's lemma — a TERMINATING and
-- LOCALLY-CONFLUENT rewrite system is CONFLUENT (Church-Rosser). Assembles the
-- three tower ingredients:
--   • TERMINATION  — Acc on the reduction step (halts→trace's driver, ADD 104).
--   • LOCAL DIAMOND — one-step peaks converge (the braided diamond, ADD 107).
--   • (the functorial/hexagon coherence, ADD 108, is what makes the local
--      diamonds TILE — it is why the induction closes.)
--
-- ⟡H0 (CORRECTED 2026-07-05, Ⓒ.closure): this module ORIGINALLY re-derived Newman
-- honestly on Acc, under the belief "the substrate has NO Newman / Church-Rosser /
-- reflexive-transitive closure — a GENUINE gap (not a re-derivation)." That belief
-- is now STALE: the same result was upstreamed, independently, as the relation-
-- generic Substrate.Foundation.RewriteConfluence (whose OWN header verified thrice
-- that no prior closure existed — the two were built in parallel, neither aware of
-- the other). Rather than maintain the identical diamond-tiling proof in two
-- places, `module Newman` now RE-EXPORTS the center: FUSep's Newman IS Foundation's
-- Newman. The parameterized `(_⇒_)` interface is preserved verbatim, so the sole
-- dependent (FUSepQReduce) opens it unchanged.
------------------------------------------------------------------------

module Substrate.FUSep.FUSepQCR where

-- The relation-generic Newman / Church-Rosser center, abstracted over the step
-- `_⇒_` and its carrier so the concrete SKI system slots in (the ⟡H0 requirement)
-- — now by INSTANTIATING Foundation.RewriteConfluence rather than re-deriving it.
module Newman
  {Tm : Set}
  (_⇒_ : Tm → Tm → Set)                              -- the one-step reduction
  where
  open import Substrate.Foundation.RewriteConfluence _⇒_
    using (_⇒*_; done; _◅_; _++*_; Converge; WCR; CR; SN; newman)
