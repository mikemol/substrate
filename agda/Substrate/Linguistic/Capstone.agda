------------------------------------------------------------------------
-- Substrate.Linguistic.Capstone
--
-- C10 of the Categorical Linguistics Classification arc per
-- [[project-language-as-free-construction-classification]].
--
-- Capstone slice (file-per-lemma decomposition):
--
--   Capstone.CrossTable   — 6×6 = 36 pairwise RosettaEntry table
--   Capstone.SmokeTests   — 6 refl-cases verifying classification
--   Capstone.Worked       — 5 worked Rosetta entries
--
-- After C1-C10 the substrate has a substrate-native, mechanically-
-- generated classification of languages by free-construction.
-- Downstream consumers can iterate over `full-cross-table`, dispatch
-- on the 6-witness lattice, and extend with new cells.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Linguistic.Capstone where

-- Re-export C1 (parent primitive) + the six witness modules + the
-- classification/Rosetta machinery so consumers see the whole arc.


-- File-per-lemma capstone submodules.