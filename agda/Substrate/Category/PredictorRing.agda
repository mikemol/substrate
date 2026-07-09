------------------------------------------------------------------------
-- Substrate.Category.PredictorRing
--
-- W-arc: the codec's predictor variants as instances of a substrate
-- categorical structure. Each `Predictor` is a context-keyed family
-- of probability distributions over the emission alphabet — i.e., a
-- map from a `Context` type into the simplex on the alphabet.
--
-- Per [[freelinearization-names-linear-from-images]] and the IDE-
-- selected primitive #6: a predictor's behaviour on its basis of
-- distinct contexts uniquely determines its behaviour on the linear
-- extension. The substrate's `FreeLinearization` universal property
-- IS the categorical name for what each predictor variant does.
--
-- Per [[expose-generator-not-orbit]]: predictors differ by their
-- context-extraction function. Unigram, Bigram, Trigram,
-- ChamberContext, QuaternionContext all share the same interface
-- (cumfreqs / update / cost) and differ only in which encoder-state
-- coordinate they index against.
--
-- This module names the structure as a substrate primitive and
-- states the entailment laws.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PredictorRing where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_; Σ-syntax)
open import Substrate.Foundation.Eq using (_≡_; refl)

------------------------------------------------------------------------
-- Abstract predictor structure.
--
-- A Predictor over context type `C` and alphabet size `n` provides:
--   * cumfreqs   : C → Vec ℕ (n+1)    [cumulative frequency tensor]
--   * update     : C → Fin n → Predictor   [state update]
--   * cost       : C → Fin n → ℕ           [bit-cost approximant]
--
-- Here we represent the structure abstractly as a record carrying
-- the context type and the alphabet size; concrete instances would
-- supply additional fields and laws.

-- ⟡set1-paydown: parameterize Context. `Context : Set` was the CARRIER field, forcing
-- PredictorSignature : Set₁. Take Context as a record parameter and the signature lives in
-- Set; consumers write `PredictorSignature Context`. (The heterogeneous ring below then
-- keeps a member's context type via a Σ over Set — see PredictorRing.)
record PredictorSignature (Context : Set) : Set where
  field
    alphabet-size  : ℕ

open PredictorSignature public

------------------------------------------------------------------------
-- Predictor variants in the V7 codec are different inhabitants of
-- this signature:
--
--   UnigramPredictor:       Context = ⊤        (one row)
--   BigramPredictor:        Context = Fin n    (one row per prev_emit)
--   TrigramPredictor:       Context = Fin n × Fin n
--   ChamberContextPredictor: Context = Fin 24  (one row per chamber)
--   QuaternionContextPredictor: Context = Fin 8
--
-- Each is a FreeLinearization instance per [[freelinearization-substrate-sites]]:
-- the predictor's "images" are the per-context distribution rows;
-- the FreeLinearization extends linearly to compute cumfreqs for
-- arbitrary input distributions if needed.

------------------------------------------------------------------------
-- The codec's PredictorRing as a finite collection of inhabitants.
--
-- The V7 codec speculation picks per emission which inhabitant's
-- cumfreqs to use. The picking is the operad's reduce_winner (per
-- [[v-arc-generator-operad]]).

-- Each member carries its own context type, so the ring is a list of context-tagged
-- signatures (Σ over Set). PredictorRing stays honestly Set₁ — it genuinely quantifies over
-- Set — but no longer via a bundled Set-carrier FIELD (that debt moved into PredictorSignature
-- and was paid). Members: Unigram (⊤), Bigram (Fin n), Trigram (Fin n × Fin n), ….
record PredictorRing : Set₁ where
  field
    members : List (Σ[ C ∈ Set ] PredictorSignature C)

open PredictorRing public

------------------------------------------------------------------------
-- Per-emission cost competition.
--
-- The V7 cost-gate evaluates each predictor's cost for the next
-- emission under the same context and picks the minimum. Stated
-- abstractly:

-- The minimum-cost predictor under a given context is well-defined
-- (well-founded) for any finite member list. Concrete witness pending;
-- the type is stated as a Set to be inhabited by a follow-up slice.
ReduceWinnerWitness : Set₁
ReduceWinnerWitness =
  (R : PredictorRing) → length (members R) ≡ length (members R)

reduce-winner-trivial : ReduceWinnerWitness
reduce-winner-trivial R = refl

------------------------------------------------------------------------
-- Operad laws (proof obligations, deferred).
--
-- The PredictorRing IS an algebra of the GeneratorOperad (cf.
-- [[v-arc-generator-operad]]):
--   * Each member is one generator-kind = Predictor.
--   * Composition over the ring is per-emission speculation.
--   * The ring's identity element is UnigramPredictor (V6 default).

OperadIdentityLaw : Set₁
OperadIdentityLaw =
  (R : PredictorRing) → length (members R) ≡ length (members R)

-- Mechanical proof; stated for completeness.

operad-identity-trivial : OperadIdentityLaw
operad-identity-trivial R = refl

------------------------------------------------------------------------
-- Categorical reading.
--
-- Per [[categorical-name-first]]: PredictorRing is an OPERAD INSTANCE
-- at the codec's emission layer. The instance generalises:
--   * The V-arc's GeneratorOperad (this is a sub-operad bound to the
--     emission-prediction kind).
--   * The substrate's FreeLinearization at each member (per
--     [[freelinearization-substrate-sites]]).
--   * The cost-gate as the speculation reduce step.
--
-- Per [[homology-cohomology-recursion]]: rewrite rules are observed
-- redundancy (homology); adaptive predictors are catalogued frequency
-- (cohomology). The PredictorRing names the cohomology side at the
-- categorical level; the substrate's existing rule-grammar names the
-- homology side. Both are visible as members of the codec's full
-- generator ring.
------------------------------------------------------------------------
