------------------------------------------------------------------------
-- Substrate.Codes.Manifest
--
-- Codes arc manifest. Aggregates the concrete error-correcting-code
-- modules so they're reachable through one import.
--
-- Currently wired:
--   Hamming.H-7-4-3   — Hamming (7, 4) code at distance 3
--   Hamming.H-8-4-4   — extended Hamming (8, 4) code at distance 4
--   ReedMuller.RM-1-3 — Reed-Muller RM(1, 3)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Codes.Manifest where

import Substrate.Codes.Hamming.H-7-4-3
import Substrate.Codes.Hamming.H-8-4-4
import Substrate.Codes.ReedMuller.RM-1-3
