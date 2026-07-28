------------------------------------------------------------------------
-- Substrate.TokiPona.ModifierBilinear
--
-- T4 of the linguistic Rosetta arc's linear-side per
-- [[project-linguistic-rosetta-arc]]. Head-modifier composition on
-- the semantic vector space.
--
-- DESIGN-LEVEL CORRECTION (recorded per [[feedback-comments-dont-overclaim]]
-- and [[feedback-negative-findings-in-corpus]] caution):
--
-- The arc plan called this slice "ModifierBilinear" with bilinearity
-- as the headline universal property. Bilinearity in the strict
-- V × V → V sense (linear in each argument with the other fixed,
-- ADDITIVELY composing) does NOT hold for `modify = ⊕` over F₂
-- because of self-inverse: (x ⊕ y) ⊕ z ≠ (x ⊕ z) ⊕ (y ⊕ z) since the
-- RHS reduces by z⊕z = ∅ to (x ⊕ y) while the LHS is (x ⊕ y ⊕ z).
--
-- What ⊕ IS: a commutative-monoid operation that is linear in each
-- argument SEPARATELY (a monoid homomorphism in each), with the two
-- linearities NOT combining into bilinearity at characteristic 2.
--
-- The TRUE bilinear modify-via-FreeLinearization construction is
-- the 2-step linear extension of a basis-pair action b : Fin n →
-- Fin n → V. That construction is provided in WithBasisAction (§6)
-- as the substrate-honest universal-property realisation; the
-- fragment's default `modify = ⊕` is the simplest specific instance
-- and the one T9 worked examples exercise.
--
-- Modifier chains use Substrate.Groups.Coxeter.Word (the substrate-
-- native cons-list) per [[feedback-minimize-stdlib-deps]] —
-- Data.List would have pulled in stdlib infrastructure the substrate
-- already supplies natively.
--
-- Sister slice: Lojban L4 Lujvo (Coxeter Word composition with
-- arity inheritance). Lojban uses DISCRETE word-algebra; Toki Pona
-- uses COMMUTATIVE-MONOID composition over a vector carrier. The
-- intersection emerges at T10.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.TokiPona.ModifierBilinear where

open import Substrate.Foundation.Nat using (ℕ)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Eq
  using (_≡_; refl; sym; cong; cong₂)
open import Substrate.Category.CommutativeMonoid using (CommutativeMonoid)

open import Substrate.Groups.Coxeter.Word
  using (Word; []; _∷_; _++_; ++-assoc;
         ++-identity-left; ++-identity-right)
open import Substrate.TokiPona.SemanticSpace
  using (SemVec; ∅; _⊕_; ⊕-assoc; ⊕-comm;
         ⊕-identityˡ; ⊕-identityʳ; ⊕-self-inverse)

private
  variable
    m : ℕ

------------------------------------------------------------------------
-- 1. The default modify: vector sum (commutative-monoid op).
--
-- modify h m = h ⊕ m. Commutative, associative, ∅-identity,
-- self-inverse. Feature-bag pooling: "soweli lili" = activate both
-- the soweli and lili basis directions.
------------------------------------------------------------------------

modify : SemVec m → SemVec m → SemVec m
modify h n = h ⊕ n

------------------------------------------------------------------------
-- 2. Commutative-monoid laws on modify.
--
-- Inherited from ⊕'s F₂ abelian-group structure (T1's re-exports).
-- T7 (Linearity) consumes these to discharge the coherence record.
------------------------------------------------------------------------

modify-identityˡ : (n : SemVec m) → modify ∅ n ≡ n
modify-identityˡ = ⊕-identityˡ

modify-identityʳ : (h : SemVec m) → modify h ∅ ≡ h
modify-identityʳ = ⊕-identityʳ

modify-comm : (h n : SemVec m) → modify h n ≡ modify n h
modify-comm = ⊕-comm

modify-assoc :
  (h n₁ n₂ : SemVec m) →
  modify (modify h n₁) n₂ ≡ modify h (modify n₁ n₂)
modify-assoc = ⊕-assoc

modify-self-inverse : (v : SemVec m) → modify v v ≡ ∅
modify-self-inverse = ⊕-self-inverse

------------------------------------------------------------------------
-- GROUNDED: the default modify (= ⊕) IS a substrate-named
-- `Category.CommutativeMonoid` per dimension — the additive feature-bag
-- model. (The asymmetric, genuinely bilinear modify is the basis-pair
-- action in .WithBasisAction §6; this commutative-monoid grounding is the
-- simplest instance, as the design note at the top records.)
------------------------------------------------------------------------

modify-CommutativeMonoid : (m : ℕ) → CommutativeMonoid (SemVec m) modify ∅
modify-CommutativeMonoid m = record
  { +R-assoc     = modify-assoc
  ; +R-identityˡ = modify-identityˡ
  ; +R-identityʳ = modify-identityʳ
  ; +R-comm      = modify-comm
  }

------------------------------------------------------------------------
-- 3. Linearity in EACH argument separately (the honest monoid-
-- homomorphism statements that survive characteristic 2).
--
-- For fixed n: modify(h, n) is a translation by n; for fixed h:
-- similarly. Neither is the standard bilinearity, but both are
-- useful: they say modify respects the additive structure within
-- ONE slot at a time, which is what T7 and T8 need at this layer.
------------------------------------------------------------------------

modify-assoc-left :
  (h k n : SemVec m) →
  modify (h ⊕ k) n ≡ h ⊕ modify k n
modify-assoc-left h k n = ⊕-assoc h k n

modify-assoc-right :
  (h n k : SemVec m) →
  modify h (n ⊕ k) ≡ modify h n ⊕ k
modify-assoc-right h n k = sym (⊕-assoc h n k)

------------------------------------------------------------------------
-- 4. Modifier-chain fold via Substrate.Groups.Coxeter.Word.
--
-- A head plus a Coxeter-Word of modifier vectors reduces by
-- left-fold to a single semantic vector via repeated modify. The
-- Coxeter-Word carrier is the substrate-native variable-length
-- sequence (per [[feedback-minimize-stdlib-deps]] strengthening);
-- modifier-chain composition reuses the existing word algebra
-- without re-rolling list infrastructure.
------------------------------------------------------------------------

modifier-chain : SemVec m → Word (SemVec m) → SemVec m
modifier-chain h []       = h
modifier-chain h (n ∷ ns) = modifier-chain (modify h n) ns

modifier-chain-[] : (h : SemVec m) → modifier-chain h [] ≡ h
modifier-chain-[] _ = refl

modifier-chain-single :
  (h n : SemVec m) → modifier-chain h (n ∷ []) ≡ modify h n
modifier-chain-single _ _ = refl

------------------------------------------------------------------------
-- 5. Modifier-chain composition under Coxeter-Word concatenation.
--
-- Chains concatenate associatively: applying ns₁ then ns₂ to a
-- head equals applying (ns₁ ++ ns₂). Proof is left-fold induction
-- over ns₁; uses Coxeter-Word's ++ and the modify-assoc law.
------------------------------------------------------------------------

modifier-chain-++ :
  (h : SemVec m) (ns₁ ns₂ : Word (SemVec m)) →
  modifier-chain h (ns₁ ++ ns₂) ≡
    modifier-chain (modifier-chain h ns₁) ns₂
modifier-chain-++ h []        ns₂ = refl
modifier-chain-++ h (n ∷ ns₁) ns₂ = modifier-chain-++ (modify h n) ns₁ ns₂

------------------------------------------------------------------------
-- 6. The bilinear-via-basis-action construction.
--
-- The substrate-honest bilinear modify lifts a basis-pair action
-- b : Fin n → Fin n → SemVec m to a bilinear map SemVec n → SemVec
-- n → SemVec m via two applications of FreeLinearization.
--
-- The implementation lives in
--   Substrate.TokiPona.ModifierBilinear.WithBasisAction
-- (a submodule file). Closed by D1 of the Closure-debt arc; T4's
-- original deferral note is superseded by that slice.
------------------------------------------------------------------------
