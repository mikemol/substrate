------------------------------------------------------------------------
-- Substrate.Pipeline.Manifest
--
-- Pipeline arc manifest. Mirrors Substrate.Groups.Manifest in shape.
--
-- Currently wired:
--   Composition  — pipeline composition primitive
--   Merger       — pipeline merging primitive
--   Sequent      — sequent-calculus pipeline primitives (exchange, …)
--
-- (Substrate.Pipeline.Examples excluded: uses --safe-incompatible
-- postulates.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Manifest where

import Substrate.Pipeline.Composition
import Substrate.Pipeline.Merger
import Substrate.Pipeline.Sequent
-- (Substrate.Pipeline.Examples excluded: uses --safe-incompatible postulates.)
