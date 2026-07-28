------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical
--
-- act-on-canonical: dispatch on (Z₃ canonical, Z₂ canonical, V₄ ctor).
-- The 6 canonical S₃ elements × 4 V₄ elements = 24-entry Cayley table
-- materialised as explicit clauses (plus a fallback for non-canonical
-- inputs, which is unreachable when called via act).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical where

import Substrate.Groups.V4.Operations as V4
open import Substrate.Groups.V4.Bijection using (V₄; e; α; β; γ)
import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
import Substrate.Groups.Coxeter.Cyclic.Base 2 as Z₃-Base
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)

act-on-canonical : Word Z₃-Base.Gen → Word Z₂-Base.Gen → V₄ → V₄
-- ([], []) = identity:
act-on-canonical [] [] v = v
-- ([a], []) = rotation (αβγ):
act-on-canonical (Z₃-Base.a ∷ []) [] e = e
act-on-canonical (Z₃-Base.a ∷ []) [] α = β
act-on-canonical (Z₃-Base.a ∷ []) [] β = γ
act-on-canonical (Z₃-Base.a ∷ []) [] γ = α
-- ([a,a], []) = rotation² (αγβ):
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) [] e = e
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) [] α = γ
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) [] β = α
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) [] γ = β
-- ([], [a]) = swap αβ (γ fixed):
act-on-canonical [] (Z₂-Base.a ∷ []) e = e
act-on-canonical [] (Z₂-Base.a ∷ []) α = β
act-on-canonical [] (Z₂-Base.a ∷ []) β = α
act-on-canonical [] (Z₂-Base.a ∷ []) γ = γ
-- ([a], [a]) = rotate ∘ swap-αβ = swap αγ (β fixed):
act-on-canonical (Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) e = e
act-on-canonical (Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) α = γ
act-on-canonical (Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) β = β
act-on-canonical (Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) γ = α
-- ([a,a], [a]) = rotate² ∘ swap-αβ = swap βγ (α fixed):
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) e = e
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) α = α
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) β = γ
act-on-canonical (Z₃-Base.a ∷ Z₃-Base.a ∷ []) (Z₂-Base.a ∷ []) γ = β
-- Fallback (unreachable on canonical S₃ inputs).
act-on-canonical _ _ v = v
