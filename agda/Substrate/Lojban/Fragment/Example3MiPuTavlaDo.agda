------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Example3MiPuTavlaDo
--
-- "mi pu tavla do" — I talked to you.
-- 4-place selbri tavla under past-tense (pu) wrapper.
-- Demonstrates apply-cmavo (PU pu) wrapping a base bridi.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Example3MiPuTavlaDo where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (tavla)
open import Substrate.Lojban.Cmavo using (pu)
open import Substrate.Lojban.Bridi using (Bridi; make-bridi; interpret)
open import Substrate.Lojban.Cmavo using (apply-cmavo)
open import Substrate.Lojban.Fragment.Carriers
  using (Sumti; mi; do-pn; zo-e; Sem; fact; pu-of; gismu-to-selbri; PU)

example-mi-pu-tavla-do : Bridi 4 Sumti Sem
example-mi-pu-tavla-do =
  apply-cmavo (PU pu)
    (make-bridi (gismu-to-selbri tavla)
                (mi ∷ do-pn ∷ zo-e ∷ zo-e ∷ []))

example-3-interp :
  interpret example-mi-pu-tavla-do
    ≡ pu-of (fact tavla (mi ∷ do-pn ∷ zo-e ∷ zo-e ∷ []))
example-3-interp = refl
