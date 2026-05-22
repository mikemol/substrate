------------------------------------------------------------------------
-- Substrate.Lojban.Fragment.Example1MiNelciDo
--
-- "mi nelci do" — I like you.
-- 2-place selbri nelci (x₁ likes x₂); arguments (mi, do-pn).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.Fragment.Example1MiNelciDo where

open import Substrate.Foundation.Vec using ([]; _∷_)
open import Substrate.Foundation.Eq using (_≡_; refl)

open import Substrate.Lojban.Gismu using (nelci)
open import Substrate.Lojban.Bridi using (Bridi; make-bridi; interpret)
open import Substrate.Lojban.Fragment.Carriers
  using (Sumti; mi; do-pn; Sem; fact; gismu-to-selbri)

example-mi-nelci-do : Bridi 2 Sumti Sem
example-mi-nelci-do = make-bridi (gismu-to-selbri nelci) (mi ∷ do-pn ∷ [])

example-1-interp :
  interpret example-mi-nelci-do ≡ fact nelci (mi ∷ do-pn ∷ [])
example-1-interp = refl
