------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4.Dispatch
--
-- Canonical-form action dispatch: act-on-canonical and act (full
-- action with pre-normalisation).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.Dispatch where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Foundation.Product using (_,_)

------------------------------------------------------------------------
-- act-on-canonical: dispatch on (Z₃ canonical, Z₂ canonical, V₄ ctor).
------------------------------------------------------------------------

act-on-canonical : Word Z₃.Gen → Word Z₂.Gen → V₄ → V₄
-- ([], []) = identity:
act-on-canonical [] [] v = v
-- ([a], []) = rotation (αβγ):
act-on-canonical (Z₃.a ∷ []) [] e = e
act-on-canonical (Z₃.a ∷ []) [] α = β
act-on-canonical (Z₃.a ∷ []) [] β = γ
act-on-canonical (Z₃.a ∷ []) [] γ = α
-- ([a,a], []) = rotation² (αγβ):
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] e = e
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] α = γ
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] β = α
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] γ = β
-- ([], [a]) = swap αβ (γ fixed):
act-on-canonical [] (Z₂.a ∷ []) e = e
act-on-canonical [] (Z₂.a ∷ []) α = β
act-on-canonical [] (Z₂.a ∷ []) β = α
act-on-canonical [] (Z₂.a ∷ []) γ = γ
-- ([a], [a]) = rotate ∘ swap-αβ = swap αγ (β fixed):
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) e = e
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) α = γ
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) β = β
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) γ = α
-- ([a,a], [a]) = rotate² ∘ swap-αβ = swap βγ (α fixed):
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) e = e
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) α = α
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) β = γ
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) γ = β
-- Fallback (unreachable on canonical S₃ inputs).
act-on-canonical _ _ v = v

------------------------------------------------------------------------
-- Full action, normalising the S₃-pair first.
------------------------------------------------------------------------

act : S₃.Carrier → V₄ → V₄
act (n , h) v = act-on-canonical (Z₃.normalize n) (Z₂.normalize h) v
