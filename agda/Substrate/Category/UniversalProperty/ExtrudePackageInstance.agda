{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudePackageInstance — ⟡extrude-package-instance: a SHARED RECORD
-- capturing this arc's extruder structure at the REDUCTION level, with Tm⟦533ef80d⟧/SKI as an INSTANCE — the refactor
-- ExtruderLambekRealigned's lesson prescribes (package as an instance, don't re-declare). ExtruderFix's
-- CombinatorAlgebra {C; _·_; S K; K-law/S-law at ≡} is the ≡-QUOTIENT combinator algebra; SKI's laws hold
-- only at ⇒* (reduction), so Tm⟦533ef80d⟧ is not a definitional CombinatorAlgebra — the honest package is a
-- REDUCTION-level record (laws at ⇒*), of which CombinatorAlgebra is the ≡-quotient. This record bundles the
-- arc's three centers: the combinator laws (⇒*), a fixed-point extruder (Y-of, 265), and the step reducer
-- (275b/276a) — my modules provide the SKI INSTANCE.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: the ReductionExtruder
-- record (carrier + _·_ + S/K/I + K-law/S-law/I-law at ⇒* + a fixed-point extruder), and ski-extruder (the
-- Tm⟦533ef80d⟧/SKI INSTANCE — the laws from the β-rules, the fixed point from Y-of). The framing ('CombinatorAlgebra is
-- the ≡-quotient; package-as-instance per ExtruderLambekRealigned') is (prose: ExtruderFix + the 274 study).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudePackageInstance where

open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; I; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
import Substrate.Algebra.R.Trace.SKIReductionToList as R
open R using (_⇒_; β-I; β-K; β-S)
open import Substrate.Foundation.RewriteConfluence (R._⇒_) using (_⇒*_; done; _◅_)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of; Y-fix)

------------------------------------------------------------------------
-- ① THE SHARED RECORD (reduction-level): a carrier with application, S/K/I, the combinator laws AT ⇒*
--    (β-reduction — the honest SKI level; CombinatorAlgebra is this quotiented to ≡), and a fixed-point
--    extruder (every f has a fixed point reachable by ⇒* — Lawvere-positive). This is the arc's center.
------------------------------------------------------------------------
record ReductionExtruder : Set₁ where
  field
    Ċ    : Set
    _⊙_  : Ċ → Ċ → Ċ
    Ṡ Ḱ İ : Ċ
    _↠_  : Ċ → Ċ → Set                                   -- the reduction relation (⇒*)
    K-law : (x y : Ċ)   → ((Ḱ ⊙ x) ⊙ y) ↠ x
    S-law : (x y z : Ċ) → ((((Ṡ ⊙ x) ⊙ y) ⊙ z)) ↠ (((x ⊙ z) ⊙ (y ⊙ z)))
    I-law : (x : Ċ)     → (İ ⊙ x) ↠ x
    extrude   : Ċ → Ċ                                     -- the fixed-point extruder (Y-of)
    extrude-fix : (f : Ċ) → (extrude f) ↠ (f ⊙ (extrude f))  -- the extruded fixed point (Lawvere-positive)

------------------------------------------------------------------------
-- ② THE SKI INSTANCE: Tm⟦533ef80d⟧ satisfies the reduction-extruder — the laws are the β-rules (at ⇒*), the extruder
--    is Y-of (265), its fixed point Y-fix. So the whole arc (μ/265, self-interp/266, reversal/268, nerve/269-
--    275) lives on THIS instance, and cites ExtruderFix/CombinatorAlgebra as the ≡-quotient.
------------------------------------------------------------------------
ski-extruder : ReductionExtruder
ski-extruder = record
  { Ċ = Tm⟦533ef80d⟧ ; _⊙_ = _∙_ ; Ṡ = S ; Ḱ = K ; İ = I ; _↠_ = _⇒*_
  ; K-law = λ x y → β-K x y ◅ done
  ; S-law = λ x y z → β-S x y z ◅ done
  ; I-law = λ x → β-I x ◅ done
  ; extrude = Y-of
  ; extrude-fix = Y-fix
  }

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the arc PACKAGES as an instance of a shared reduction-extruder record, not
-- a pile of separate modules; CombinatorAlgebra is its ≡-quotient): ExtruderLambekRealigned's lesson —
-- package-as-instance, don't re-declare — applied to the whole arc. The ReductionExtruder record (①) bundles
-- the arc's centers (combinator laws at ⇒*, a fixed-point extruder), and ski-extruder (②) is the Tm⟦533ef80d⟧/SKI
-- INSTANCE: the laws are the β-rules, the extruder is Y-of (265), its fixed point Y-fix (Lawvere-positive).
-- CombinatorAlgebra (ExtruderFix, laws at ≡) is the ≡-QUOTIENT of this record — SKI's laws hold at ⇒*, and
-- quotienting ⇒* to ≡ (the confluence-observation, 266) recovers CombinatorAlgebra. So the arc is one
-- instance of one shared structure, citing the substrate's ExtruderFix as its quotient — reuse + package,
-- no duplication, no spook. Chain: 274 (ExtruderFix/the extruder line) → 275cd (cite) → 276b (package as
-- an instance).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = ReductionExtruder (the shared record) + ski-extruder (the Tm⟦533ef80d⟧
-- INSTANCE — β-laws + Y-of fixed point). SCOPED (reused-in-spirit): the actual functor ReductionExtruder →
-- CombinatorAlgebra (quotient ⇒* by confluence to ≡ — ⟡extrude-quotient-to-combinatoralgebra); folding my
-- other modules (μ/self-interp/nerve) through this record's fields (a mechanical refactor —
-- ⟡extrude-package-fold). What's grounded: the arc IS an instance of a shared reduction-extruder record,
-- CombinatorAlgebra its ≡-quotient — packaged, not re-declared.
------------------------------------------------------------------------
