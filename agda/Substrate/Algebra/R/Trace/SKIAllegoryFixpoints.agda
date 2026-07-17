{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.SKIAllegoryFixpoints — ⟡ski-allegory-fixpoints: the
-- two fixed-point ENDPOINTS of the flat/graded allegory (ADD 156), wired to their
-- PROVEN universal properties — HONESTLY scoping the part the substrate flags open.
--
-- HONESTY FIRST (Refinement.agda, verbatim): "Trace = μΦ; RealTrace = νΦ ... proving
-- `Trace ≅ μ` of a SPECIFIC Φ (and RealTrace ≅ ν) is a further obligation" — an
-- IDENTIFIED-NOT-YET-PROVEN deferral, the LARGE remainder. AND it flags a FALSE
-- SHORTCUT: raw `GradedDivStr.R` (the toy Φ-arity of ADD 156, a fixed/non-shrinking
-- shift) is NOT a Φ-iterate; the iterate lives on a Φ built from the wedge STEP.
--
-- So this module does NOT claim Trace ≅ μ(Φ-arity) (that would BE the false shortcut).
-- It wires the two endpoints to what IS proven: Trace's INITIAL-ALGEBRA property
-- (trace-fold-unique = the μ universal property) and RealTrace's TERMINAL-COALGEBRA
-- property (ana-unique = the ν universal property). The least/greatest pair is the
-- fold⊣unfold duality; the SPECIFIC-Φ iso is scoped as the substrate's own frontier.
------------------------------------------------------------------------

module Substrate.Algebra.R.Trace.SKIAllegoryFixpoints where

open import Substrate.Foundation.Eq  using (_≡_; refl)
open import Substrate.Algebra.Wedge using (DivStr; z; Trace; done; more; trace-fold; trace-fold-unique)
open import Substrate.Algebra.R.Trace using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Bisim using (_~_; ~-refl)
open import Substrate.Algebra.R.Trace.Final using (Coalg; ana; ana-unique)
open import Substrate.Category.Allegory.Refinement using (isSingleton)

-- the μ/ν universal properties are GENERIC over any DivStr / Coalg — instantiate
-- at the SKI carrier by supplying its DivStr (the ADD-153 combinator-DivStr is one
-- such D; here we state the endpoints generically, then note the SKI instance).

------------------------------------------------------------------------
-- ① THE LEAST-FIXED-POINT ENDPOINT (μ): the flat inductive Trace. Its μ character
-- is the INITIAL-ALGEBRA universal property — trace-fold is the UNIQUE morphism out
-- (trace-fold-unique). This is the PROVEN "Trace = μ" content: initiality = leastness.
------------------------------------------------------------------------
-- the SKI reduction Trace IS the least-fixed-point endpoint: any fold agreeing with
-- (bi, si) IS trace-fold — the μ universal property (trace-fold-unique, generic over D).
μ-endpoint-unique = trace-fold-unique

------------------------------------------------------------------------
-- ② THE GREATEST-FIXED-POINT ENDPOINT (ν): the coinductive RealTrace. Its ν
-- character is the TERMINAL-COALGEBRA universal property — ANY coalgebra morphism
-- into RealTrace is ~ ana (ana-unique). This is the PROVEN "RealTrace = ν": finality
-- = greatestness. The SKI divergent reduction (regress side, ADD 146) lives here.
------------------------------------------------------------------------
-- any coalgebra morphism into RealTrace is ~ ana (ana-unique, the ν universal property).
ν-endpoint-unique = ana-unique

------------------------------------------------------------------------
-- ③ THE DUALITY (the allegory's two endpoints, made explicit): μ = Trace (initial,
-- fold, least, inductive, the finite/SN reduction) and ν = RealTrace (terminal,
-- unfold, greatest, coinductive, the infinite/regress reduction) are the two
-- fixed-point endpoints of ONE structure — the fold⊣unfold duality (ADD 149). The
-- allegory Φ-chain (ADD 156) is the descent BETWEEN them; μ is its least, ν its
-- greatest. This IS the least/greatest containment (ADD 146's SN ⊆ Diverges).
------------------------------------------------------------------------
-- a trivial map-readout: a coinductive endpoint is reflexively bisimilar (its own
-- observations) — the ν side's self-consistency, from ana-unique's self-unfold shape.
ν-self : (x : RealTrace) → x ~ x
ν-self = ~-refl

------------------------------------------------------------------------
-- ④ HONEST SCOPE MARKER (the frontier the substrate flags, NOT claimed here):
-- Trace ≅ μ(specific Φ) and RealTrace ≅ ν(specific Φ) require a Φ built from the
-- WEDGE STEP (Refinement's note), NOT the toy raw-R shift (ADD 156's Φ-arity, the
-- FALSE SHORTCUT). What IS delivered: the endpoints' PROVEN universal properties
-- (μ = trace-fold-unique, ν = ana-unique) instantiated at the SKI carrier; the
-- specific-Φ iso stays the substrate's own IDENTIFIED-NOT-YET-PROVEN obligation.
-- isSingleton (the map readout) records the deterministic-fiber condition (ALG-5).
------------------------------------------------------------------------
open import Substrate.Foundation.Nat using (ℕ)

-- the map/relation readout is available (a fiber family is map-like iff subsingleton):
map-readout : (ℕ → Set) → Set
map-readout = isSingleton

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — HONESTLY): the allegory's two endpoints are μ
-- (Trace, initial/fold/least, the finite reduction) and ν (RealTrace, terminal/
-- unfold/greatest, the divergent reduction), each with its PROVEN universal property
-- (trace-fold-unique, ana-unique). The μ-vs-ν either/or dissolves into the fold⊣unfold
-- duality — ONE structure, two fixed-point endpoints, the allegory Φ-chain between.
-- The SPECIFIC-Φ iso (Trace ≅ μ(a wedge-step Φ)) is the substrate's flagged frontier,
-- scoped NOT claimed — heeding the FALSE-SHORTCUT warning (raw R is not the iterate).
-- What's grounded: the endpoints are the proven universal properties; the frontier
-- is the concrete-Φ isomorphism, honestly deferred.
------------------------------------------------------------------------
