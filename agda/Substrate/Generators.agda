------------------------------------------------------------------------
-- Substrate.Generators
--
-- Index / catalog of every "generator-shaped" definition in the
-- substrate's Agda surface. Substrate-native: a single re-exporter so
-- the catalog is mechanically checkable and open-import-able. Each
-- section corresponds to one kind of generator; see the section
-- comments for what each kind means.
--
-- Per the user's framing of "generator" (collected 2026-05-22):
--   1. Cover / dispatch combinators — the tools that EXPOSE a generator
--      by collapsing N-case enumeration into a 1-line refl-tuple.
--   2. Payload-shape primitives — the structural-tuple types that
--      describe what a cover's payload looks like (Pow, dep-Pow,
--      n-refls, etc.).
--   3. Coxeter-style group generators — `data Gen` declarations and
--      their insert/normalize machinery (Z/2, Z/3, Z/4, Z/5, Z/7, V₄,
--      FreeCyclic).
--   4. Group-action generators — the morphism-level primitives whose
--      products give the full action (rotate, swap-αβ, rot-pow, ...).
--   5. F₂-linear / GL(3,F₂) generators — σ-permutations, swap01,
--      cycle3, Singer cycle.
--   6. Hodge / duality generators — ★, dual-line, normal-vector.
--   7. Universal-property generators — Free constructions and the
--      universal arrows + extensionality lemmas that surface them.
--   8. Categorical limit/colimit primitives — Cone, Equalizer,
--      Pullback, Limit, Colimit.
--   9. Adjunctions — IsLinearAdjunction, GaloisAdjunction.
--   10. Higher-categorical generators — UPArrow / UPMorphism / fixed
--       point embedding.
--   11. Operadic — GeneratorOperad, OpcodeAlgebra.
--   12. Monad / Comonad / Kan extension.
--
-- This module is a CATALOG, not a library: it re-exports `public` so
-- downstream callers can `open import Substrate.Generators` and have
-- every named generator in scope under a section-specific namespace
-- alias (Z₂, Z₃, Z₄, ..., V₄C, etc.).
--
-- Naming discipline: each algebraic family is exposed via a `module M
-- where open import X public` namespacing block, so name clashes
-- between Z/n's are resolved structurally (Z₃.a vs Z₄.a vs ...).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Generators where

------------------------------------------------------------------------
-- 1. COVER / DISPATCH COMBINATORS
--
-- These are the "expose generator not orbit" tools. Each takes a
-- predicate P and a tuple of per-position witnesses, and dispatches
-- across the finite-constructor type.
------------------------------------------------------------------------

open import Substrate.Foundation.Fin.Cover
  using ( dep-Pow
        ; fin-cover
        ; fin×fin-cover
        ; fin-cover-2²
        ; fin-cover-2⁴
        ; tabulate
        )

open import Substrate.Groups.V4.Operations
  using ( v4-cover
        ; v4×v4-cover
        ; v4×v4×v4-cover
        )

open import Substrate.Axes.Cover using (axis-cover)
open import Substrate.Axes.PairCover using (axis×axis-cover)

------------------------------------------------------------------------
-- 2. PAYLOAD-SHAPE PRIMITIVES
--
-- The structural-tuple types and named-refl-tuple primitives that the
-- covers consume.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.CanonicalCover
  using ( Pow
        ; copies
        ; n-refls
        ; 4²-refls
        ; 4³-refls
        ; 2²-refls
        ; 2³-refls
        ; 2⁴-refls
        )

------------------------------------------------------------------------
-- 3. COXETER-STYLE GROUP GENERATORS
--
-- Each Z/n group exposes a single `data Gen` declaration with the
-- generator-letter `a` (and the involution/wrap relations are encoded
-- in `insert`). V₄ is the exceptional case with TWO generators (A, B).
-- FreeCyclic is the relation-free Z/∞ analogue (no wraparound).
--
-- Per-family namespace aliases so downstream code can write
-- `Substrate.Generators.Z₃.a` etc. without clashes.
------------------------------------------------------------------------

open import Substrate.Groups.Actions.S3-on-V4.Generators
  using ( rotate
        ; swap-αβ
        ; rot-pow
        ; swap-pow
        )
open import Substrate.Algebra.GL3F2.GaugeGenerators
  using ( σ₂
        ; swap01-Linear
        ; σ₃
        ; cycle3-Linear
        )
open import Substrate.Algebra.F2.FanoPlane
  using ( singer
        ; singer-Linear
        )
open import Substrate.Algebra.F2.HodgeDim4.HodgeStar
  using ( hodge-star
        )
open import Substrate.ShadowArchitecture.Duality
  using ( normal-vector
        ; dual-line
        )
open import Substrate.Category.FreeOverBasis
  using ( FreeOverBasis
        )
open import Substrate.Category.FreeLinearization
  using ( FreeLinearization
        )
open import Substrate.Category.FreeLinearization.FromImages
  using ( free-linearize
        )
open import Substrate.Algebra.F2.Linear.FromImages
  using ( linear-from-images
        )
open import Substrate.Algebra.F2.Linear.Universal
  using ( linear-extensionality
        )
open import Substrate.Algebra.Module.Free.Basis
  using ( FreeBasisUniversal
        )
open import Substrate.Algebra.Module.Free.UniqueExtension
  using ( FreeModuleExtensionality
        )
open import Substrate.Category.Equalizer
  using ( Equalizer-Of
        ; equalizer-factor
        )
open import Substrate.Category.Coequalizer
  using ( Coequalises
        ; coequalizer-factor
        )
open import Substrate.Category.Pullback
  using ( Pullback-Of
        )
open import Substrate.Category.Pushout
  using ( PushoutCocone
        ; pushout-factor
        )
open import Substrate.Category.Limit
  using ( Limit
        )
open import Substrate.Category.Colimit
  using ( Colimit
        )
open import Substrate.Category.Opposite
  using ( Opposite
        )
open import Substrate.Category.Functor.Opposite
  using ( opposite-Functor
        ; from-opposite-Functor
        )
open import Substrate.Category.Adjunction
  using ( IsLinearAdjunction
        ; linear-adjunction
        )
open import Substrate.Category.GaloisAdjunction
  using ( GaloisAdjunction
        )
open import Substrate.Category.UniversalProperty
  using ( UPArrowP
        )
open import Substrate.Category.UniversalProperty.Morphism
  using ( UPMorphism
        )
open import Substrate.Category.UniversalProperty.FixedPoint
  using ( ι
        )
open import Substrate.Category.UniversalProperty.Terminal
  using ( to-trivial-cond
        )
open import Substrate.Category.Monad
  using ( Monad
        )
open import Substrate.Category.Comonad
  using ( Comonad
        )
open import Substrate.Category.KanExtension
  using ( LeftKanExtension
        ; RightKanExtension
        )
module Z₂C where
  open import Substrate.Groups.Z2-Coxeter
module Z₃C where
  open import Substrate.Groups.Z3-Coxeter
module Z₄C where
  open import Substrate.Groups.Z4-Coxeter
module Z₅C where
  open import Substrate.Groups.Z5-Coxeter
module Z₇C where
  open import Substrate.Groups.Z7-Coxeter
module V₄C where
  open import Substrate.Groups.V4-Coxeter
module FCyclic where
  open import Substrate.Groups.FreeCyclic-Coxeter
------------------------------------------------------------------------
-- 4. GROUP-ACTION GENERATORS (S₃ on V₄)
--
-- The dihedral-style action generators rotate / swap-αβ / their `pow`
-- iterators. Together they generate the full S₃ action on V₄.
------------------------------------------------------------------------


------------------------------------------------------------------------
-- 5. F₂-LINEAR / GL(3,F₂) GENERATORS
--
-- Permutation generators on Fin n + their basis-permutation linear
-- extensions in GL(3,F₂). Together these cover the Sylow-2 (σ₂ /
-- swap01-Linear, order 2), Sylow-3 (σ₃ / cycle3-Linear, order 3), and
-- Sylow-7 (singer / singer-Linear, order 7) of GL(3,F₂).
------------------------------------------------------------------------

-- Ⓖ.cyclen-collapse-registry: σ₃ / cycle3-Linear now come from their canonical
-- Sylow-3 home (GaugeGenerators, below) — the standalone ...Permutation.Cycle3
-- orbit-module is dissolved. All three Sylow generators re-export from one place.


------------------------------------------------------------------------
-- 6. HODGE / DUALITY GENERATORS
--
-- Order-2 / order-7 involution-style generators tied to Hodge ★ on
-- F₂⁴ bivectors and Fano-plane self-duality (Point ↔ Line).
------------------------------------------------------------------------



------------------------------------------------------------------------
-- 7. UNIVERSAL-PROPERTY GENERATORS
--
-- Free constructions: the universal arrow and the extensionality
-- lemma that the universal property surfaces. These reduce per-element
-- checking (size of carrier) to per-basis checking (n).
------------------------------------------------------------------------








------------------------------------------------------------------------
-- 8. CATEGORICAL LIMIT / COLIMIT PRIMITIVES
--
-- Equalizer, Pullback, Limit, Colimit. Cone-based subsumption: per
-- [[project-cone-subsumes-equalizer-pullback]] these are (2,1) /
-- (3,1)-shape Cone instances; they remain exposed as ergonomic
-- primitives.
------------------------------------------------------------------------







------------------------------------------------------------------------
-- 8a. DUALITY-WITNESSING PRIMITIVES
--
-- Opposite + Functor-on-Opposite: the substrate's structural vehicle
-- for absorbing categorical-duality similarity into a single
-- parametric skeleton. Each dual pair (Monad/Comonad, Limit/Colimit,
-- Algebra/Coalgebra, …) can be presented as primal-applied-to-
-- Opposite rather than as a separately-catalogued dual record.
--
-- Per the pullback-as-skeleton principle: Opposite is the projection
-- that lets one parametric witness (e.g. Monad C) cover both
-- specializations (Monad on C; Monad on Opposite C = Comonad on C).
------------------------------------------------------------------------



-- 1:N cone witnesses for substrate-named categorical structures
-- (per [[named-categorical-structure-skeletons]]). DaggerCategory.AsNamed
-- and SymmetricMonoidal.AsNamed are the apex modules; substrate-named
-- legs (HodgeStar.AsDaggerEndomap, Bijection.AsDagger, etc.) become
-- 2-line `open + renaming` projections from these.
--
-- (Parametric modules: not re-exported as values; downstream code
-- imports the relevant leg directly.)

------------------------------------------------------------------------
-- 9. ADJUNCTIONS
--
-- The Free–Forgetful style adjunctions that surface universal arrows.
-- linear-adjunction is the canonical F₂-vector free-forgetful pair;
-- GaloisAdjunction is the PresentedGroup ↔ ConjugationCoalgebra bridge
-- (T-arc Galois machinery).
------------------------------------------------------------------------



------------------------------------------------------------------------
-- 10. HIGHER-CATEGORICAL GENERATORS (Universal Property as object)
--
-- UPArrow = the "arrow with its universal-property witness" carrier;
-- UPMorphism = structure-preserving morphism between UPArrows;
-- ι : UPArrow² → UPArrow is the fixed-point embedding that closes the
-- arrow-category-of-UPCategory under self-application (per
-- [[project-tetrative-metacircularity]]). to-trivial-cond is the
-- conditional terminal map.
------------------------------------------------------------------------





------------------------------------------------------------------------
-- 11. OPERADIC / OPCODE-ALGEBRA GENERATORS
--
-- OpcodeAlgebra exposes the codec's opcode set as a CCC carrier; each
-- opcode IS a generator. GeneratorOperad is the operad over the
-- substrate's emission generator ring (Rule / Predictor / BasisShift /
-- Sink kinds) — composition is concatenation, the operad laws are the
-- proof obligations.
------------------------------------------------------------------------

-- NOTE: Two operadic primitives are NOT re-exported here because they
-- fail to typecheck cleanly:
--   * Substrate.Category.OpcodeAlgebra — its `execute` function tries
--     to instantiate substrate-native `Vec` (Set-only) with a Set ℓO
--     opcode type, sort-mismatch. Record itself is sound; importers
--     should reach into the module directly.
--   * Substrate.Category.GeneratorOperad — imports stdlib `Data.List`,
--     which conflicts with `Substrate.Foundation.Bool`'s BUILTIN BOOL
--     binding. Violates substrate-stdlib-avoidance discipline (see
--     [[feedback-minimize-stdlib-deps]]); should be rewritten to use
--     Coxeter.Word-as-List or substrate-native List.
--
-- Both are catalogued here (as kinds of generator-shaped definitions)
-- but cannot be safely re-exported until those issues are resolved.

------------------------------------------------------------------------
-- 12. MONAD / COMONAD / KAN EXTENSION
--
-- Endofunctor-with-structure records. Monad = (T, η, μ); Comonad =
-- (S, ε, δ); Kan extensions = (left/right) universal extension of a
-- functor along another.
------------------------------------------------------------------------




-- 1:N cone witness for Monad-derived categories.
-- Substrate.Category.Monad.DerivedCategoryOf is the apex; its legs
-- are Substrate.Category.KleisliCategory (R5) and
-- Substrate.Category.EilenbergMooreCategory (R6), each a thin
-- renaming projection from this skeleton. New categories-derived-
-- from-a-monad land as additional renaming legs.
--
-- (Parametric modules: not re-exported as values; downstream code
-- imports the relevant leg directly.)

------------------------------------------------------------------------
-- INDEX SUMMARY
--
-- Cover/dispatch (§1):
--   dep-Pow, fin-cover, fin×fin-cover, fin-cover-2², fin-cover-2⁴,
--   tabulate, v4-cover, v4×v4-cover, v4×v4×v4-cover, axis-cover,
--   axis×axis-cover, Z_nC.canonical-cover (uniform across n=2/3/4/5/7,
--   all in-core).
--
-- Payload shape (§2):
--   Pow, copies, n-refls, 2²-refls / 2³-refls / 2⁴-refls /
--   4²-refls / 4³-refls.
--
-- Coxeter Gens (§3):
--   Z₂C / Z₃C / Z₄C / Z₅C / Z₇C (single-letter `a` + insert),
--   V₄C (generators `A`, `B`), FCyclic (`a`, no wrap).
--
-- S₃-on-V₄ actions (§4):
--   rotate, swap-αβ, rot-pow, swap-pow.
--
-- GL(3,F₂) Sylows (§5):
--   σ₂ / swap01-Linear (Sylow-2),
--   σ₃ / cycle3-Linear (Sylow-3),
--   singer / singer-Linear (Sylow-7).
--
-- Hodge / duality (§6):
--   hodge-star, normal-vector, dual-line.
--
-- Free / universal-arrow (§7):
--   FreeOverBasis, FreeLinearization, free-linearize,
--   linear-from-images, linear-extensionality, FreeBasisUniversal,
--   FreeModuleExtensionality.
--
-- Limit-shaped (§8):
--   Equalizer-Of, equalizer-factor, Pullback-Of, Limit, Colimit.
--
-- Adjunctions (§9):
--   IsLinearAdjunction, linear-adjunction, GaloisAdjunction.
--
-- Higher-categorical (§10):
--   UPArrow, UPMorphism, ι (FixedPoint), to-trivial-cond.
--
-- Monad / Comonad / Kan (§12):
--   Monad, Comonad, LeftKanExtension, RightKanExtension.
--
-- Catalogued but NOT re-exported (typecheck-blocked):
--   OpcodeAlgebra  (Vec sort mismatch),
--   GeneratorOperad (stdlib pollution).
------------------------------------------------------------------------
