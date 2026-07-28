------------------------------------------------------------------------
-- Substrate.WitnessTower.Surjective
--
-- injective ⟹ surjective for the bijective image-vectors on Fin n: every
-- y : Fin n is hit. This is what the Groups.Symmetric record's inverse
-- field needs. Proof reuses the decomposition's "punch out the head" step
-- (decomp-tail IS the smaller injective map), with Fin decidable equality
-- to split on whether y is the head.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.WitnessTower.Surjective where

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.Op
open import Substrate.Foundation.Vec using (lookup; tabulate)
open import Substrate.Foundation.Vec.Properties using (lookup∘tabulate)
open import Substrate.Foundation.Eq using (_≡_; refl; sym; trans)
open import Substrate.Foundation.Negation using (yes; no)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Fin.Punctured using (punchOut)

open import Substrate.WitnessTower.Enumerate using (Perm)
open import Substrate.WitnessTower.IsPermutation using (IsPerm)
open import Substrate.WitnessTower.Decompose
  using (decomp-tail; decomp-tail-perm; tail-≢-head; punchOut-injective)

perm-surjective :
  {n : ℕ} (σ : Perm n) → IsPerm σ → (y : Fin n) → Σ (Fin n) (λ x → lookup σ x ≡ y)
perm-surjective {suc n} σ perm y with y ≟ lookup σ zero
... | yes y≡h = zero , sym y≡h
... | no  y≢h
      with perm-surjective (decomp-tail σ perm) (decomp-tail-perm σ perm)
             (punchOut {k = lookup σ zero} {i = y} y≢h)
...   | x' , dtx'≡y' = suc x' , punchOut-injective (tail-≢-head σ perm x') y≢h pe
        where
          f = λ i → punchOut {k = lookup σ zero} {i = lookup σ (suc i)}
                              (tail-≢-head σ perm i)
          -- lookup (decomp-tail) x' ≡ f x' = punchOut (tail-≢-head … x');
          -- and dtx'≡y' says that equals punchOut y≢h.
          pe : punchOut (tail-≢-head σ perm x') ≡ punchOut {k = lookup σ zero} {i = y} y≢h
          pe = trans (sym (lookup∘tabulate f x')) dtx'≡y'
