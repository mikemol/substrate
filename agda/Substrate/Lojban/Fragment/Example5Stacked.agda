------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Example5Stacked
--
-- Stacked cmavo (NA after PU): exhibits the compose-coherence from
-- L7. Applying NA after PU yields the same semantic value as applying
-- their composed wrapper.
--
-- Demonstrates [[feedback-grothendieck-coherence-rule]]: the cmavo
-- algebra's composition lands as a 2-cell witness on the worked-
-- example layer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Example5Stacked where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (nelci)
open import Substrate.Lojban.Cmavo using (pu; _∘-cmavo_)
open import Substrate.Lojban.Bridi using (Bridi; make-bridi; interpret)
open import Substrate.Lojban.Cmavo using (apply-cmavo)
open import Substrate.Lojban.Functoriality using (cmavo-compose-coherent)
open import Substrate.Lojban.Fragment.Carriers
  using (Sumti; mi; do-pn; Sem; fact; pu-of; na-of; gismu-to-selbri; PU; NA)

example-stacked : Bridi 2 Sumti Sem
example-stacked =
  apply-cmavo NA (apply-cmavo (PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ [])))

example-5-interp :
  interpret example-stacked
    ≡ na-of (pu-of (fact nelci (mi ∷ do-pn ∷ [])))
example-5-interp = refl

-- The compose-coherence path (citing L7) gives the same interpretation.
example-stacked-via-compose : Bridi 2 Sumti Sem
example-stacked-via-compose =
  apply-cmavo (NA ∘-cmavo PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))

example-5-coherent :
  interpret example-stacked ≡ interpret example-stacked-via-compose
example-5-coherent =
  cmavo-compose-coherent NA (PU pu)
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))
