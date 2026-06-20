------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.IRRetraction — Ⓤ.split
--
-- The jea IR→source retraction (the Ⓤ arc, jea/metalanguage/jea_extrude_ir.py)
-- formalized as an instance of the SPLIT-IDEMPOTENT apex
-- `Substrate.Algebra.Quotient.split-Canonical`.
--
-- The arc built, and validated on 133/133 real modules, a lossless round-trip
--     recon (decompose s) ≡ s
-- where `decompose` lowers a source into a SKELETON (the interned, shared
-- structure) PLUS a RESIDUE (the per-occurrence cofactor: literal values,
-- bound-name spellings, def names, field-tags, …), and `recon` (the extruder
-- fed the residue) rebuilds the source EXACTLY. That is precisely a retraction
-- F ∘ s ≡ id with the section going through a PRODUCT  Skeleton × Residue —
-- so the substrate's own `split-Canonical` makes it a `Canonical` for `ker recon`
-- with NO quotient type. "byte-grade is structurally impossible" was the wrong
-- frame: the residue is the kept cofactor (never-discard-residue), and keeping
-- it turns the lossy skeleton projection into this retraction.
--
-- The round-trip itself is an empirical, machine-checked property of the Python
-- extruder (Σ6 `chk_extrude_ir`: AST-faithful over the full language, byte-exact
-- via the CST carrier). Here it enters as the section/retraction HYPOTHESIS (the
-- honest conditional, per scoped-hypotheses discipline); given it, this module
-- DERIVES the Canonical with `--safe --without-K`, no postulates. A trivial
-- concrete instance (`example`) witnesses the hypothesis set is inhabitable.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.IRRetraction where

open import Agda.Primitive using (Level; _⊔_)
open import Substrate.Foundation.Eq using (_≡_; refl)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Algebra.Quotient using (ker-Quotient; split-Canonical)
  renaming (Canonical to Canonical⟦de760d07⟧)   -- shape-specialise: `Canonical` collides across 4 nodes

------------------------------------------------------------------------
-- The IR-retraction data, abstract over the three carriers + the maps.
--
--   lower   : the skeleton interning  (Source → Skeleton)        — the SHARED quotient part
--   capture : the residue cofactor    (Source → Residue)         — the per-occurrence remainder
--   extrude : recon from both         (Skeleton → Residue → Source)
--   round-trip : extrude (lower s) (capture s) ≡ s               — the 133/133 verified retraction
------------------------------------------------------------------------

module IR
  {ℓs ℓk ℓr : Level}
  (Source : Set ℓs) (Skeleton : Set ℓk) (Residue : Set ℓr)
  (lower   : Source → Skeleton)
  (capture : Source → Residue)
  (extrude : Skeleton → Residue → Source)
  (round-trip : (s : Source) → extrude (lower s) (capture s) ≡ s)
  where

  -- The representation space is the PRODUCT: skeleton (shared) × residue (cofactor).
  Repr : Set (ℓk ⊔ ℓr)
  Repr = Skeleton × Residue

  -- s : B → A — decompose a source into (skeleton, residue).
  decompose : Source → Repr
  decompose s = (lower s , capture s)

  -- F : A → B — recon a source from a (skeleton, residue) pair.
  recon : Repr → Source
  recon p = extrude (proj₁ p) (proj₂ p)

  -- F ∘ s ≡ id_Source : recon (decompose s) ≡ s — definitionally the round-trip.
  recon-decompose : (s : Source) → recon (decompose s) ≡ s
  recon-decompose = round-trip

  -- The apex: a retraction ⟹ the split idempotent decompose ∘ recon is a Canonical
  -- for ker recon (two Reprs that rebuild the same source — e.g. an ill-formed residue
  -- stream, or a non-canonical skeleton). The canonical form is `decompose ∘ recon`.
  ir-Canonical : Canonical⟦de760d07⟧ (ker-Quotient recon)
  ir-Canonical = split-Canonical recon decompose recon-decompose

------------------------------------------------------------------------
-- Non-vacuity: the hypothesis set is inhabitable. Take Source itself to be the
-- product Skeleton × Residue, lower = proj₁, capture = proj₂, extrude = pairing;
-- the round-trip is `refl` by the η-law for Σ. So `ir-Canonical` exists concretely.
------------------------------------------------------------------------

module example {ℓk ℓr : Level} (Skeleton : Set ℓk) (Residue : Set ℓr) where
  open IR (Skeleton × Residue) Skeleton Residue
          proj₁ proj₂ (λ k r → (k , r)) (λ _ → refl) public
