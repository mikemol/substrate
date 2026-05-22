------------------------------------------------------------------------
-- Substrate.Pipeline.Manifest
--
-- Pipeline arc manifest. Mirrors Substrate.Groups.Manifest in shape.
--
-- Currently wired:
--   Composition  — pipeline composition primitive
--   Merger       — pipeline merging primitive
--   Sequent      — sequent-calculus pipeline primitives (exchange, …)
--   Examples     — parametric brick examples (Char/Counts/Window/…
--                  supplied at use site)
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Pipeline.Manifest where

import Substrate.Pipeline.Composition
import Substrate.Pipeline.Merger
import Substrate.Pipeline.Sequent
import Substrate.Pipeline.Examples
