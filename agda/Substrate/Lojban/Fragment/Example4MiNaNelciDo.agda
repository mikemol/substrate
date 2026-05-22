------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Example4MiNaNelciDo
--
-- "mi na nelci do" — I do not like you.
-- Demonstrates NA negation as a cmavo wrapper.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Example4MiNaNelciDo where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (nelci)
open import Substrate.Lojban.Bridi using (Bridi; make-bridi; interpret)
open import Substrate.Lojban.Cmavo using (apply-cmavo)
open import Substrate.Lojban.Fragment.Carriers
  using (Sumti; mi; do-pn; Sem; fact; na-of; gismu-to-selbri; NA)

example-mi-na-nelci-do : Bridi 2 Sumti Sem
example-mi-na-nelci-do =
  apply-cmavo NA
    (make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ []))

example-4-interp :
  interpret example-mi-na-nelci-do
    ≡ na-of (fact nelci (mi ∷ do-pn ∷ []))
example-4-interp = refl
