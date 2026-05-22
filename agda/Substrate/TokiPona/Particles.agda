------------------------------------------------------------------------
-- Substrate.TokiPona.Particles
--
-- T6 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]].
--
-- The Toki Pona particles (li, e, pi, la, o) as **F₂-graded
-- structural markers** — the deliberate contrast with Lojban's L6
-- Cmavo (semantic post-composer wrappers).
--
-- DESIGN-LEVEL CONTRAST (the contrastive-pedagogy point per
-- [[user-rosetta-code-contrastive-pedagogy]]):
--
--   Lojban L6 Cmavo: each cmavo is a SEMANTIC OPERATION
--     (Sem → Sem post-composer; PU adds tense, NA negates).
--
--   Toki Pona T6 Particles: each particle is a STRUCTURAL MARKER
--     (an F₂ bit attached to a sentence position; li/e/pi/la/o
--     drive evaluation order without modifying semantic vectors
--     themselves).
--
-- Same linguistic outcome (compositional sentence meaning),
-- different mechanism. Lojban encodes structure positionally; Toki
-- Pona encodes structure via markers. F₂-grading captures the
-- discrete "marker present / absent" choice for each of the five
-- particle classes.
--
-- Per [[project-3plus1-parity-universal]]: the F₂-grading on
-- particles is yet another instance of the substrate's universal
-- F₂-chirality structure; the 5 particles times their on/off
-- states give 2⁵ = 32 marker configurations.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.Particles where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; cong; sym)

open import Substrate.Algebra.F2 using (F₂; 𝟘; 𝟙; _+_)
open import Substrate.TokiPona.SemanticSpace using (SemVec)
open import Substrate.TokiPona.TokiSentence using (TokiSentence)

private
  variable
    m : ℕ

------------------------------------------------------------------------
-- 1. Particle enumeration.
--
-- The five structural particles. `li` and `e` are obligatory
-- structural markers for transitive sentences; `pi`, `la`, `o` are
-- optional / context-dependent.
------------------------------------------------------------------------

data Particle : Set where
  li : Particle    -- predicate marker
  e  : Particle    -- object marker
  pi : Particle    -- modifier regrouping
  la : Particle    -- context / conditional prefix
  o  : Particle    -- vocative / imperative

------------------------------------------------------------------------
-- 2. F₂-graded marker bits.
--
-- A `MarkerSet` is a 5-tuple of F₂ bits, one per particle. The
-- whole-marker-set lives in (F₂)⁵ ≅ 2⁵ configurations. Each
-- TokiSentence pairs with a MarkerSet to convey structural
-- information that bare ⊕-pooling at T5 cannot.
------------------------------------------------------------------------

record MarkerSet : Set where
  constructor mkMarkers
  field
    li-mark : F₂
    e-mark  : F₂
    pi-mark : F₂
    la-mark : F₂
    o-mark  : F₂

open MarkerSet public

------------------------------------------------------------------------
-- 3. The empty marker set (no particles active).
--
-- An intransitive sentence with no contextual or vocative marking
-- carries this.
------------------------------------------------------------------------

no-markers : MarkerSet
no-markers = mkMarkers 𝟘 𝟘 𝟘 𝟘 𝟘

------------------------------------------------------------------------
-- 4. Single-particle marker constructors.
--
-- Each lifts a single Particle to the MarkerSet with that bit set.
------------------------------------------------------------------------

set-particle : Particle → MarkerSet
set-particle li = mkMarkers 𝟙 𝟘 𝟘 𝟘 𝟘
set-particle e  = mkMarkers 𝟘 𝟙 𝟘 𝟘 𝟘
set-particle pi = mkMarkers 𝟘 𝟘 𝟙 𝟘 𝟘
set-particle la = mkMarkers 𝟘 𝟘 𝟘 𝟙 𝟘
set-particle o  = mkMarkers 𝟘 𝟘 𝟘 𝟘 𝟙

------------------------------------------------------------------------
-- 5. Marker-set merge (componentwise F₂ XOR).
--
-- Combines two marker-sets componentwise; equivalent to F₂-vector
-- addition on the 5-tuple. Self-inverse (each particle marker
-- toggles), associative, commutative.
------------------------------------------------------------------------

merge-markers : MarkerSet → MarkerSet → MarkerSet
merge-markers a b = mkMarkers
  (li-mark a + li-mark b)
  (e-mark  a + e-mark  b)
  (pi-mark a + pi-mark b)
  (la-mark a + la-mark b)
  (o-mark  a + o-mark  b)

------------------------------------------------------------------------
-- 6. The MarkedSentence: a TokiSentence paired with its MarkerSet.
--
-- The richer linguistic object that carries both semantic vector
-- content AND structural-marker information. T9 worked examples
-- use this for sentences that need disambiguation (e.g.,
-- distinguishing transitive from intransitive, `pi`-regrouping
-- examples).
------------------------------------------------------------------------

record MarkedSentence (m : ℕ) : Set where
  constructor mkMarked
  field
    sentence : TokiSentence m
    markers  : MarkerSet

open MarkedSentence public

------------------------------------------------------------------------
-- 7. Lifted constructors.
--
-- A bare sentence becomes a MarkedSentence with no markers;
-- adding a particle merges its marker bit into the marker set.
------------------------------------------------------------------------

mark : TokiSentence m → MarkedSentence m
mark s = mkMarked s no-markers

with-particle : Particle → MarkedSentence m → MarkedSentence m
with-particle p ms = mkMarked
  (sentence ms)
  (merge-markers (markers ms) (set-particle p))

------------------------------------------------------------------------
-- 8. Particle-merge identity / composition coherence.
--
-- merge-markers is a commutative-monoid op on MarkerSet
-- (componentwise F₂); adding the same particle twice cancels
-- (self-inverse). T7 (Linearity) consumes these laws to discharge
-- the structural-marker coherence.
------------------------------------------------------------------------

merge-no-markersˡ : (ms : MarkerSet) → merge-markers no-markers ms ≡ ms
merge-no-markersˡ _ = refl

merge-no-markersʳ : (ms : MarkerSet) → merge-markers ms no-markers ≡ ms
merge-no-markersʳ (mkMarkers a b c d e′) =
  -- Each F₂ + 𝟘 reduces by 𝟘-right-identity. The substrate's F₂
  -- has the left-identity definitional (𝟘 + y = y) but the right
  -- side needs a 2-case proof — handled per component below.
  cong₅-mkMarkers
    (rightId a) (rightId b) (rightId c) (rightId d) (rightId e′)
  where
    rightId : (x : F₂) → x + 𝟘 ≡ x
    rightId 𝟘 = refl
    rightId 𝟙 = refl
    cong₅-mkMarkers :
      {a₁ a₂ b₁ b₂ c₁ c₂ d₁ d₂ e₁ e₂ : F₂} →
      a₁ ≡ a₂ → b₁ ≡ b₂ → c₁ ≡ c₂ → d₁ ≡ d₂ → e₁ ≡ e₂ →
      mkMarkers a₁ b₁ c₁ d₁ e₁ ≡ mkMarkers a₂ b₂ c₂ d₂ e₂
    cong₅-mkMarkers refl refl refl refl refl = refl
