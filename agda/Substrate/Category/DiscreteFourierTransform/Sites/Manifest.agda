------------------------------------------------------------------------
-- Substrate.Category.DiscreteFourierTransform.Sites.Manifest
--
-- Aggregates all concrete DFT sites. Currently wired:
--   Zn   — cyclic DFT (CRT + multi-Sylow decompositions).
--   F2n  — Walsh-Hadamard DFT at F₂ⁿ.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.DiscreteFourierTransform.Sites.Manifest where

import Substrate.Category.DiscreteFourierTransform.Sites.Zn
import Substrate.Category.DiscreteFourierTransform.Sites.F2n
