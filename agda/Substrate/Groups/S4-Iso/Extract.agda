------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Extract
--
-- extract-s-from, extract-s, and perm-to-compositional (backward
-- direction of the iso).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Extract where

open import Substrate.Axes.Axis using (Axis; C; S; W)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
open import Substrate.Groups.Z2.A
open import Substrate.Groups.Z3.A
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Groups.Symmetric.Permutation Axis
open import Substrate.Groups.SemidirectProduct.V
open import Substrate.Groups.SemidirectProduct.S
open import Substrate.Foundation.Product using (_,_)

------------------------------------------------------------------------
-- Read off S₃ element from the action on (C, S) of a Stab(D) permutation.
------------------------------------------------------------------------

extract-s-from : Axis → Axis → S₃.Carrier
extract-s-from C S = ([] , [])                                -- identity
extract-s-from S W = (a₃ ∷ [] , [])                         -- rotate (CSW)
extract-s-from W C = (a₃ ∷ a₃ ∷ [] , [])                  -- rotate² (CWS)
extract-s-from S C = ([] , a₂ ∷ [])                         -- swap CS
extract-s-from W S = (a₃ ∷ [] , a₂ ∷ [])                  -- swap CW
extract-s-from C W = (a₃ ∷ a₃ ∷ [] , a₂ ∷ [])           -- swap SW
extract-s-from _ _ = ([] , [])                                -- impossible

extract-s : Permutation → S₃.Carrier
extract-s s = extract-s-from (apply s C) (apply s S)

perm-to-compositional : Permutation → S4C.Carrier
perm-to-compositional σ = (v-for σ , extract-s (s-for σ))
