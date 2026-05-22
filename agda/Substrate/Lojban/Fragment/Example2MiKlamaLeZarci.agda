------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Example2MiKlamaLeZarci
--
-- "mi klama le zarci" — I go to the market.
-- 5-place selbri klama (x₁ goes to x₂ from x₃ via x₄ using x₅);
-- unfilled slots take zo'e.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Example2MiKlamaLeZarci where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (klama)
open import Substrate.Lojban.Bridi using (Bridi; make-bridi; interpret)
open import Substrate.Lojban.Fragment.Carriers
  using (Sumti; mi; zo-e; le-zarci; Sem; fact; gismu-to-selbri)

example-mi-klama-le-zarci : Bridi 5 Sumti Sem
example-mi-klama-le-zarci =
  make-bridi (gismu-to-selbri klama)
             (mi ∷ le-zarci ∷ zo-e ∷ zo-e ∷ zo-e ∷ [])

example-2-interp :
  interpret example-mi-klama-le-zarci
    ≡ fact klama (mi ∷ le-zarci ∷ zo-e ∷ zo-e ∷ zo-e ∷ [])
example-2-interp = refl
