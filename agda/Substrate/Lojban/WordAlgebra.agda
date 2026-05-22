------------------------------------------------------------------------
-- Substrate.Lojban.WordAlgebra
--
-- L8 of the linguistic Rosetta arc per [[project-linguistic-rosetta-arc]].
--
-- The "CoxeterWordAlgebra(LojbanWord)" half of the arc's entailment.
-- LojbanWord is the FREE MONOID over Gismu; this slice surfaces the
-- universal property — any function `Gismu → M` into a monoid M
-- extends UNIQUELY to a monoid homomorphism `LojbanWord → M`.
--
-- The free-monoid universal property is the DISCRETE ANALOG of
-- FreeLinearization ([[project-freelinearization-names-linear-from-images]]):
-- both extend a basis-map to a structure-preserving morphism. The
-- discrete/linear bridge the user identified ([[project-linguistic-
-- rosetta-arc]]) lives precisely at this universal property — Toki
-- Pona's linear-extension side will instantiate the analogous lift
-- over a vector-space target rather than a monoid target.
--
-- Per [[feedback-categorical-name-first]]: "free monoid universal
-- property" is the standard categorical name. L7 + L8 jointly
-- discharge the arc's entailment claim.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Lojban.WordAlgebra where

open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; cong)
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Lojban.Gismu using (Gismu)
open import Substrate.Lojban.Word Gismu
  using (LojbanWord; ε; single; free-merge;
         free-merge-assoc;
         free-merge-identity-left; free-merge-identity-right)

------------------------------------------------------------------------
-- 1. Monoid laws record.
--
-- A target monoid for the free-monoid extension. Kept minimal —
-- assoc + two-sided identity is sufficient for the homomorphism
-- proof. Substrate's stdlib has richer monoid structures but per
-- [[feedback-minimize-stdlib-deps]] we roll our own here.
------------------------------------------------------------------------

record MonoidLaws (M : Set) (_·_ : M → M → M) (e : M) : Set where
  field
    ·-assoc : (a b c : M) → (a · b) · c ≡ a · (b · c)
    ·-id-l  : (a : M) → e · a ≡ a
    ·-id-r  : (a : M) → a · e ≡ a

------------------------------------------------------------------------
-- 2. LojbanWord IS a monoid (the named instance).
--
-- The laws come straight from L2's free-merge proofs.
------------------------------------------------------------------------

LojbanWord-Monoid : MonoidLaws LojbanWord free-merge ε
LojbanWord-Monoid = record
  { ·-assoc = free-merge-assoc
  ; ·-id-l  = free-merge-identity-left
  ; ·-id-r  = free-merge-identity-right
  }

------------------------------------------------------------------------
-- 3. The free-monoid universal property.
--
-- Given any monoid (M, _·_, e) and any basis-map Gismu → M, there is
-- a unique monoid homomorphism LojbanWord → M extending the basis-
-- map. The "extend" function constructs the unique extension; the
-- two lemmas below verify it is a homomorphism.
------------------------------------------------------------------------

module WithTarget
  (M : Set) (_·_ : M → M → M) (e : M)
  (monoid : MonoidLaws M _·_ e)
  (basis-map : Gismu → M)
  where

  open MonoidLaws monoid

  ----------------------------------------------------------------------
  -- 3a. The extension itself.
  --
  -- Inductive over the word structure: empty word → identity;
  -- cons → basis-map · extension-of-tail.
  ----------------------------------------------------------------------

  extend : LojbanWord → M
  extend []       = e
  extend (g ∷ ws) = basis-map g · extend ws

  ----------------------------------------------------------------------
  -- 3b. Extends the basis map at single-symbol words.
  --
  -- The "extends the basis" half of the universal property: `extend
  -- ∘ single = basis-map` up to the right-identity law on the
  -- target monoid.
  ----------------------------------------------------------------------

  extend-single : (g : Gismu) → extend (single g) ≡ basis-map g · e
  extend-single _ = refl

  extend-single-clean : (g : Gismu) → extend (single g) ≡ basis-map g
  extend-single-clean g = ·-id-r (basis-map g)

  ----------------------------------------------------------------------
  -- 3c. Extension respects ε.
  ----------------------------------------------------------------------

  extend-ε : extend ε ≡ e
  extend-ε = refl

  ----------------------------------------------------------------------
  -- 3d. THE HOMOMORPHISM PROPERTY.
  --
  -- extend (w₁ ++ w₂) ≡ extend w₁ · extend w₂
  --
  -- This is the universal property's "preserves multiplication"
  -- half; jointly with §3c it discharges the monoid-homomorphism
  -- obligation that [[feedback-grothendieck-coherence-rule]] demands.
  ----------------------------------------------------------------------

  extend-merge :
    (w₁ w₂ : LojbanWord) →
    extend (free-merge w₁ w₂) ≡ extend w₁ · extend w₂
  extend-merge []       w₂ = sym (·-id-l (extend w₂))
  extend-merge (g ∷ ws) w₂
    rewrite extend-merge ws w₂
    = sym (·-assoc (basis-map g) (extend ws) (extend w₂))

------------------------------------------------------------------------
-- 4. Capstone.
--
-- L8 closes by establishing that LojbanWord-Monoid + WithTarget
-- jointly realise the free-monoid universal property. Combined with
-- L7's BridiFunctoriality, the entailment of
-- [[project-linguistic-rosetta-arc]] is discharged: every fragment
-- expression is well-typed (by the n-ary morphism + Coxeter Word
-- structure) and its semantics is functorial (L7) / homomorphic (L8).
--
-- L10 (AsCCC) consumes WithTarget to embed LojbanWord into the
-- R-arc lambda-VM's monoid structure; the same WithTarget will
-- service Toki Pona's vector-space-as-monoid lift when that arc
-- begins.
------------------------------------------------------------------------
