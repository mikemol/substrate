------------------------------------------------------------------------
-- Substrate.Lojban.PlaceStructure
--
-- L1 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- Costructure shadow #1: `Selbri n` as the n-ary morphism universal-
-- property primitive for Lojban predicates. A selbri with n place-
-- structure slots is precisely a typed n-ary morphism
--
--   apply : Vec Sumti n → Sem
--
-- where Sumti is the argument carrier and Sem is the semantic codomain
-- (a bridi or other interpretation target). Compare
-- Substrate.Category.Morphism, whose Preserves predicate is the unary
-- analogue; this primitive captures the arity-indexed extension.
--
-- Per [[feedback-categorical-name-first]]: "n-ary morphism" is the
-- standard categorical name. This module supplies the substrate-level
-- realisation for the linguistic instantiation.
--
-- Per [[feedback-grothendieck-coherence-rule]]: the post-composition
-- operation `selbri-postcompose` is provided as the functorial handle.
-- Identity preservation + composition preservation are discharged
-- pointwise here at L1; L7 (Functoriality) lifts them to the full
-- coherence statement.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]: kept
-- parametric in (Sumti, Sem) so the same primitive instantiates for
-- Lojban (Sumti = Lojban-individuals, Sem = Bridi), the eventual
-- Toki Pona side (Sumti = vector basis, Sem = linear-form), and any
-- other downstream consumer.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.PlaceStructure where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Vec using (Vec)
open import Substrate.Foundation.Level using (Level; _⊔_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong)

private
  variable
    ℓA ℓB ℓC ℓD : Level
    n : ℕ

------------------------------------------------------------------------
-- 1. Selbri : the n-ary morphism record.
--
-- A `Selbri n Sumti Sem` is an n-place predicate / relation viewed
-- as a typed n-ary function. The record allows future fields
-- (preservation tags, arity metadata) without breaking the surface.
------------------------------------------------------------------------

record Selbri
  (n : ℕ) (Sumti : Set ℓA) (Sem : Set ℓB) : Set (ℓA ⊔ ℓB) where
  constructor mkSelbri
  field
    apply : Vec Sumti n → Sem

open Selbri public

------------------------------------------------------------------------
-- 2. Post-composition: functorial in the codomain.
--
-- If S : Selbri n Sumti Sem and h : Sem → Sem', composing the meaning
-- function yields a new selbri at the new codomain. This is the
-- functoriality handle that L7 lifts.
------------------------------------------------------------------------

selbri-postcompose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} →
  (Sem → Sem') → Selbri n Sumti Sem → Selbri n Sumti Sem'
selbri-postcompose h S = mkSelbri (λ args → h (apply S args))

------------------------------------------------------------------------
-- 3. Identity preservation (pointwise).
--
-- Post-composing with the identity on Sem reproduces the original
-- apply on every argument vector.
------------------------------------------------------------------------

selbri-postcompose-id :
  {Sumti : Set ℓA} {Sem : Set ℓB} →
  (S : Selbri n Sumti Sem) →
  (args : Vec Sumti n) →
  apply (selbri-postcompose (λ x → x) S) args ≡ apply S args
selbri-postcompose-id _ _ = refl

------------------------------------------------------------------------
-- 4. Composition preservation (pointwise).
--
-- Post-composing with (g ∘ f) factors through post-composing with f
-- then with g. Together with §3 this is the functor-law obligation
-- that L7 discharges at the coherent level.
------------------------------------------------------------------------

selbri-postcompose-compose :
  {Sumti : Set ℓA} {Sem : Set ℓB} {Sem' : Set ℓC} {Sem'' : Set ℓD} →
  (f : Sem → Sem') (g : Sem' → Sem'') →
  (S : Selbri n Sumti Sem) →
  (args : Vec Sumti n) →
  apply (selbri-postcompose (λ x → g (f x)) S) args
    ≡ apply (selbri-postcompose g (selbri-postcompose f S)) args
selbri-postcompose-compose _ _ _ _ = refl

------------------------------------------------------------------------
-- 5. Sumti-substitution (pre-composition on the argument vector).
--
-- Pre-composing an n-ary substitution s : Vec Sumti' n → Vec Sumti n
-- on the argument side yields a new selbri at the new Sumti carrier.
-- Useful for L6 (cmavo wrappers that rearrange argument vectors)
-- and for the eventual Sumti-renaming arc.
------------------------------------------------------------------------

selbri-precompose :
  {Sumti Sumti' : Set ℓA} {Sem : Set ℓB} →
  (Vec Sumti' n → Vec Sumti n) →
  Selbri n Sumti Sem → Selbri n Sumti' Sem
selbri-precompose s S = mkSelbri (λ args → apply S (s args))
