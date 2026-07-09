{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.DiagonalLawvereCarrier — ⟡diagonal-lawvere-coalg-carrier:
-- landing Lawvere's POSITIVE direction (point-surjection ⟹ fixed point) on the escape's carrier, and
-- honestly DISTINGUISHING the two "reflexivities" the arc conflated.
--
-- The catalog-check (ADD 244, standing) found the repo ALREADY has BOTH halves: Lawvere.lawvere-fixed-point
-- (the generic positive theorem) and UniversalProperty.FixedPoint (ι/promote — a concrete reflexive-object
-- realization, "the category of arrow categories has a fixed point"). So this module REUSES, not rebuilds.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: Reflexive (the
-- point-surjection-carrier record wrapping Lawvere.PointSurjective), reflexive-forces-fixpoint (a Reflexive
-- carrier ⟹ every endomap has a fixed point, = lawvere-fixed-point), ⊤-reflexive : Reflexive ⊤ ⊤ (a non-vacuous instance).
-- The framing ('the escape carrier', 'the two reflexivities meet') is (prose: illuminating, NOT a theorem
-- of this slice; the genuine coinductive/SKI reflexive witness is scoped below).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.DiagonalLawvereCarrier where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Foundation.Unit using (⊤; tt)
open import Substrate.Category.Lawvere using (PointSurjective; lawvere-fixed-point)

------------------------------------------------------------------------
-- ① THE REFLEXIVE CARRIER (Lawvere's positive hypothesis, packaged). A carrier A that point-surjects
--    onto its own V-valued function space (A → V) — the reflexive-object / self-application condition.
--    This is the LAWVERE reflexivity: representing your own function space. (NOT the Lambek reflexivity
--    νF ≅ F(νF) — see the invariant note; they are DIFFERENT, and the arc conflated them.)
------------------------------------------------------------------------
record Reflexive (A V : Set) : Set where
  field
    app  : A → A → V
    surj : PointSurjective app

------------------------------------------------------------------------
-- ② A REFLEXIVE CARRIER FORCES THE ESCAPE'S FIXED POINT. This is Lawvere's positive direction landed on
--    the carrier: if A is reflexive onto V, EVERY endomap f : V → V has a fixed point. = lawvere-fixed-point
--    (REUSED, not re-derived). The "escape" (a fixed point exists for the diagonal endomap) is exactly what
--    a reflexive carrier forces — so the escape lives on a LAWVERE-reflexive carrier.
------------------------------------------------------------------------
reflexive-forces-fixpoint :
  {A V : Set} → Reflexive A V → (f : V → V) → Σ V (λ v → f v ≡ v)
reflexive-forces-fixpoint r f = lawvere-fixed-point (Reflexive.app r) (Reflexive.surj r) f

------------------------------------------------------------------------
-- ③ NON-VACUITY (the discharge-with-instance habit, 230): ⊤ is trivially reflexive — every g : A → ⊤ is
--    the constant λ _ → tt = app a. So reflexive-forces-fixpoint is inhabited (tt is the forced fixed
--    point). A TRIVIAL instance (V = ⊤ has only the trivial endomap), but real: the framework is non-empty.
------------------------------------------------------------------------
-- A = ⊤ (POINTED, so PointSurjective has a witness point) and V = ⊤. Every g : ⊤ → ⊤ is the constant
-- tt-map = app tt, on the nose (both sides compute to λ _ → tt). The point-surjection witness is tt : ⊤.
⊤-reflexive : Reflexive ⊤ ⊤
⊤-reflexive = record
  { app  = λ _ _ → tt
  ; surj = λ g → tt , refl }

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the arc conflated TWO reflexivities; they are distinct, and the escape's
-- POSITIVE direction needs the LAWVERE one, realized by a self-applicative carrier): the either/or "is the
-- ν-fixed-point (Lambek, 234) the reflexivity that forces the escape's fixed point?" bottoms out in a
-- DISTINCTION, not a conflation:
--   * LAMBEK reflexivity — νF ≅ F(νF) (DiagonalEscapeCoalg.prediction-is-nu-fixed-point): the object is a
--     fixed point of the FUNCTOR. This grounds escape=FINALITY (234): behaviour canonical up to ~.
--   * LAWVERE reflexivity — A point-surjects onto (A → V) (Reflexive, ①): the object represents its own
--     FUNCTION SPACE. This grounds escape=a-FIXED-POINT-EXISTS (②, lawvere-fixed-point): every endomap
--     has a fixed point (the 221 `full`).
-- These are DIFFERENT reflexivities (functor-fixed-point vs function-space-representation); the arc used
-- Lambek for finality (234) and Lawvere for the fixed point (221/245), and CONFLATED them as "the
-- coinductive escape". Honestly separated here: the escape's POSITIVE face (a fixed point exists) is
-- Lawvere-reflexivity (②); the escape's FINALITY face (canonical up to ~) is Lambek-reflexivity (234).
-- A carrier that is BOTH — a self-applicative coinductive object (SKI/Y, where self-application gives Y's
-- fixed point AND the behaviour is a ν-fixed-point) — is where the two meet. That carrier is the genuine
-- target, scoped below.
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = Reflexive (Lawvere's positive hypothesis packaged),
-- reflexive-forces-fixpoint (= lawvere-fixed-point, REUSED), the non-vacuous ⊤ instance, and the
-- Lambek-vs-Lawvere DISTINCTION (the arc's conflation, corrected). SCOPED (prose, not this slice): (a) a
-- GENUINE non-trivial coinductive reflexive carrier — the SKI/Y self-applicative object (the repo's
-- NewmanSKI/SKIReductionToList, catalog-found 244) as a Reflexive witness, so lawvere-fixed-point lands on
-- the OBSERVER's behaviour type, not just ⊤ — ⟡diagonal-lawvere-ski-carrier (the deepest grounding; needs
-- the SKI machinery + the Y-combinator = the constructive point-surjection); (b) the formal proof that no
-- SET carrier is Lawvere-reflexive onto a fpf-V (Cantor forbids it — why the trivial ⊤ is the only
-- constructible SET instance and the genuine one is coinductive/computational). What's grounded: the
-- escape's positive face IS Lawvere-reflexivity, distinct from its finality face (Lambek), landed on the
-- carrier via lawvere-fixed-point (reused), with the SKI/Y coinductive witness scoped.
------------------------------------------------------------------------
