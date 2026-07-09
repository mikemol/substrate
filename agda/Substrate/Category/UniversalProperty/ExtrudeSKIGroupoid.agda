{-# OPTIONS --safe --without-K --guardedness #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.ExtrudeSKIGroupoid — ⟡extrude-ski-quotient: the constructive
-- Tm⟦533ef80d⟧/≈ quotient AS A GROUPOID (user's steer: search groupoids). The 250 gap ("the literal ExtruderFix
-- ≡-record needs a quotient type Tm⟦533ef80d⟧/≈, blocked as a HIT") DISSOLVES: a setoid IS a thin groupoid — an
-- equivalence where every morphism is invertible by sym (StencilGroupoid's own statement) — and THAT is
-- the constructive quotient, no HIT needed. So Tm⟦533ef80d⟧/≈ is realized as the convertibility groupoid, and the
-- combinator-algebra structure + Y-of live on it as internal (up-to-≈) data.
--
-- The catalog-check (244, standing) + the groupoid search found the pattern NAMED: StencilGroupoid
-- ("a setoid-as-groupoid = an equivalence where every morphism/proof is invertible by sym") and
-- IsoGroupoid (the funext-free SETOID-ENRICHMENT route: morphism-equality is the setoid, laws hold
-- WITHOUT funext). This module applies that pattern to ≈ (250) — REUSING the equivalence, exhibiting it
-- as a groupoid, the constructive Tm⟦533ef80d⟧/≈.
--
-- COMMENT HYGIENE (agda_comment_hygiene): the MACHINE-CHECKED content is EXACTLY: ≈-inv (every ≈-morphism
-- is invertible = the groupoid property, by ≈sym), and the combinator/fixpoint data lifted to ≈ (reused
-- from 250). The framing ('Tm⟦533ef80d⟧/≈ as a groupoid IS the quotient', 'the HIT is dissolved') is (prose:
-- constructive-quotient-via-groupoid; the LITERAL CategoryOf instance with its ≡-laws on morphisms is
-- scoped — it needs morphism proof-irrelevance / setoid-enrichment à la IsoGroupoid).
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.ExtrudeSKIGroupoid where

open import Substrate.Foundation.Product using (Σ; _,_)
open import Substrate.Algebra.R.Trace.SKIShedDuality using (S; K; _∙_) renaming (Tm to Tm⟦533ef80d⟧)
open import Substrate.Category.UniversalProperty.ExtrudeSKISetoid
  using (_≋_; K-law-≋; S-law-≋; fix-law-≋; ski-HasFix)
open import Substrate.FUSep.ConversionCongruence using (ARS; _≈_; ≈refl; ≈sym; ≈trans)
open import Substrate.Category.UniversalProperty.ExtrudeSKISetoid using (ski-ARS)
open import Substrate.Category.UniversalProperty.DiagonalYCombinator using (Y-of)

------------------------------------------------------------------------
-- ① Tm⟦533ef80d⟧/≈ IS A GROUPOID (the constructive quotient). Objects = Tm⟦533ef80d⟧; a morphism a → b is a proof a ≋ b
--    (convertibility, 250). It is a groupoid: identity = ≈refl, composition = ≈trans, and EVERY morphism
--    is invertible — its inverse is ≈sym. This is the setoid-as-groupoid (StencilGroupoid), and it IS the
--    quotient Tm⟦533ef80d⟧/≈ constructively: "equality of objects" = an invertible morphism = ≋.
------------------------------------------------------------------------
Hom : Tm⟦533ef80d⟧ → Tm⟦533ef80d⟧ → Set
Hom a b = a ≋ b

hom-id : (a : Tm⟦533ef80d⟧) → Hom a a
hom-id a = ≈refl

hom-∘ : {a b c : Tm⟦533ef80d⟧} → Hom b c → Hom a b → Hom a c
hom-∘ g f = ≈trans f g

-- the GROUPOID property: every morphism is invertible (by ≈sym). This is what makes ≈ a QUOTIENT
-- equality (objects equal-up-to-iso ⟺ ≋) rather than a mere preorder.
≈-inv : {a b : Tm⟦533ef80d⟧} → Hom a b → Hom b a
≈-inv f = ≈sym f

------------------------------------------------------------------------
-- ② THE COMBINATOR ALGEBRA LIVES ON THE QUOTIENT GROUPOID. On Tm⟦533ef80d⟧/≈, the S/K laws and the fixpoint law
--    are EQUALITIES (invertible morphisms), not mere reductions — because a Hom IS the quotient-equality.
--    So (Tm⟦533ef80d⟧/≈, ∙) is a combinator algebra with Y-of the fixpoint, at the quotient's OWN equality.
------------------------------------------------------------------------
K-eq : (x y : Tm⟦533ef80d⟧) → Hom ((K ∙ x) ∙ y) x
K-eq = K-law-≋

S-eq : (x y z : Tm⟦533ef80d⟧) → Hom (((S ∙ x) ∙ y) ∙ z) ((x ∙ z) ∙ (y ∙ z))
S-eq = S-law-≋

fix-eq : (f : Tm⟦533ef80d⟧) → Hom (Y-of f) (f ∙ (Y-of f))
fix-eq = fix-law-≋

-- the fixpoint, as quotient data: for every f, an object v = Y-of f with an ISO (invertible morphism)
-- v ≅ f · v. On the quotient groupoid this IS "v ≡ f · v" — the literal HasFix, at the quotient equality.
quotient-HasFix : (f : Tm⟦533ef80d⟧) → Σ Tm⟦533ef80d⟧ (λ v → Hom v (f ∙ v))
quotient-HasFix = ski-HasFix

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — the "quotient type needs a HIT" boundary DISSOLVES via the groupoid:
-- Tm⟦533ef80d⟧/≈ IS the convertibility groupoid, and the combinator algebra + Y-of live on it at the quotient's own
-- equality): the either/or "either a HIT quotient (unavailable --safe) or no literal ExtruderFix instance"
-- (250) dissolves — a setoid IS a thin GROUPOID (an equivalence where every morphism is invertible by sym,
-- StencilGroupoid's own statement), and that groupoid IS the constructive quotient Tm⟦533ef80d⟧/≈. Objects = Tm⟦533ef80d⟧;
-- Hom a b = a ≋ b; identity/compose/INVERSE = ≈refl/≈trans/≈sym (①). On this quotient, "a ≡ b" MEANS "an
-- invertible Hom a b" = ≋, so the S/K laws and Y-of's fixpoint (②) are EQUALITIES at the quotient's own
-- equality — the literal ExtruderFix structure, realized WITHOUT a HIT. The user's steer (groupoids) is the
-- key: the quotient the extruder needs is not a missing type former, it is the groupoid ≈ already is.
-- Chain: 249 (extruder=fixed point) → 250 (gap closed at ≈, a setoid) → 251 (the setoid IS the groupoid =
-- the constructive quotient; the combinator algebra lives on it).
--
-- HONEST BOUNDARY (⟡H-overclaim): GROUNDED = Tm⟦533ef80d⟧/≈ as a groupoid (Hom/id/∘/inv, ≈-inv the invertibility) +
-- the combinator laws + Y-of's HasFix as quotient-equality data. SCOPED: the LITERAL CategoryOf/ExtruderFix
-- record instance — CategoryOf's laws (left-id/right-id/assoc) are stated at propositional ≡ ON MORPHISMS
-- (Hom-proofs), so instantiating it needs morphism proof-irrelevance or the setoid-ENRICHMENT IsoGroupoid
-- uses (morphism-equality = a setoid, laws WITHOUT funext) — a packaging step (⟡extrude-ski-catof), NOT a
-- new HIT. So the HIT boundary (250) is GONE; what remains is the funext-free CategoryOf enrichment
-- IsoGroupoid already demonstrates — reuse it to package (⟡extrude-ski-catof). What's grounded: Tm⟦533ef80d⟧/≈ is
-- the constructive quotient (a groupoid), and the combinator algebra + Y-of live on it — the extruder's
-- ≡-structure realized at the quotient equality, the user's groupoid steer dissolving the HIT boundary.
------------------------------------------------------------------------
