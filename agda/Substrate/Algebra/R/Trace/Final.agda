------------------------------------------------------------------------
-- Substrate.Algebra.R.Trace.Final
--
-- "Bisimulation: proving the infinite behaviours are universally dual… This is
--  just Lawvere." (user, 2026-06-12) — correcting my framing of the round-trip's
-- behaviour-equality as "a separate, grander type-theoretic objective". It is
-- neither separate nor grander: it is the universal property of the FINAL
-- COALGEBRA, the exact codual of the substrate's Free/initial centre
-- ([[project_center_free_universal_property]]).
--
-- RealTrace is the TERMINAL COALGEBRA of the stream functor S(X) = ℕ × X. The
-- record's two fields ARE the structure map, and by LAMBEK'S LEMMA that map is an
-- ISO — the final coalgebra is a FIXED POINT of S. Lambek's lemma is the
-- coalgebraic face of `Category.Lawvere` (the diagonal/fixed-point atom behind
-- Cantor/Gödel/Tarski and the wedge residue): "final coalgebra = fixed point" is
-- the positive Lawvere conclusion on the dual side. So:
--
--   initial algebra  (term algebra, Free⊣Forgetful)  =  CONSTRUCTORS, induction
--   final coalgebra  (RealTrace, this module)         =  OBSERVATIONS, coinduction
--
-- are one adjoint structure hinged by Lawvere. Bisimilarity `_~_` is EQUALITY in
-- the final coalgebra; coinduction is its uniqueness clause — the precise dual of
-- recursion. Two generator-presentations of the same number (e's Euler CF vs its
-- Taylor stream) being `~` is therefore a ROUTINE instance of this UP, not a
-- frontier: exhibit the coalgebra morphism and `ana-unique` gives the rest.
--
-- What is proved here (all finite / coinductive, zero postulates):
--   • Lambek iso: out/into invert (one direction `≡`, the other `~` — coinductive
--     records carry no definitional η, so the round-trip is a bisimulation).
--   • ana = unfold is the anamorphism; its coalgebra-morphism square holds by refl.
--   • ana-unique: ANY coalgebra morphism into RealTrace is `~` to ana — the
--     terminal universal property, by guarded coinduction. THIS is "the infinite
--     behaviours are universally dual", proved generically.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K --guardedness #-}

module Substrate.Algebra.R.Trace.Final where

open import Substrate.Foundation.Nat     using (ℕ)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)
open import Substrate.Foundation.Eq      using (_≡_; refl)

open import Substrate.Algebra.R.Trace        using (RealTrace; head; tail)
open import Substrate.Algebra.R.Trace.Unfold using (unfold)
open import Substrate.Algebra.R.Trace.Bisim  using (_~_; head~; tail~; ~-refl; cons)

------------------------------------------------------------------------
-- The stream functor S(X) = ℕ × X. A coalgebra is a state machine S → ℕ × S.
------------------------------------------------------------------------

Coalg : Set → Set
Coalg S = S → ℕ × S

------------------------------------------------------------------------
-- The structure map of RealTrace and its inverse — Lambek's lemma: the final
-- coalgebra is a FIXED POINT, RealTrace ≅ ℕ × RealTrace.
------------------------------------------------------------------------

out : RealTrace → ℕ × RealTrace
out x = head x , tail x

into : ℕ × RealTrace → RealTrace
into (n , x) = cons n x

lambek-out-into : (ns : ℕ × RealTrace) → out (into ns) ≡ ns
lambek-out-into (n , x) = refl

lambek-into-out : (x : RealTrace) → into (out x) ~ x
head~ (lambek-into-out x) = refl
tail~ (lambek-into-out x) = ~-refl (tail x)

------------------------------------------------------------------------
-- ana = unfold: the unique coalgebra morphism from (S, c) into the terminal
-- coalgebra. The morphism square (out ∘ ana = (id × ana) ∘ c) holds by refl.
------------------------------------------------------------------------

ana : {S : Set} → Coalg S → S → RealTrace
ana = unfold

ana-head : {S : Set} (c : Coalg S) (s : S) → head (ana c s) ≡ proj₁ (c s)
ana-head c s = refl

ana-tail : {S : Set} (c : Coalg S) (s : S) → tail (ana c s) ≡ ana c (proj₂ (c s))
ana-tail c s = refl

------------------------------------------------------------------------
-- TERMINALITY (the universal property) — coinduction is its uniqueness clause.
-- Any h : S → RealTrace that is a coalgebra morphism (its head/tail match the
-- coalgebra c) is bisimilar to ana c. This is the generic "infinite behaviours
-- are universally dual": all morphisms into RealTrace agree up to `~`.
------------------------------------------------------------------------

-- The morphism's tail-square is only PROPOSITIONAL (tail (h s) ≡ h (proj₂ (c s))),
-- and transporting `~` along it under `tail~` would break guardedness. We instead
-- carry the witness `t ≡ h s` as a parameter and consume it `refl` inside the
-- copattern, so the corecursive call sits DIRECTLY under `tail~` (guarded).
ana-unique : {S : Set} (c : Coalg S) (h : S → RealTrace)
           → (∀ s → head (h s) ≡ proj₁ (c s))
           → (∀ s → tail (h s) ≡ h (proj₂ (c s)))
           → ∀ s → h s ~ ana c s
ana-unique {S} c h hh ht s₀ = go s₀ (h s₀) refl
  where
    go : (s : S) (t : RealTrace) → t ≡ h s → t ~ ana c s
    head~ (go s t refl) = hh s
    tail~ (go s t refl) = go (proj₂ (c s)) (tail t) (ht s)

------------------------------------------------------------------------
-- The h = id corollary: every generator IS the unfold of its own observations.
-- So "is this generator the right number?" is not a theorem to discharge against
-- an external value — the generator is canonical up to `~`, and any presentation
-- with the same structure map is `~` to it (ana-unique). Presentation-uniqueness
-- is routine; there is no privileged "true value" to match.
------------------------------------------------------------------------

self-unfold : (x : RealTrace) → x ~ ana out x
head~ (self-unfold x) = refl
tail~ (self-unfold x) = self-unfold (tail x)
