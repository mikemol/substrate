------------------------------------------------------------------------
-- Substrate.Pipeline.Manifest
--
-- Pipeline arc manifest. Mirrors Substrate.Groups.Manifest in shape.
--
-- Currently wired:
--   Composition  — pipeline composition primitive
--   Examples     — worked pipeline examples
--   Merger       — pipeline merging primitive
--
-- (Substrate.Pipeline.Sequent is currently excluded — has a
-- pre-existing build error to be addressed separately.)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Manifest where

import Substrate.Pipeline.Composition
import Substrate.Pipeline.Merger
-- (Substrate.Pipeline.Examples excluded: uses --safe-incompatible postulates.)
-- (Substrate.Pipeline.Sequent excluded: has a pre-existing build error.)
