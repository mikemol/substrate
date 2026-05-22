------------------------------------------------------------------------
-- Substrate.Groups.Actions.Z2-on-Z3
--
-- The action of Z/2 on Z/3 by inversion. This is the unique non-trivial
-- group homomorphism Z/2 → Aut(Z/3), and the action data for the
-- semidirect product S₃ = Z/3 ⋊ Z/2.
--
-- The Z/2 generator acts on Z/3 as the inversion automorphism
-- (a ↦ a², i.e., [a] ↔ [a, a]); Z/2's identity acts trivially.
--
-- Strategy: define `act h n` as a function of (Z₂.normalize h,
-- Z₃.normalize n). Both arguments are pre-canonicalized, then a
-- helper `act-letter` dispatches on the Z₂ canonical structure.
-- This makes the output always Z/3-canonical, which simplifies the
-- normalize-equality proofs needed by Substrate.Groups.Coxeter.SemidirectProductGroup.
--
-- Per [[feedback-composable-primitives-over-flat-enumeration]]:
-- isolating the action in its own file keeps S3's composition
-- cognitively local — S3.agda just plugs this in.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.Z2-on-Z3 where

import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.Z2-Coxeter-Group as Z₂G
import Substrate.Groups.Z3-Coxeter-Group as Z₃G
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Foundation.Eq
  using (_≡_; refl; trans; sym; cong)

------------------------------------------------------------------------
-- 1. The action: pre-canonicalize both arguments, then dispatch on
-- the canonical Z/2 word shape ([] or [a]).
------------------------------------------------------------------------

act-letter : Word Z₂.Gen → Word Z₃.Gen → Word Z₃.Gen
act-letter []                            n = n
act-letter (Z₂.a ∷ [])                   n = Z₃.inv n
act-letter (Z₂.a ∷ (Z₂.a ∷ _))           n = n  -- unreachable on canonical Z₂

act : Word Z₂.Gen → Word Z₃.Gen → Word Z₃.Gen
act h n = act-letter (Z₂.normalize h) (Z₃.normalize n)

------------------------------------------------------------------------
-- 2. Helper: act-letter on canonical (h, n) outputs a Z/3-canonical word.
------------------------------------------------------------------------

act-letter-canonical : ∀ {h n} → Z₂.Canonical h → Z₃.Canonical n →
                       Z₃.Canonical (act-letter h n)
act-letter-canonical Z₂.c-ε c-n = c-n
act-letter-canonical Z₂.c-a c-n = Z₃.inv-canonical c-n

act-canonical : ∀ h n → Z₃.Canonical (act h n)
act-canonical h n =
  act-letter-canonical
    (Z₂.normalize-canonical h)
    (Z₃.normalize-canonical n)

normalize-act : ∀ h n → Z₃.normalize (act h n) ≡ act h n
normalize-act h n = Z₃.canonical-is-fixed (act-canonical h n)

------------------------------------------------------------------------
-- 3. act-cong: depends only on (Z₂.normalize h, Z₃.normalize n),
-- so the action equalities transport directly.
------------------------------------------------------------------------

act-cong : ∀ {h₁ h₂ n₁ n₂} → h₁ Z₂G.≈ h₂ → n₁ Z₃G.≈ n₂ →
           act h₁ n₁ Z₃G.≈ act h₂ n₂
act-cong {h₁} {h₂} {n₁} {n₂} h-eq n-eq =
  -- act h n = act-letter (Z₂.normalize h) (Z₃.normalize n).
  -- act h₁ n₁ ≡ act h₂ n₂ propositionally via cong on act-letter.
  -- ≈ on top: Z₃.normalize equality preserved by cong.
  cong Z₃.normalize (cong₂ act-letter h-eq n-eq)
  where open import Substrate.Foundation.Eq using (cong₂)

------------------------------------------------------------------------
-- 4. act-ε: act ε₂ n ≈ n.
--
-- Z₂.ε = []. act [] n = act-letter [] (Z₃.normalize n) = Z₃.normalize n.
-- Outer Z₃.normalize: Z₃.normalize (Z₃.normalize n) = Z₃.normalize n (idem).
------------------------------------------------------------------------

act-ε : ∀ n → act Z₂G.ε n Z₃G.≈ n
act-ε n = Z₃.normalize-idem n

------------------------------------------------------------------------
-- 5. act-ε-N: act h ε₁ ≈ ε₁.
--
-- For canonical h ∈ {[], [a]}: act-letter h [] is either [] (identity)
-- or Z₃.inv [] = [] (inversion of identity). Both = [] = Z₃G.ε.
------------------------------------------------------------------------

act-letter-ε : ∀ {h} → Z₂.Canonical h → act-letter h [] ≡ []
act-letter-ε Z₂.c-ε = refl
act-letter-ε Z₂.c-a = refl

act-ε-N : ∀ h → act h Z₃G.ε Z₃G.≈ Z₃G.ε
act-ε-N h =
  -- act h [] = act-letter (Z₂.normalize h) (Z₃.normalize []) = act-letter (Z₂.normalize h) [].
  -- Z₃.normalize of this = ... we want ≡ Z₃.normalize [] = [].
  cong Z₃.normalize (act-letter-ε (Z₂.normalize-canonical h))

------------------------------------------------------------------------
-- 6. act-∙: act (h₁ ∙ h₂) n ≈ act h₁ (act h₂ n).
--
-- act (h₁ Z₂G.∙ h₂) n = act-letter (Z₂.normalize (Z₂.normalize (h₁ ++ h₂))) (Z₃.normalize n)
--                     = act-letter (Z₂.normalize (h₁ ++ h₂)) (Z₃.normalize n)   [idem]
-- By Z₂.normalize-distrib + cong: Z₂.normalize (h₁ ++ h₂) = Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂).
-- So LHS = act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) (Z₃.normalize n).
--
-- act h₁ (act h₂ n) = act-letter (Z₂.normalize h₁) (Z₃.normalize (act h₂ n)).
-- By normalize-act: Z₃.normalize (act h₂ n) = act h₂ n. So
-- RHS = act-letter (Z₂.normalize h₁) (act h₂ n)
--     = act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) (Z₃.normalize n)).
--
-- Case-analysis on (Z₂.normalize h₁, Z₂.normalize h₂) — 4 cases via
-- the canonical proofs.
------------------------------------------------------------------------

-- Helper: when canonical proofs of Z₂.normalize h are known, reduce
-- act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) X to
-- act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) X) for
-- canonical Z₃ X.
act-letter-compose :
  ∀ {h₁ h₂} (c₁ : Z₂.Canonical h₁) (c₂ : Z₂.Canonical h₂)
    {x} (c-x : Z₃.Canonical x) →
  act-letter (Z₂.normalize (h₁ ++ h₂)) x ≡
  act-letter h₁ (act-letter h₂ x)
act-letter-compose Z₂.c-ε Z₂.c-ε c-x = refl
act-letter-compose Z₂.c-ε Z₂.c-a c-x = refl
act-letter-compose Z₂.c-a Z₂.c-ε {x} c-x =
  -- LHS: act-letter (Z₂.normalize ([a] ++ [])) x = act-letter (Z₂.normalize [a]) x = act-letter [a] x = Z₃.inv x.
  -- RHS: act-letter [a] (act-letter [] x) = act-letter [a] x = Z₃.inv x.
  refl
act-letter-compose Z₂.c-a Z₂.c-a {x} c-x =
  -- LHS: act-letter (Z₂.normalize ([a] ++ [a])) x.
  --   [a] ++ [a] = a ∷ [a]. Z₂.normalize (a ∷ [a]) = Z₂.insert a (Z₂.normalize [a]) = Z₂.insert a [a] = [].
  --   So LHS = act-letter [] x = x.
  -- RHS: act-letter [a] (act-letter [a] x) = act-letter [a] (Z₃.inv x) = Z₃.inv (Z₃.inv x).
  -- For canonical x: Z₃.inv (Z₃.inv x) = x via inv-inv-canonical.
  sym (Z₃.inv-inv-canonical c-x)

act-∙ : ∀ h₁ h₂ n → act (h₁ Z₂G.· h₂) n Z₃G.≈ act h₁ (act h₂ n)
act-∙ h₁ h₂ n =
  let
    inner-n = Z₃.normalize n
    c-n = Z₃.normalize-canonical n
    c₁ = Z₂.normalize-canonical h₁
    c₂ = Z₂.normalize-canonical h₂
    -- LHS goal expansion:
    --   act (h₁ Z₂G.· h₂) n
    --     = act (Z₂.normalize (h₁ ++ h₂)) n
    --     = act-letter (Z₂.normalize (Z₂.normalize (h₁ ++ h₂))) inner-n
    -- bridge-h: Z₂.normalize (Z₂.normalize (h₁ ++ h₂)) ≡ Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)
    bridge-h : Z₂.normalize (Z₂.normalize (h₁ ++ h₂)) ≡
               Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)
    bridge-h = trans (Z₂.normalize-idem (h₁ ++ h₂))
                     (Z₂.normalize-distrib h₁ h₂)
    -- act-letter-compose: act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) inner-n
    --                       ≡ act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) inner-n)
    composed : act-letter (Z₂.normalize (Z₂.normalize h₁ ++ Z₂.normalize h₂)) inner-n ≡
               act-letter (Z₂.normalize h₁) (act-letter (Z₂.normalize h₂) inner-n)
    composed = act-letter-compose c₁ c₂ c-n
    -- Inner act h₂ n IS act-letter (Z₂.normalize h₂) inner-n (definitionally).
    -- Z₃.normalize of it equals itself (canonicality of act-letter output).
    inner-canonical : Z₃.normalize (act-letter (Z₂.normalize h₂) inner-n) ≡
                      act-letter (Z₂.normalize h₂) inner-n
    inner-canonical = Z₃.canonical-is-fixed (act-letter-canonical c₂ c-n)
  in
  trans (cong (λ x → Z₃.normalize (act-letter x inner-n)) bridge-h)
  (trans (cong Z₃.normalize composed)
         (sym (cong (λ x → Z₃.normalize (act-letter (Z₂.normalize h₁) x))
                    inner-canonical)))

------------------------------------------------------------------------
-- 7. act-hom: act h (n₁ ∙ n₂) ≈ act h n₁ ∙ act h n₂.
--
-- Case on canonical h. For c-ε: both sides ≈ n₁ ∙ n₂.
-- For c-a: uses Z₃.inv-distrib-canonical (Z/3 is abelian, so inv is
-- a homomorphism).
------------------------------------------------------------------------

-- Helper: act-letter h (n₁ ·₃ n₂) vs (act-letter h n₁) ·₃ (act-letter h n₂)
-- after normalize. 2 cases on canonical h.
act-letter-hom :
  ∀ {h} (c : Z₂.Canonical h)
    {n₁ n₂} (c-n₁ : Z₃.Canonical n₁) (c-n₂ : Z₃.Canonical n₂) →
  Z₃.normalize (act-letter h (n₁ Z₃G.· n₂)) ≡
  Z₃.normalize (act-letter h n₁ Z₃G.· act-letter h n₂)
act-letter-hom Z₂.c-ε {n₁} {n₂} c-n₁ c-n₂ =
  -- LHS: Z₃.normalize (n₁ ·₃ n₂) = Z₃.normalize (Z₃.normalize (n₁ ++ n₂)) = Z₃.normalize (n₁ ++ n₂).
  -- RHS: Z₃.normalize (n₁ ·₃ n₂) = same.
  refl
act-letter-hom Z₂.c-a {n₁} {n₂} c-n₁ c-n₂ =
  -- LHS evaluates to: Z₃.normalize (Z₃.inv (Z₃.normalize (n₁ ++ n₂))).
  -- RHS evaluates to: Z₃.normalize (Z₃.normalize (Z₃.inv n₁ ++ Z₃.inv n₂)).
  -- Z₃.inv-distrib-canonical gives the LHS ≡ Z₃.normalize (Z₃.inv n₁ ++ Z₃.inv n₂),
  -- then sym idem bridges to the outer-normalized RHS form.
  trans (Z₃.inv-distrib-canonical c-n₁ c-n₂)
        (sym (Z₃.normalize-idem (Z₃.inv n₁ ++ Z₃.inv n₂)))

act-hom : ∀ h n₁ n₂ → act h (n₁ Z₃G.· n₂) Z₃G.≈ (act h n₁ Z₃G.· act h n₂)
act-hom h n₁ n₂ =
  let
    c-h = Z₂.normalize-canonical h
    c-n₁ = Z₃.normalize-canonical n₁
    c-n₂ = Z₃.normalize-canonical n₂
    -- Bridge: Z₃.normalize (n₁ Z₃G.· n₂) ≡ Z₃.normalize n₁ Z₃G.· Z₃.normalize n₂.
    -- LHS evaluates to Z₃.normalize (Z₃.normalize (n₁ ++ n₂)) → Z₃.normalize (n₁ ++ n₂) (idem).
    -- RHS is Z₃.normalize (Z₃.normalize n₁ ++ Z₃.normalize n₂) by def of Z₃G.·.
    -- Use Z₃.normalize-distrib to bridge.
    bridge-· : Z₃.normalize (n₁ Z₃G.· n₂) ≡ Z₃.normalize n₁ Z₃G.· Z₃.normalize n₂
    bridge-· = trans (Z₃.normalize-idem (n₁ ++ n₂)) (Z₃.normalize-distrib n₁ n₂)
  in
  -- Goal: Z₃.normalize (act-letter (Z₂.normalize h) (Z₃.normalize (n₁ Z₃G.· n₂)))
  --      ≡ Z₃.normalize (act-letter (Z₂.normalize h) (Z₃.normalize n₁) Z₃G.· act-letter (Z₂.normalize h) (Z₃.normalize n₂))
  -- Step 1: Apply bridge-· inside the act-letter's second arg via cong.
  -- Step 2: Apply act-letter-hom (with c-n at the Z₃-canonicals of n₁, n₂).
  trans (cong Z₃.normalize (cong (act-letter (Z₂.normalize h)) bridge-·))
        (act-letter-hom c-h c-n₁ c-n₂)
