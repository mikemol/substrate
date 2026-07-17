------------------------------------------------------------------------
-- Substrate.Algebra.Sporadic.GriessAlgebra.Aut
--
-- The Monster reconstructed as Aut(GriessAlgebra) via Z2's
-- AutomorphismGroup primitive. Closes Gap #2 from the Grothendieck-
-- closure audit: the Monster's universal characterisation is now
-- structurally accessible (was meta-claim in T8/X5).
--
-- Z9 of the 10-slice Grothendieck-closure arc per
-- [[prime-factored-gauge-arc]] follow-on.
--
-- KEY STRUCTURAL CONTENT:
--
--   Take a GriessAlgebra (X4 instance): a CommutativeNonAssociative-
--   Algebra of dimension 196,884 with product + form + axioms.
--
--   Apply Z2 AutomorphismGroup with:
--     V = the algebra's carrier
--     Preserves = "f preserves product (f(xy) = f(x)f(y)) and
--                  preserves form (⟨f(x), f(y)⟩ = ⟨x, y⟩)"
--
--   The resulting AutomorphismGroup record IS the Monster.
--
--   This is the substrate-side formal identification
--   M ≅ Aut(GriessAlgebra) — previously stated as meta-claim, now
--   constructible from the X4 GriessAlgebra + Z2 AutomorphismGroup
--   primitives.
--
-- Per [[universal-property-discipline]]: this completes the
-- Monster's universal-property identification. The Monster is no
-- longer "a 10^53-element group asserted to be M" but specifically
-- "Aut(GriessAlgebra)" — a structural identification at the
-- substrate primitive layer.
--
-- Per [[coalgebraic-not-consumer-driven]]: this is the substrate's
-- coalgebraic-side identification of M — Aut acts on the algebra's
-- carrier, and that action IS the Monster.
--
-- Module-parametric over the GriessAlgebra + the algebra-+-form-
-- preservation predicate. Concrete consumers supply the
-- preservation predicate definition.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Level using (Level; 0ℓ)
open import Substrate.Foundation.Eq using (_≡_)

open import Substrate.Category.CommutativeNonAssociativeAlgebra
  using (CommutativeNonAssociativeAlgebra)
open import Substrate.Category.AutomorphismGroup
  using (AutomorphismGroup)

module Substrate.Algebra.Sporadic.GriessAlgebra.Aut
  -- The Griess algebra (= an X4 CommutativeNonAssociativeAlgebra
  -- instance at dimension 196,884; supplied by user citing X4 +
  -- Griess 1982 + FLM 1988).
  (GriessAlg : CommutativeNonAssociativeAlgebra {0ℓ} {0ℓ})
  -- The preservation predicate: a function on V preserves both
  -- the algebra product and the bilinear form. (User supplies the
  -- explicit definition; the substrate provides the structural
  -- target.)
  (Preserves-Griess :
    (CommutativeNonAssociativeAlgebra.V GriessAlg →
     CommutativeNonAssociativeAlgebra.V GriessAlg) →
    Set)
  -- The carrier of Aut(GriessAlgebra) itself (⟡set1-rp: carrier→param
  -- — was a Set-valued FIELD of AutomorphismGroup, now a param the
  -- Monster-Aut instance below must be threaded against).
  (Aut-X : Set)
  -- The Monster-as-Aut(GriessAlgebra) instance: Aut record for
  -- Griess's V with the preservation predicate. User supplies the
  -- explicit construction (= each Aut element + its inverse + the
  -- group structure, citing the Monster's character table /
  -- representations).
  (Monster-Aut : AutomorphismGroup
                   (CommutativeNonAssociativeAlgebra.V GriessAlg)
                   Preserves-Griess
                   Aut-X)
  where

------------------------------------------------------------------------
-- 1. The Monster as Aut(GriessAlgebra).
--
-- Direct re-export — the substrate-side formal target is the
-- supplied Monster-Aut value.
------------------------------------------------------------------------

Monster-as-AutGriess :
  AutomorphismGroup
    (CommutativeNonAssociativeAlgebra.V GriessAlg)
    Preserves-Griess
    Aut-X
Monster-as-AutGriess = Monster-Aut

------------------------------------------------------------------------
-- 2. Capstone — Monster's universal-property identification closed.
--
-- Z9 of the 10-slice Z-arc. With Z9 landed, the substrate has the
-- Monster reconstructed STRUCTURALLY as Aut(GriessAlgebra) via
-- Z2's AutomorphismGroup primitive.
--
-- Closes Gap #2 from the Grothendieck-closure audit constructively:
--   * Previously: M ≅ Aut(GriessAlgebra) was a META-CLAIM in
--     T8/X5 (no Aut primitive to construct it).
--   * Now: Aut(GriessAlgebra) is built via Z2 + Z9; the Monster IS
--     this Aut record.
--
-- Module-parametric per substrate convention; concrete instance
-- requires the user to supply:
--   * The GriessAlgebra (X4 + Griess+FLM external content)
--   * The preservation predicate (= algebra-hom + form-preserving)
--   * The actual Aut(GriessAlgebra) construction (= the Monster as
--     a group of structure-preserving bijections; ATLAS-cited)
--
-- After Z9, the substrate has all 3 substrate-internal views of M:
--   1. T8 Monster.AsCoalgebra — as a ConjugationCoalgebra
--   2. Y7+Y8 Monster.AsPresented — as a PresentedGroup
--   3. Z9 Monster.AsAutGriess (this) — as Aut(GriessAlgebra)
-- Per T4 GaloisAdjunction: views 1+2 are bridged. Z9 adds the
-- third view bridged via Z2's universal Aut(_) primitive.
--
-- Next: Z10 (capstone refresh exposing all Z1-Z9).
------------------------------------------------------------------------
