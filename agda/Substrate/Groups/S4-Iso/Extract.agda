------------------------------------------------------------------------
-- Substrate.Groups.S4-Iso.Extract
--
-- extract-s-from, extract-s, and perm-to-compositional (backward
-- direction of the iso).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.S4-Iso.Extract where

open import Substrate.Axes using (Axis; C; S; W)
import Substrate.Groups.S3 as S₃
import Substrate.Groups.S4-Composed as S4C
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
open import Substrate.Groups.Coxeter.Word using ([]; _∷_)
open import Substrate.Groups.S4 using (Permutation)
open Permutation
open import Substrate.Groups.SemidirectProduct using (v-for; s-for)
open import Substrate.Foundation.Product using (_,_)

------------------------------------------------------------------------
-- Read off S₃ element from the action on (C, S) of a Stab(D) permutation.
------------------------------------------------------------------------

extract-s-from : Axis → Axis → S₃.Carrier
extract-s-from C S = ([] , [])                                -- identity
extract-s-from S W = (Z₃.a ∷ [] , [])                         -- rotate (CSW)
extract-s-from W C = (Z₃.a ∷ Z₃.a ∷ [] , [])                  -- rotate² (CWS)
extract-s-from S C = ([] , Z₂.a ∷ [])                         -- swap CS
extract-s-from W S = (Z₃.a ∷ [] , Z₂.a ∷ [])                  -- swap CW
extract-s-from C W = (Z₃.a ∷ Z₃.a ∷ [] , Z₂.a ∷ [])           -- swap SW
extract-s-from _ _ = ([] , [])                                -- impossible

extract-s : Permutation → S₃.Carrier
extract-s s = extract-s-from (apply s C) (apply s S)

perm-to-compositional : Permutation → S4C.Carrier
perm-to-compositional σ = (v-for σ , extract-s (s-for σ))
