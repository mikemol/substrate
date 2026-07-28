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
-- ⟡predictorring-freemonoid: the ring is the FREE MONOID on its member
-- alphabet, not a bare `List (Σ Set …)`. The old `members : List (Σ[ C ∈
-- Set ] PredictorSignature C)` forced `PredictorRing : Set₁` — the Set₁
-- debt lived in the `Σ over Set` ALPHABET (the container was never the
-- issue). Every real context is FINITE (⊤≅Fin 1, Fin n, Fin n×Fin n≅Fin(n·n),
-- Fin 24, Fin 8), so the context is encoded by its CARDINALITY (a ℕ code)
-- decoded via `Fin` — dropping the `Σ Set` and landing the whole structure
-- in Set₀. The container becomes `Coxeter.Word Gen` (the free monoid,
-- `FreeMonoid.free-monoid`), so the two ex-tautology "laws" below carry
-- REAL content: the operad identity IS the word-monoid unit law, and
-- reduce-winner IS the free-monoid fold into the tropical cost monoid.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.PredictorRing where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Product using (Σ-syntax; _,_; proj₂)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-identity-left; ++-identity-right)
open import Substrate.Category.FreeUniversalProperty.FreeMonoid
  using (MonoidOn; foldW; word-monoid)
open import Substrate.Algebra.Semiring.NatInf
  using (ℕ∞; fin; ∞; _⊓_; ⊓-assoc; ⊓-identityˡ; ⊓-identityʳ)

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
-- Set; consumers write `PredictorSignature Context`. (`Context` is phantom here — only
-- alphabet-size is a field — so `PredictorSignature C ≅ ℕ` for any C.)
record PredictorSignature (Context : Set) : Set where
  field
    alphabet-size  : ℕ

open PredictorSignature public

------------------------------------------------------------------------
-- Predictor variants in the V7 codec are different inhabitants of
-- this signature:
--
--   UnigramPredictor:       Context = ⊤        (one row)     ≅ Fin 1
--   BigramPredictor:        Context = Fin n    (one row per prev_emit)
--   TrigramPredictor:       Context = Fin n × Fin n          ≅ Fin (n·n)
--   ChamberContextPredictor: Context = Fin 24  (one row per chamber)
--   QuaternionContextPredictor: Context = Fin 8
--
-- Every context is FINITE, so it is coded by its cardinality (a ℕ) and
-- decoded via `Fin`. The member alphabet is therefore a Set₀ type.

-- ⟡predictorring-freemonoid: the member alphabet at Set₀. A member = its context
-- cardinality `cc : ℕ` (decoded to `Fin cc`) together with its signature. No `Σ Set`.
Gen : Set
Gen = Σ[ cc ∈ ℕ ] PredictorSignature (Fin cc)

------------------------------------------------------------------------
-- The codec's PredictorRing as the FREE MONOID on the member alphabet.
--
-- The V7 codec speculation picks per emission which inhabitant's
-- cumfreqs to use. The picking is the operad's reduce_winner (per
-- [[v-arc-generator-operad]]).

-- The ring IS `Coxeter.Word Gen` — the free monoid on the member alphabet
-- (`FreeMonoid.free-monoid`, ε = the empty ring [], ∙ = ring concatenation ++).
-- Now honestly Set₀: the Set₁ debt was the `Σ Set` alphabet (paid above), and the
-- container is the free-monoid structure, not a bare List.
record PredictorRing : Set where
  field
    members : Word Gen

open PredictorRing public

-- The ring's monoid structure: the free monoid on Gen (ε=[], ∙=++).
ring-monoid : MonoidOn (Word Gen)
ring-monoid = word-monoid Gen

------------------------------------------------------------------------
-- Operad identity law (REAL content; was a `length xs ≡ length xs` tautology).
--
-- The PredictorRing IS an algebra of the GeneratorOperad (cf.
-- [[v-arc-generator-operad]]):
--   * Each member is one generator-kind = Predictor.
--   * Composition over the ring is per-emission speculation (ring ++).
--   * The ring's identity element is the EMPTY ring [] (the V6 default:
--     no speculation = Unigram only), a genuine two-sided unit for ++.
--
-- These are the word-monoid unit laws — the operad identity, not a tautology.
------------------------------------------------------------------------

operad-identity-left : (w : Word Gen) → ([] ++ w) ≡ w
operad-identity-left = ++-identity-left

operad-identity-right : (w : Word Gen) → (w ++ []) ≡ w
operad-identity-right = ++-identity-right

------------------------------------------------------------------------
-- Per-emission cost competition (REAL content; was a `length xs ≡ length xs`
-- tautology). The V7 cost-gate evaluates each predictor's cost under the
-- same context and picks the MINIMUM. This is the free-monoid fold (`foldW`,
-- FreeMonoid.free-monoid's `extend`) into the TROPICAL (min, ∞) cost monoid
-- — so `reduce-winner`'s uniqueness is exactly the free-monoid `extend-unique`.
------------------------------------------------------------------------

-- The per-member bit-cost approximant. A placeholder cost (the alphabet size as
-- a finite tropical cost); the real codec supplies the measured per-context cost.
member-cost : Gen → ℕ∞
member-cost g = fin (alphabet-size (proj₂ g))

-- The tropical (min, ∞) cost monoid: ℕ∞ under ⊓ (min), identity ∞ (unreachable).
cost-monoid : MonoidOn ℕ∞
cost-monoid = record
  { ε = ∞ ; _∙_ = _⊓_
  ; ∙-assoc = ⊓-assoc ; ε-left = ⊓-identityˡ ; ε-right = ⊓-identityʳ
  }

-- reduce-winner: fold the ring to the MINIMUM member cost. The empty ring folds
-- to ∞ (no winner); each member competes by ⊓. This is `foldW` of the free monoid
-- on Gen into the tropical cost gauge — the operad's reduce step, made concrete.
reduce-winner : PredictorRing → ℕ∞
reduce-winner R = foldW Gen cost-monoid member-cost (members R)

------------------------------------------------------------------------
-- Categorical reading.
--
-- Per [[categorical-name-first]]: PredictorRing is the FREE MONOID
-- (an operad instance) at the codec's emission layer:
--   * `Coxeter.Word Gen` = the free monoid on the member alphabet
--     (`FreeMonoid.free-monoid` — a content-bearing FreeUP).
--   * The V-arc's GeneratorOperad (this is a sub-operad bound to the
--     emission-prediction kind); composition = ring ++.
--   * The cost-gate `reduce-winner` = the free-monoid fold into the
--     tropical cost monoid; its uniqueness = the UP's `extend-unique`.
--
-- Per [[homology-cohomology-recursion]]: rewrite rules are observed
-- redundancy (homology); adaptive predictors are catalogued frequency
-- (cohomology). The PredictorRing names the cohomology side at the
-- categorical level; the substrate's existing rule-grammar names the
-- homology side. Both are visible as members of the codec's full
-- generator ring.
--
-- (NOTE: "Ring" is a legacy misnomer — there is no additive/distributive
-- structure. This is the free MONOID of predictor signatures; selection
-- is the tropical FOLD `reduce-winner`, not a ring operation.)
------------------------------------------------------------------------
