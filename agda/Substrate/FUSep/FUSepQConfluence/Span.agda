------------------------------------------------------------------------
-- Substrate.FUSep.FUSepQConfluence.Span
--
-- Defines: Span, p-recon, pBack, r-recon, rBack, viaP, viaR
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.FUSep.FUSepQConfluence; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.FUSep.FUSepQConfluence.Span where

open import Substrate.Foundation.Nat.Nat
open import Substrate.FUSep.FUSepQSKI    using (atom; app) renaming (Tm-QSKI to Tm-QSKI)
open import Substrate.Foundation.Eq
open import Substrate.FUSep.FUSepQSKI



------------------------------------------------------------------------
-- THE GENUINE CONTENT: the braiding must witness that the two indexes COMMUTE AS
-- REWRITES on the shared bucket — the DIAMOND. A node s with a reduce-edge to r
-- AND a peel-edge to p converges: reducing-then-peeling and peeling-then-reducing
-- reach a COMMON node d. The braiding carries this convergence (Hindley-Rosen:
-- two commuting relations). The residues (backpointers, ADD 106) are what let the
-- reordered path reconstruct — the same witness, walked in the braided order.
------------------------------------------------------------------------

-- a reduce-edge and a peel-edge OUT of the same node s, with their target nodes.
record Span (s : Tm-QSKI) : Set where
  field
    viaR    : Tm-QSKI            -- s reduces to viaR
    viaP    : Tm-QSKI            -- s peels to viaP
    -- the RESIDUES (backpointers) that reconstruct s from each target:
    rBack   : Tm-QSKI            -- reduce backpointer (the kept parent = s itself)
    pBack   : Tm-QSKI            -- peel backpointer (the argument)
    r-recon : s ≡ rBack             -- reduce is lossy: s IS its own backpointer
    p-recon : s ≡ app viaP pBack     -- peel: s = app (function) (argument)
open Span public
