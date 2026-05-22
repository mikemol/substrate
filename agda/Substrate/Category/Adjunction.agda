------------------------------------------------------------------------
-- Substrate.Category.Adjunction
--
-- Primitive #4 in the Substrate.Category.Primitives roadmap.
-- The adjoint-pair universal property at the substrate's level,
-- scoped to the free-on-Fin-n linear extension that M-3.5 work
-- captures (`linear-from-images ⊣ images-of-linear`).
--
-- Substrate-friendly framing: avoids full functor adjunction (which
-- needs functor categories, naturality, etc.) and packages the
-- universal property as a record over Set-level data:
--
--   L : (Fin n → Vector m) → Linear n m   (left adjoint:
--                                          "build linear extension")
--   R : Linear n m → (Fin n → Vector m)   (right adjoint:
--                                          "extract basis images")
--   η : R ∘ L ≡ id (pointwise on basis)   (unit; M-3.5's
--                                          apply-linear-from-images-basis)
--   ε : L ∘ R ≡ id (pointwise on vectors) (counit; M-3.5's
--                                          linear-extensionality applied
--                                          to L(R T) vs T)
--
-- This is the "free F₂-module on n generators" adjunction restricted
-- to vector codomain. Subsumable to full functor adjunction in
-- future work; sufficient now for the substrate's M-3.5 universal-
-- property invocations.
--
-- Per `feedback_categorical_name_first`: M-3.5's `linear-from-images`
-- + `apply-linear-from-images-basis` + `linear-extensionality` IS
-- the substrate's instance of the free-construction adjunction. The
-- universal property IS the inference rule. Naming this primitive
-- lets downstream code cite the adjunction at the site rather than
-- chaining M-3.5 lemmas per-call.
--
-- Connection to roadmap:
--
--   * Primitive #1 Coalgebra (FixedPoint, InvariantSubset, FiniteOrder,
--     LagrangeOrder) — characterised cyclic / composite torsion.
--   * Primitive #2 Equalizer (IsEqualised, Kernel-At) — characterised
--     kernel-shaped universal properties.
--   * Primitive #3 Pullback (Pullback-Of, Wide-Meet) — characterised
--     intersection / meet structures.
--   * Primitive #4 Adjunction (THIS slice) — characterises free
--     constructions / universal extension.
--   * Primitive #5 BeckChevalley (deferred) — characterises
--     non-commuting quotient squares; needs Adjunction.
--   * Primitive #6 FreeLinearization (deferred) — generic graph-to-
--     module functor; specialises Adjunction.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.Adjunction where

open import Substrate.Foundation.Fin using (Fin)
open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; trans; cong)

open import Substrate.Algebra.F2.Vector using (Vector; basis)
open import Substrate.Algebra.F2.Linear using (Linear; apply)
open import Substrate.Algebra.F2.Linear.FromImages
  using (linear-from-images; apply-linear-from-images-basis)
open import Substrate.Algebra.F2.Linear.Universal
  using (linear-extensionality)

------------------------------------------------------------------------
-- N-1: IsLinearAdjunction — the adjoint-pair universal property
-- between (Fin n → Vector m) and Linear n m.
--
-- The substrate-relevant adjunction:
--
--   L : (Fin n → Vector m) → Linear n m
--   R : Linear n m → (Fin n → Vector m)
--
-- with the unit/counit pair satisfying the triangle identities (here
-- expressed as pointwise equalities, avoiding funext).
------------------------------------------------------------------------

record IsLinearAdjunction (n m : ℕ) : Set where
  field
    -- Left adjoint: build a linear map from basis images.
    L : (Fin n → Vector m) → Linear n m

    -- Right adjoint: extract basis images from a linear map.
    R : Linear n m → (Fin n → Vector m)

    -- Unit (η): R ∘ L is identity pointwise on basis-image functions.
    -- I.e., recovering basis images from the constructed linear map
    -- gives back the original images.
    unit : (f : Fin n → Vector m) (i : Fin n) → R (L f) i ≡ f i

    -- Counit (ε): L ∘ R is identity pointwise on vectors. I.e., the
    -- linear map built from a linear map's own basis images IS that
    -- linear map (up to apply-equality).
    counit : (T : Linear n m) (v : Vector n) → apply (L (R T)) v ≡ apply T v

------------------------------------------------------------------------
-- N-2: The substrate's canonical instance — M-3.5 adjunction.
--
-- L = linear-from-images
-- R = images-of-linear (λ T i → apply T (basis i))
-- unit = apply-linear-from-images-basis
-- counit = derived via linear-extensionality
------------------------------------------------------------------------

-- The right adjoint: extract basis images. (Defined at module level
-- to avoid where-block scoping confusion in the record instance.)
images-of-linear : ∀ {n m} → Linear n m → (Fin n → Vector m)
images-of-linear T i = apply T (basis i)

linear-adjunction : ∀ {n m} → IsLinearAdjunction n m
linear-adjunction {n} {m} = record
  { L      = linear-from-images
  ; R      = images-of-linear
  ; unit   = apply-linear-from-images-basis
  ; counit = counit-impl
  }
  where
    -- counit T v: apply (linear-from-images (images-of-linear T)) v ≡ apply T v.
    -- Strategy: both sides are linear maps that agree on basis
    --   (by apply-linear-from-images-basis at the constructed map's
    --   own basis images). linear-extensionality lifts agreement on
    --   basis to agreement on all v.
    counit-impl : (T : Linear n m) (v : Vector n) →
                  apply (linear-from-images (images-of-linear T)) v
                    ≡ apply T v
    counit-impl T =
      linear-extensionality
        (linear-from-images (images-of-linear T)) T
        (λ i → apply-linear-from-images-basis (images-of-linear T) i)

------------------------------------------------------------------------
-- N-3: Derived universal property — uniqueness of the extension.
--
-- Any linear map L' that agrees with f on basis IS linear-from-images f
-- (up to apply-equality on all vectors). This is the universal mapping
-- property of the free construction: there's a UNIQUE linear extension.
--
-- Derived from the adjunction's unit + counit + linear-extensionality.
------------------------------------------------------------------------

linear-extension-unique :
  ∀ {n m} (f : Fin n → Vector m) (L' : Linear n m) →
  ((i : Fin n) → apply L' (basis i) ≡ f i) →
  (v : Vector n) → apply L' v ≡ apply (linear-from-images f) v
linear-extension-unique f L' agree v =
  linear-extensionality L' (linear-from-images f)
    (λ i → trans (agree i)
                 (sym (apply-linear-from-images-basis f i)))
    v

------------------------------------------------------------------------
-- N-4: Capstone — Adjunction primitive #4 lands.
--
-- After this slice, the substrate's M-3.5 universal-property
-- infrastructure is named with its categorical handle:
--
--   * `linear-from-images` is the LEFT ADJOINT of the free-on-Fin-n
--     adjunction.
--   * `images-of-linear` (= λ T i → apply T (basis i)) is the
--     RIGHT ADJOINT.
--   * `apply-linear-from-images-basis` is the UNIT.
--   * `linear-extensionality` is what derives the COUNIT.
--   * `linear-extension-unique` is the universal mapping property
--     directly, derivable from the adjunction.
--
-- The Category roadmap now covers:
--
--   #1 Coalgebra   (FixedPoint, InvariantSubset, FiniteOrder,
--                   LagrangeOrder) — cyclic / composite torsion ✓
--   #2 Equalizer   (IsEqualised, Kernel-At) ✓
--   #3 Pullback    (Pullback-Of, Wide-Meet) ✓
--   #4 Adjunction  (IsLinearAdjunction, linear-adjunction) — THIS ✓
--   #5 BeckChevalley — depends on Adjunction. The non-commuting
--                      quotient square / 2-cell. Names the 3+1 parity
--                      universal across meta-levels.
--   #6 FreeLinearization — generic graph-to-module functor, opens
--                          Prong B (continuous-side bridging).
--
-- Per `feedback_categorical_name_first`: the universal property of
-- the adjunction IS the inference rule. Downstream substrate code
-- can cite linear-adjunction's unit/counit/extension-unique rather
-- than chaining apply-linear-from-images-basis + linear-extensionality
-- per call site.
--
-- Demotion targets (deferred sweep):
--
--   * Every use of `apply-linear-from-images-basis` becomes a
--     `linear-adjunction.unit` citation. Same content, named with
--     its universal property.
--
--   * Every use of `linear-extensionality` for the "two linear maps
--     agree on basis ⇒ agree on all vectors" pattern becomes
--     `linear-extension-unique` (which packages the agreement
--     directly).
--
--   * Substrate-wide audit for retrofit opportunities (separate
--     slice — Explore agent to identify all M-3.5 call sites).
--
-- Deferred coalgebraic-unfolding follow-ons:
--
--   * **General functor adjunction** at universe level (requires
--     functor categories; substantial categorical machinery). The
--     present Set-level scoped version is sufficient for the
--     substrate's current uses.
--
--   * **Triangle identities** as explicit lemmas (derivable from
--     unit + counit + naturality; here implicit since unit/counit
--     suffice for the substrate's invocations).
--
--   * **Yoneda lemma instance**: every linear map factors uniquely
--     through its basis-image function. Direct corollary of
--     linear-extension-unique; if substrate needs the Yoneda framing
--     explicitly, can be a follow-on slice.
--
--   * **Adjunction-via-bijection**: re-package linear-adjunction
--     as a bijection of homsets `Hom(L f, T) ≅ Hom(f, R T)`. This is
--     the standard categorical formulation; the present unit/counit
--     packaging is equivalent but unrolled.
------------------------------------------------------------------------
