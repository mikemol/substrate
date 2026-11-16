------------------------------------------------------------------------
-- Substrate.Algebra.Quotient.KerRel
--
-- Defines: KerRel
-- ⟡cap-128-forcing: one lemma, one elaboration unit (split horizontally
-- out of Substrate.Algebra.Quotient; no barrel re-exports these siblings).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.Quotient.KerRel where

open import Agda.Primitive
open import Substrate.Foundation.Eq



------------------------------------------------------------------------
-- 3½. Retraction ⟹ Canonical: the SPLIT-IDEMPOTENT apex.
--
-- A quotient by `ker F` (F : A → B) is realized constructively WITHOUT a
-- quotient type exactly when F SPLITS — a section s : B → A with F ∘ s ≡ id.
-- Then e = s ∘ F : A → A is idempotent (a split idempotent / Karoubi), and e
-- is a `Canonical` form for `ker F`: the canonical representatives are its
-- image. So "no quotient types under --safe --without-K" is a non-issue — a
-- lossless round-trip (the ℚ↔R retraction, eval/reify, …) IS a retraction,
-- hence a section-based quotient.
--
-- This is the apex of a scattered cluster, each an (F, s, F∘s≡id) retraction
-- whose split idempotent is its canonical form: eval/reify (UPTerm/≈ᵤ;
-- `split-Canonical eval reify eval-reify`), ℚ `reduce`, the wedge `recon`
-- (a ≡ recon q b r), the EEA CF-shape, CRT `combine`, Coxeter `normalize`,
-- GenericHodgeStar `star`/`star-inv`, BeckChevalley section/retraction. The
-- "which quotient" either/or (raw / semantic / presented) collapses: each is
-- `ker (fold into a target)`; choosing the quotient = choosing the target;
-- and when that fold splits, this lemma realizes it. (cf. foldUPTerm = the
-- free-category universal extension; eval = its instance; UP4 = ker eval.)
------------------------------------------------------------------------

-- The kernel of any map, as a relation: x ≈ y iff F sends them to the same B.
KerRel : {a b : Level} {A : Set a} {B : Set b} → (A → B) → A → A → Set b
KerRel F x y = F x ≡ F y
