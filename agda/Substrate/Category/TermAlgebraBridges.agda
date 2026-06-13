------------------------------------------------------------------------
-- Substrate.Category.TermAlgebraBridges
--
-- T23-T28: cross-arc bridges connecting the term-algebra encodings
-- of related morphism categories. These bridges expose the substrate's
-- structural pattern: when one category embeds in another, the term
-- algebras embed compatibly.
--
-- Bridges:
--   T23: StochasticLens.Term → MarkovCategory.Term
--        (every lens lives in a Markov category as a forward+backward
--         pair of kernels)
--   T24: PolyLens.Term → Poly.Term (definitional, since PolyLens = Poly)
--   T25: ConjugateMonad.Term → MarkovCategory.Term (Bayesian updates
--        are Markov kernels)
--   T26: DFT.Term → PontryaginDual.Term (DFT operates on the dual
--        group's characters)
--   T27: CascadedCoalgebra.Term → MarkovCategory.Term (each cascade
--        layer is a Markov kernel)
--   T28: PontryaginDual.Term → Substrate.Groups.Coxeter (cyclic
--        characters as Coxeter words)
--   T29: Wedge.Trace → free-monoid word (the EEA free term's continued-
--        fraction digit word) — CONCRETE (not a stub), via `trace-word`.
--        Reflects the R-arc / division machinery into this diagram.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.TermAlgebraBridges where

open import Substrate.Foundation.Product using (_,_; _×_)

open import Substrate.Probability.MarkovCategory.Term
  using (MarkovTerm; MarkovGen)
  renaming ([] to []ₘ; _∷_ to _∷ₘ_)
open import Substrate.Category.StochasticLens.Term
  using (LensTerm; LensGen; LensTriple)
  renaming ([] to []ₗ; _∷_ to _∷ₗ_)
open import Substrate.Category.Poly.Term
  using (PolyTerm; PolyGen)
  renaming ([] to []ₚ; _∷_ to _∷ₚ_)
open import Substrate.Category.PolyLens.Term using (PolyLensTerm)
open import Substrate.Probability.ConjugateMonad.Term
  using (ConjTerm; ConjGen; ConjState)
  renaming ([] to []ᶜ; _∷_ to _∷ᶜ_)
open import Substrate.Category.DiscreteFourierTransform.Term
  using (DFTTerm; DFTGen; DFTContext)
  renaming ([] to []ᶠ; _∷_ to _∷ᶠ_)
open import Substrate.Category.CascadedCoalgebra.Term
  using (CascadeTerm; CascadeGen; CascadeState)
  renaming ([] to []ᶜᶜ; _∷_ to _∷ᶜᶜ_)
open import Substrate.Algebra.PontryaginDual.Term
  using (CharTerm; CharGen)
open import Substrate.Algebra.Wedge using (DivStr; C; Trace)
open import Substrate.Algebra.Wedge.TraceWord using (trace-word)
open import Substrate.Foundation.List using (List)
open import Substrate.Foundation.Nat using (ℕ)

------------------------------------------------------------------------
-- T23: StochasticLens.Term → MarkovCategory.Term bridge.
--
-- A lens consists of forward and backward Markov kernels; the lens
-- term embeds into MarkovTerm by translating each lens generator
-- into a pair of Markov generators (forward + backward).

-- Stub: the embedding requires the lens's (S, A, B) triple to be
-- decomposed into Markov objects. Concrete instances supply.

------------------------------------------------------------------------
-- T24: PolyLens.Term → Poly.Term (definitional identity).
--
-- PolyLens IS Poly (per Substrate.Category.PolyLens), so PolyLensTerm
-- IS PolyTerm. No translation needed.

bridge-polylens-poly : ∀ {P Q} → PolyLensTerm P Q → PolyTerm P Q
bridge-polylens-poly t = t

------------------------------------------------------------------------
-- T25: ConjugateMonad.Term → MarkovCategory.Term bridge.
--
-- Every Bayesian update IS a Markov kernel (parameter, observation →
-- updated parameter). ConjGen embeds into MarkovGen.

-- Stub: the embedding requires the (parameter, observation) pair to
-- be reified as a Markov object. Concrete instances supply.

------------------------------------------------------------------------
-- T26: DFT.Term → PontryaginDual.Term bridge.
--
-- The DFT operates on characters of the dual group. Each DFT
-- generator (forward/inverse) embeds into the dual group's character
-- multiplication structure.

-- Stub: bridge requires character-indexing per DFT context. Concrete
-- instances at specific groups supply.

------------------------------------------------------------------------
-- T27: CascadedCoalgebra.Term → MarkovCategory.Term bridge.
--
-- Each cascade layer is a Markov kernel; the cascade itself is a
-- composition of Markov kernels with the one-way coupling preserved
-- in the embedding.

-- Stub: requires the cascade state to be a Markov object. Concrete
-- instances supply.

------------------------------------------------------------------------
-- T28: PontryaginDual.Term → Coxeter Word bridge.
--
-- For Z/n with cyclic generator g, characters are g^k. The CharTerm
-- IS a Coxeter word on one generator. The bridge is the identity
-- mapping CharTerm n → Substrate.Groups.Coxeter.FreeCyclic.

-- Stub: requires Substrate.Groups.Coxeter.FreeCyclic module integration.
-- The structural connection is named here; the explicit Coxeter
-- import is deferred to a concrete site.

------------------------------------------------------------------------
-- T29: Wedge.Trace → free-monoid word (CONCRETE, not a stub).
--
-- The R-arc / division machinery's free term is `Algebra.Wedge.Trace` (keep
-- every wedge step). It bridges into this diagram via `trace-word`: the free
-- wedge term ↦ its continued-fraction digit word (the free monoid on ℕ),
-- uniform over every `DivStr` — the same shape as T28 (a term ↦ a word). This
-- one is fully realized, not deferred.

bridge-wedgetrace-word : {D : DivStr} {a b g : C D} → Trace D a b g → List ℕ
bridge-wedgetrace-word = trace-word

------------------------------------------------------------------------
-- Categorical reading: the bridges form a small DIAGRAM in the
-- substrate's category-of-term-algebras. Each bridge is a functor
-- between the source and target term-categories; the bridges'
-- composability follows from the underlying records' semantic
-- compatibility.
--
-- Per the substrate's UP-topos discipline: bridges between term
-- algebras inhabit the UPCategory itself (each is a UPArrow whose
-- Source is one term-algebra and Target is another).
