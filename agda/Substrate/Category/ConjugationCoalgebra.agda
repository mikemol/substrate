------------------------------------------------------------------------
-- Substrate.Category.ConjugationCoalgebra
--
-- The top-down primitive: a group equipped with its conjugacy-class
-- structure. Captures "introspection-and-diffraction" — the group's
-- self-action via conjugation (= introspection) decomposed into
-- conjugacy-class orbits (= diffraction).
--
-- The "coalgebra" framing: conjugation γ : G → (G → G), `γ x y = x·y·x⁻¹`,
-- is an Endomap-valued morphism on G (the group acts on itself by
-- inner automorphism). The conjugacy classes are the orbits of this
-- action; partition data is the coalgebra's "diffraction pattern."
--
-- T3 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. The top-down side of the Galois
-- adjunction (T4) bridges this with PresentedGroup (T2):
--
--   * PresentedGroup: bottom-up (generators + relations + ∼ quotient)
--   * ConjugationCoalgebra: top-down (conjugacy classes + introspection)
--
-- For groups where one direction is intractable (e.g., the Monster,
-- where the presentation's normal form is intractable but the
-- conjugacy class structure is published in the ATLAS), having BOTH
-- primitives + the Galois bridge lets the substrate work in whichever
-- direction is constructively accessible.
--
-- Per [[coalgebraic-not-consumer-driven]]: this is the substrate's
-- coalgebraic primitive at the group-theoretic level. The Coalgebra
-- (Endomap) primitive is at the per-element level (fixed points,
-- finite-order); ConjugationCoalgebra is at the conjugacy-class
-- level (introspection-of-the-whole-group).
--
-- Per [[categorical-name-first]]: "conjugation coalgebra" / "class
-- algebra" / "centralizer-and-class data" — standard categorical
-- naming. The character table (rational-valued data per class
-- pair) is the cohomological extension; landed as a follow-on.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ConjugationCoalgebra where

open import Substrate.Foundation.Level using (Level; _⊔_) renaming (suc to lsuc)

private
  variable
    ℓ : Level

------------------------------------------------------------------------
-- The ConjugationCoalgebra record.
--
-- Bundles a group (G, ·, ε, ⁻¹) with its conjugacy-class structure:
--   * Class : indexing set for conjugacy classes
--   * rep : Class → G, one representative per class
--   * in-class : Class → (G → Set), membership predicate per class
--
-- Axioms (the "this IS a class structure" obligations):
--   * in-class-rep : the representative is in its own class
--   * conjugation-respects-class : conjugating by any g preserves
--     class membership (= the orbit property)
--
-- Presupposed (not internal): the group axioms (assoc, identity,
-- inverse laws) for (·, ε, ⁻¹). Substrate-pattern minimum-axiom
-- record — the user supplies a genuine group + a genuine class
-- partition, this primitive packages them.
--
-- INTERNAL (load-bearing): conjugation-respects-class is what makes
-- the class structure a coalgebra (= the conjugation Endomap
-- preserves classes). Without this, the partition isn't structurally
-- compatible with the group action.
------------------------------------------------------------------------

record ConjugationCoalgebra : Set (lsuc ℓ) where
  constructor mkConjugationCoalgebra
  field
    G        : Set ℓ
    _·_      : G → G → G
    ε        : G
    _⁻¹      : G → G

    Class    : Set ℓ
    rep      : Class → G
    in-class : Class → G → Set ℓ

    -- Class structure axioms.
    in-class-rep : (c : Class) → in-class c (rep c)
    conjugation-respects-class :
      (g : G) (c : Class) (h : G) →
      in-class c h →
      in-class c ((g · h) · (g ⁻¹))

------------------------------------------------------------------------
-- Capstone — primitive in place.
--
-- T3 of the prime-factored-gauge arc per
-- [[prime-factored-gauge-arc]]. Foundation for T4 (GaloisAdjunction);
-- the top-down side of the Galois bridge to PresentedGroup (T2).
--
-- Concrete instances expected (T8 of the arc):
--   * Monster M: G = an abstract carrier; 194 conjugacy classes from
--     ATLAS; class representatives + membership predicates populated
--     from external data. The substrate-side identification with
--     "the Monster" lives in commentary (since CFSG-uniqueness is
--     external).
--   * Baby Monster B: as `centralizer-of` projection from the
--     Monster's 2A class (followed by quotient by ⟨z⟩).
--   * Any classical group (S_n, GL(n, F_q), PSL(n, F_q)) with
--     character tables from standard references.
--
-- Follow-on extensions:
--   * `ConjugationCoalgebra.WithCharacters` adds the character table
--     (Char : Class → Class → ℚ); brings the full ATLAS-style
--     diffraction data.
--   * `CentralizerDescent` formalises the recursive Happy Family
--     hierarchy (each Class has a centralizer that is itself a
--     ConjugationCoalgebra).
--
-- Per [[shadow-architecture]]: this completes the bottom-up / top-down
-- DBE-foundational pair (T2 + T3). T4 (GaloisAdjunction) is next,
-- bridging them.
------------------------------------------------------------------------
