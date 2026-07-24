{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Algebra.F2.AES.KAT.RoundFin — the FINAL round pin (INDEPENDENT).
--
-- One final round (no MixColumns) on the concrete penultimate state S9 →
-- the ciphertext state Sct:   final-round K10 S9 ≡ Sct   (by refl).
--
-- ⚑ ⟡cap128-aes-pipeline: this is Round 10, isolated in its OWN module exactly like
-- KAT.Round1…Round9. It was the ONE round left computed IN-LINE inside KAT.Full — a
-- ~108 MB `refl` (the concrete final-round WHNF). Pinning it here means `KAT.Full`
-- IMPORTS it as a pre-checked handle instead of forcing it, so Full's peak drops the
-- full round's worth (228 → under the 128 MB per-module cap). Same staging the KAT
-- already applies to every other round; this completes it.
--
-- --safe --without-K; no postulates, no holes.
------------------------------------------------------------------------

module Substrate.Algebra.F2.AES.KAT.RoundFin where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.F2.AES.Round using (final-round)
open import Substrate.Algebra.F2.AES.KAT.Trace

opaque
  unfolding final-round
  fin : final-round K10 S9 ≡ Sct
  fin = refl
