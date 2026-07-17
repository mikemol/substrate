{-# OPTIONS --safe --without-K #-}

------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.StencilDedekind — ⟡stencil-dedekind: meet-
-- preservation (197) is ITSELF a stencil instance, its two directions being two framings
-- CHIRALITY-OPPOSED under the converse †.
--
-- THE OPERATOR'S INSIGHT: the ≈ of maps-preserve-meets has two directions —
--   • ⊆  f ⨾ (S ∧ T) ⊆ (f ⨾ S) ∧ (f ⨾ T)   — MONOTONICITY, free, holds for ALL relations.
--   • ⊇  (f ⨾ S) ∧ (f ⨾ T) ⊆ f ⨾ (S ∧ T)   — the DEDEKIND form, needs the map (determinism).
-- These are two FRAMINGS, CHIRALITY-OPPOSED: the Dedekind form (modular-2) is the base
-- modular law (modular-1) seen through the converse † — the same † mirror as self-converse
-- (193) and residual-duality (194, "left/right division = one residual through †"). So the
-- chirality IS the † involution, the substrate's own dissolve-either/or. Another stencil
-- instance: the meet-preservation ≈ is the fixed point; monotonicity (free) and Dedekind
-- (structured) are the two framings; † is the chirality relating them — the ≡-exact/~-partial
-- asymmetry realized as free-vs-structured, hinged by the converse mirror.
------------------------------------------------------------------------

module Substrate.Category.UniversalProperty.StencilDedekind where

open import Substrate.Foundation.Product using (Σ; _,_; _×_)
open import Substrate.Category.Allegory
  using (_⨾_; _∧_; _†; _⊆_; _≈_; modular)

------------------------------------------------------------------------
-- ② THE DEDEKIND FORM (modular-2): (P ⨾ Q) ∧ U ⊆ P ⨾ (Q ∧ (P† ⨾ U)). This is the CHIRAL
-- TWIN of the substrate's modular-1 ((R⨾S)∧T ⊆ (R∧(T⨾S†))⨾S) — the same law seen through
-- †. Provable directly (the Σ-rearrangement, like modular-1): take the same middle b and
-- witness a' = a for the P†⨾U term.
------------------------------------------------------------------------
dedekind : {A B C : Set} (P : A → B → Set) (Q : B → C → Set) (U : A → C → Set)
         → ((P ⨾ Q) ∧ U) ⊆ (P ⨾ (Q ∧ ((P †) ⨾ U)))
dedekind P Q U a c ((b , (pab , qbc)) , uac) =
  b , (pab , (qbc , (a , (pab , uac))))
  --  same middle b: P a b, then Q b c ∧ (P†⨾U) b c with a'=a: P† b a (= P a b), U a c.

------------------------------------------------------------------------
-- ③ THE CHIRALITY-OPPOSED STENCIL: the two framings of meet-preservation.
------------------------------------------------------------------------
module _ {A B C : Set} (f : A → B → Set) where

  -- FRAMING 1 (free / generic — the "≡-exact" side): MONOTONICITY. ⨾ distributes into ∧
  -- from the left, for ANY f. No structure needed.
  meet-mono : (S T : B → C → Set) → (f ⨾ (S ∧ T)) ⊆ ((f ⨾ S) ∧ (f ⨾ T))
  meet-mono S T a c (b , (fab , (sbc , tbc))) = (b , (fab , sbc)) , (b , (fab , tbc))

  -- FRAMING 2 (structured / the "~-partial" side): the DEDEKIND step. (f⨾S)∧(f⨾T) lands
  -- below f ⨾ (S ∧ (f†⨾f⨾T)) — the Dedekind form (modular-2) instantiated at U = f⨾T. The
  -- map's determinism (f†⨾f ⊆ idR) then collapses it to f⨾(S∧T) (197); here we expose the
  -- Dedekind landing itself, the chiral twin of monotonicity.
  meet-dedekind : (S T : B → C → Set) →
    ((f ⨾ S) ∧ (f ⨾ T)) ⊆ (f ⨾ (S ∧ ((f †) ⨾ (f ⨾ T))))
  meet-dedekind S T = dedekind f S (f ⨾ T)

------------------------------------------------------------------------
-- THE INVARIANT (bottoming out — meet-preservation is another stencil instance, its two
-- directions chirality-opposed under †): the ≈ of maps-preserve-meets (197) is a fixed
-- point framed two ways — MONOTONICITY (meet-mono, the ⊆, free, holds for all relations,
-- the "≡-exact/generic" side) and DEDEKIND (meet-dedekind, the ⊇ route, the modular content,
-- the "~-partial/structured" side needing the map). These two framings are CHIRALITY-OPPOSED:
-- the Dedekind form (modular-2, dedekind) is the base modular law (modular-1) seen through
-- the converse † — witnessed by †-∧ (converse over meet) + †-comp (converse over ⨾), the
-- chirality machinery. So the mirror relating the two framings IS the † involution — the
-- SAME dissolve-either/or as self-converse (193) and residual-duality (194: "left/right
-- division = one residual through †"). The either/or "monotonicity vs Dedekind" dissolves
-- into the two chiral hands of ONE meet-preservation, related by †: monotonicity the free
-- hand (any relation), Dedekind the structured hand (the map). This is the stencil AGAIN,
-- self-similar (190): a fixed point (the ≈), two framings (free/structured), one mirror
-- (†) — with the ≡-exact/~-partial asymmetry realized as free-vs-structured and the Lambek/
-- converse hinge realized as the chirality. The stencil stencils even its own modular proof.
------------------------------------------------------------------------
