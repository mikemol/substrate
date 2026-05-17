------------------------------------------------------------------------
-- Substrate.Groups.Actions.S3-on-V4
--
-- The AGL action of S₃ on V₄: S₃ ≅ GL(V₄, F₂) ≅ Sym({α, β, γ}),
-- acting on V₄ as the natural permutation of nonzero elements (e fixed).
--
-- S₃ here is the compositional construction Z/3 ⋊ Z/2 from
-- Substrate.Groups.S3. Its 6 canonical elements correspond to the 6
-- permutations of {α, β, γ}:
--
--   ([] , [])    ↔ id           (e, α, β, γ all fixed)
--   ([a], [])    ↔ (α β γ)      Z/3 generator: rotates α→β→γ→α
--   ([a,a], [])  ↔ (α γ β)      Z/3²: rotates α→γ→β→α
--   ([] , [a])   ↔ (α β)        Z/2 generator: swaps α↔β, γ fixed
--   ([a], [a])   ↔ (α γ)        rotate ∘ swap-αβ = swap αγ, β fixed
--   ([a,a], [a]) ↔ (β γ)        rotate² ∘ swap-αβ = swap βγ, α fixed
--
-- Convention: act (n, h) v = rotate^|n| (swap-αβ^|h| v).
-- This matches our SemidirectProductGroup twist: (n₁, h₁) · (n₂, h₂)
-- = (n₁ ·_N (act h₁ n₂), h₁ ·_H h₂) where act h is inversion on Z/3.
--
-- DBE plan (this file):
--   Shadows:
--     act-on-canonical : 24-case dispatch (canonical S₃ × V₄ → V₄)
--     act              : full action with pre-normalisation
--     act-hom-canonical: per-canonical-S₃ V₄ automorphism (6 × 16 refl)
--     act-∙-canonical  : per-(canonical-s₁, canonical-s₂, v) compositional law
--   Compose: dispatch lemmas → act axioms via canonical-bridge cong chains.
--   Entail:  6 × 4 + 6 × 16 + 6 × 6 × 4 = bounded refl enumeration.
--
-- Provides all 5 axioms for Substrate.Groups.Coxeter.SemidirectProductGroup,
-- enabling S₄ = V₄ ⋊ S₃ in Substrate.Groups.S4-Composed.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4 where

import Substrate.Groups.V4 as V4
open V4 using (V₄; e; α; β; γ)
import Substrate.Groups.Z2-Coxeter as Z₂
import Substrate.Groups.Z3-Coxeter as Z₃
import Substrate.Groups.S3 as S₃
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Data.Product using (_,_; proj₁; proj₂)
open import Relation.Binary.PropositionalEquality
  using (_≡_; refl; trans; sym; cong; cong₂)

------------------------------------------------------------------------
-- 1. Canonical-form action: dispatch on (Z₃ canonical, Z₂ canonical)
-- and V₄ ctor.
------------------------------------------------------------------------

act-on-canonical : Word Z₃.Gen → Word Z₂.Gen → V₄ → V₄
-- ([], []) = identity:
act-on-canonical [] [] v = v
-- ([a], []) = rotation (αβγ):
act-on-canonical (Z₃.a ∷ []) [] e = e
act-on-canonical (Z₃.a ∷ []) [] α = β
act-on-canonical (Z₃.a ∷ []) [] β = γ
act-on-canonical (Z₃.a ∷ []) [] γ = α
-- ([a,a], []) = rotation² (αγβ):
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] e = e
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] α = γ
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] β = α
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] γ = β
-- ([], [a]) = swap αβ (γ fixed):
act-on-canonical [] (Z₂.a ∷ []) e = e
act-on-canonical [] (Z₂.a ∷ []) α = β
act-on-canonical [] (Z₂.a ∷ []) β = α
act-on-canonical [] (Z₂.a ∷ []) γ = γ
-- ([a], [a]) = rotate ∘ swap-αβ = swap αγ (β fixed):
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) e = e
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) α = γ
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) β = β
act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) γ = α
-- ([a,a], [a]) = rotate² ∘ swap-αβ = swap βγ (α fixed):
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) e = e
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) α = α
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) β = γ
act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) γ = β
-- Fallback (unreachable on canonical S₃ inputs).
act-on-canonical _ _ v = v

------------------------------------------------------------------------
-- 2. Full action, normalising the S₃-pair first.
------------------------------------------------------------------------

act : S₃.Carrier → V₄ → V₄
act (n , h) v = act-on-canonical (Z₃.normalize n) (Z₂.normalize h) v

------------------------------------------------------------------------
-- 3. Per-canonical V₄-homomorphism lemmas.
--
-- For each of the 6 canonical S₃ elements, act-on-canonical with that
-- element is a V₄-automorphism. 16 refl cases each (V₄ × V₄).
------------------------------------------------------------------------

-- ([], []) — identity:
hom-id : ∀ v₁ v₂ →
  act-on-canonical [] [] (v₁ V4.· v₂) ≡
  act-on-canonical [] [] v₁ V4.· act-on-canonical [] [] v₂
hom-id _ _ = refl

-- ([a], []) — rotation (αβγ):
hom-rot : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ []) [] (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ []) [] v₁ V4.· act-on-canonical (Z₃.a ∷ []) [] v₂
hom-rot e e = refl
hom-rot e α = refl
hom-rot e β = refl
hom-rot e γ = refl
hom-rot α e = refl
hom-rot α α = refl
hom-rot α β = refl
hom-rot α γ = refl
hom-rot β e = refl
hom-rot β α = refl
hom-rot β β = refl
hom-rot β γ = refl
hom-rot γ e = refl
hom-rot γ α = refl
hom-rot γ β = refl
hom-rot γ γ = refl

-- ([a,a], []) — rotation² (αγβ):
hom-rot² : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] v₁ V4.· act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) [] v₂
hom-rot² e e = refl
hom-rot² e α = refl
hom-rot² e β = refl
hom-rot² e γ = refl
hom-rot² α e = refl
hom-rot² α α = refl
hom-rot² α β = refl
hom-rot² α γ = refl
hom-rot² β e = refl
hom-rot² β α = refl
hom-rot² β β = refl
hom-rot² β γ = refl
hom-rot² γ e = refl
hom-rot² γ α = refl
hom-rot² γ β = refl
hom-rot² γ γ = refl

-- ([], [a]) — swap αβ:
hom-swap-αβ : ∀ v₁ v₂ →
  act-on-canonical [] (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical [] (Z₂.a ∷ []) v₁ V4.· act-on-canonical [] (Z₂.a ∷ []) v₂
hom-swap-αβ e e = refl
hom-swap-αβ e α = refl
hom-swap-αβ e β = refl
hom-swap-αβ e γ = refl
hom-swap-αβ α e = refl
hom-swap-αβ α α = refl
hom-swap-αβ α β = refl
hom-swap-αβ α γ = refl
hom-swap-αβ β e = refl
hom-swap-αβ β α = refl
hom-swap-αβ β β = refl
hom-swap-αβ β γ = refl
hom-swap-αβ γ e = refl
hom-swap-αβ γ α = refl
hom-swap-αβ γ β = refl
hom-swap-αβ γ γ = refl

-- ([a], [a]) — swap αγ:
hom-swap-αγ : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) v₁ V4.· act-on-canonical (Z₃.a ∷ []) (Z₂.a ∷ []) v₂
hom-swap-αγ e e = refl
hom-swap-αγ e α = refl
hom-swap-αγ e β = refl
hom-swap-αγ e γ = refl
hom-swap-αγ α e = refl
hom-swap-αγ α α = refl
hom-swap-αγ α β = refl
hom-swap-αγ α γ = refl
hom-swap-αγ β e = refl
hom-swap-αγ β α = refl
hom-swap-αγ β β = refl
hom-swap-αγ β γ = refl
hom-swap-αγ γ e = refl
hom-swap-αγ γ α = refl
hom-swap-αγ γ β = refl
hom-swap-αγ γ γ = refl

-- ([a,a], [a]) — swap βγ:
hom-swap-βγ : ∀ v₁ v₂ →
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) (v₁ V4.· v₂) ≡
  act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₁ V4.· act-on-canonical (Z₃.a ∷ Z₃.a ∷ []) (Z₂.a ∷ []) v₂
hom-swap-βγ e e = refl
hom-swap-βγ e α = refl
hom-swap-βγ e β = refl
hom-swap-βγ e γ = refl
hom-swap-βγ α e = refl
hom-swap-βγ α α = refl
hom-swap-βγ α β = refl
hom-swap-βγ α γ = refl
hom-swap-βγ β e = refl
hom-swap-βγ β α = refl
hom-swap-βγ β β = refl
hom-swap-βγ β γ = refl
hom-swap-βγ γ e = refl
hom-swap-βγ γ α = refl
hom-swap-βγ γ β = refl
hom-swap-βγ γ γ = refl

------------------------------------------------------------------------
-- 4. Easy action axioms: act-cong, act-ε, act-ε-N.
------------------------------------------------------------------------

-- act-cong: depends only on (canonical n, canonical h, v).
-- V₄ uses _≡_ as its ≈, so cong on V₄ is just propositional cong.
act-cong : ∀ {s₁ s₂ v₁ v₂} → s₁ S₃.≈ s₂ → v₁ ≡ v₂ →
           act s₁ v₁ ≡ act s₂ v₂
act-cong {n₁ , h₁} {n₂ , h₂} {v₁} {v₂} (n-eq , h-eq) v-eq =
  trans (cong₂ (λ x y → act-on-canonical x y v₁) n-eq h-eq)
        (cong (act-on-canonical (Z₃.normalize n₂) (Z₂.normalize h₂)) v-eq)

-- act-ε: act (S₃.ε = ([], [])) v ≡ v.
-- Z₃.normalize [] = []. Z₂.normalize [] = []. act-on-canonical [] [] v = v.
act-ε : ∀ v → act S₃.ε v ≡ v
act-ε v = refl

-- act-ε-N: act g e ≡ e (every action preserves V₄'s identity).
-- Every act-on-canonical pattern starts with `_ _ e = e` or includes it.
-- Case on canonical (Z₃.normalize n, Z₂.normalize h).
act-ε-N-on-canonical : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h →
                       act-on-canonical n h e ≡ e
act-ε-N-on-canonical Z₃.c-ε  Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-a  Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-aa Z₂.c-ε = refl
act-ε-N-on-canonical Z₃.c-ε  Z₂.c-a = refl
act-ε-N-on-canonical Z₃.c-a  Z₂.c-a = refl
act-ε-N-on-canonical Z₃.c-aa Z₂.c-a = refl

act-ε-N : ∀ s → act s e ≡ e
act-ε-N (n , h) = act-ε-N-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)

------------------------------------------------------------------------
-- 5. act-hom: dispatch through the 6 per-canonical hom lemmas.
------------------------------------------------------------------------

act-hom-on-canonical :
  ∀ {n h} (c-n : Z₃.Canonical n) (c-h : Z₂.Canonical h) →
  ∀ v₁ v₂ →
  act-on-canonical n h (v₁ V4.· v₂) ≡
  act-on-canonical n h v₁ V4.· act-on-canonical n h v₂
act-hom-on-canonical Z₃.c-ε  Z₂.c-ε = hom-id
act-hom-on-canonical Z₃.c-a  Z₂.c-ε = hom-rot
act-hom-on-canonical Z₃.c-aa Z₂.c-ε = hom-rot²
act-hom-on-canonical Z₃.c-ε  Z₂.c-a = hom-swap-αβ
act-hom-on-canonical Z₃.c-a  Z₂.c-a = hom-swap-αγ
act-hom-on-canonical Z₃.c-aa Z₂.c-a = hom-swap-βγ

act-hom : ∀ s v₁ v₂ → act s (v₁ V4.· v₂) ≡ act s v₁ V4.· act s v₂
act-hom (n , h) =
  act-hom-on-canonical (Z₃.normalize-canonical n) (Z₂.normalize-canonical h)

------------------------------------------------------------------------
-- 6. act-∙: the action's composition law.
--
-- DBE (in-file, fired by 2nd-error rule):
--   Target: ∀ s₁ s₂ v → act (s₁ S₃.∙ s₂) v ≡ act s₁ (act s₂ v).
--   Prior failure pattern: act-∙-on-canonical with implicit args from
--     Canonical proofs creates a signature that doesn't unify with the
--     act-∙ caller's original-form goal.
--   Resolution: split into two shadows.
--
--   Shadow ∙-CANONICAL:
--     act-∙-canonical : ∀ (n₁ h₁ n₂ h₂ : Word) (canonicals) (v) →
--                       act ((n₁,h₁) S₃.∙ (n₂,h₂)) v ≡ act-on-canonical n₁ h₁ (act-on-canonical n₂ h₂ v)
--     — Explicit Word args. Pattern matching on Canonical proofs forces
--       n_i to specific Word values, making S₃.∙ reduce.
--     — 144 refl cases (36 (s₁,s₂) combos × 4 v ctors).
--
--   Shadow ∙-BRIDGE:
--     act-∙ : bridges (n₁,h₁,n₂,h₂) → (Z₃.normalize, Z₂.normalize) form via
--             act-cong of S₃.∙-cong applied to (sym normalize-idem) components.
--
--   Compose: trans bridge (act-∙-canonical (Z₃.normalize n₁) ...).
--   Entail:  per-canonical refl + ≈-bridging via group congruence.
------------------------------------------------------------------------


------------------------------------------------------------------------
-- 6. act-∙ via the dihedral structure (structural decomposition).
--
-- DBE (in-file, structural approach):
--   Insight: act-∙ holds because of three generator-level facts:
--     (a) rotate has order 3 (rotate³ ≡ id),
--     (b) swap-αβ has order 2 (swap-αβ² ≡ id),
--     (c) swap-αβ ∘ rotate ≡ rotate² ∘ swap-αβ (the dihedral relation).
--   Not by 144 coincidences.
--
--   Shadows (in dependency order):
--     S1. rot-pow, swap-pow  : recursive power functions (3 lines each)
--     S2. *-append           : compose ++ with power (inductive, 3 lines)
--     S3. rotate³-id, swap-αβ²-id : generator-order identities (4 cases each)
--     S4. *-normalize-eq     : power respects normalize (induction + S3)
--     S5. act-equals-pow     : bridge to act-on-canonical (24 refl)
--     S6. swap-rotate-twist  : the dihedral relation (4 refl)
--     S7. rot-pow-swap-twist : lifted twist on canonical n (12 refl)
--
--   Composition (act-∙): 4 blocks by (h₁, h₂); each chains through
--                        rot-pow-append, normalize-eq, the twist.
------------------------------------------------------------------------

-- S0: generators rotate and swap-αβ (extracted from act-on-canonical
-- at canonical ([a], []) and ([], [a]) respectively).
rotate : V₄ → V₄
rotate e = e
rotate α = β
rotate β = γ
rotate γ = α

swap-αβ : V₄ → V₄
swap-αβ e = e
swap-αβ α = β
swap-αβ β = α
swap-αβ γ = γ

-- S1: power functions.
rot-pow : Word Z₃.Gen → V₄ → V₄
rot-pow []           v = v
rot-pow (Z₃.a ∷ w)   v = rotate (rot-pow w v)

swap-pow : Word Z₂.Gen → V₄ → V₄
swap-pow []         v = v
swap-pow (Z₂.a ∷ w) v = swap-αβ (swap-pow w v)

-- S2: append composes (strict, by induction on first arg).
open import Substrate.Groups.Coxeter.Word using (_++_)

rot-pow-append : (w₁ w₂ : Word Z₃.Gen) (v : V₄) →
                 rot-pow (w₁ ++ w₂) v ≡ rot-pow w₁ (rot-pow w₂ v)
rot-pow-append []           w₂ v = refl
rot-pow-append (Z₃.a ∷ w₁)  w₂ v = cong rotate (rot-pow-append w₁ w₂ v)

swap-pow-append : (w₁ w₂ : Word Z₂.Gen) (v : V₄) →
                  swap-pow (w₁ ++ w₂) v ≡ swap-pow w₁ (swap-pow w₂ v)
swap-pow-append []          w₂ v = refl
swap-pow-append (Z₂.a ∷ w₁) w₂ v = cong swap-αβ (swap-pow-append w₁ w₂ v)

-- S3: generator-order identities.
rotate³-id : (v : V₄) → rotate (rotate (rotate v)) ≡ v
rotate³-id e = refl
rotate³-id α = refl
rotate³-id β = refl
rotate³-id γ = refl

swap-αβ²-id : (v : V₄) → swap-αβ (swap-αβ v) ≡ v
swap-αβ²-id e = refl
swap-αβ²-id α = refl
swap-αβ²-id β = refl
swap-αβ²-id γ = refl

-- S4: power respects normalize.
--
-- Refactored to use an explicit helper (avoids `with` not substituting
-- in the IH's type). The helper dispatches on the canonical form of
-- Z₃.normalize w, applying rotate³-id only in the c-aa wraparound case.
rot-pow-normalize-eq : (w : Word Z₃.Gen) (v : V₄) →
                       rot-pow w v ≡ rot-pow (Z₃.normalize w) v
rot-pow-normalize-eq []         v = refl
rot-pow-normalize-eq (Z₃.a ∷ w) v =
  trans (cong rotate (rot-pow-normalize-eq w v))
        (rot-step (Z₃.normalize-canonical w) v)
  where
    rot-step : ∀ {x} → Z₃.Canonical x → (v : V₄) →
               rotate (rot-pow x v) ≡ rot-pow (Z₃.insert Z₃.a x) v
    rot-step Z₃.c-ε  _ = refl
    rot-step Z₃.c-a  _ = refl
    rot-step Z₃.c-aa v = rotate³-id v

swap-pow-normalize-eq : (w : Word Z₂.Gen) (v : V₄) →
                        swap-pow w v ≡ swap-pow (Z₂.normalize w) v
swap-pow-normalize-eq []         v = refl
swap-pow-normalize-eq (Z₂.a ∷ w) v =
  trans (cong swap-αβ (swap-pow-normalize-eq w v))
        (swap-step (Z₂.normalize-canonical w) v)
  where
    swap-step : ∀ {x} → Z₂.Canonical x → (v : V₄) →
                swap-αβ (swap-pow x v) ≡ swap-pow (Z₂.insert Z₂.a x) v
    swap-step Z₂.c-ε _ = refl
    swap-step Z₂.c-a v = swap-αβ²-id v

-- S5: bridge act-on-canonical ↔ rot-pow ∘ swap-pow on canonical inputs.
act-equals-pow : ∀ {n h} → Z₃.Canonical n → Z₂.Canonical h → ∀ v →
                 act-on-canonical n h v ≡ rot-pow n (swap-pow h v)
act-equals-pow Z₃.c-ε  Z₂.c-ε e = refl
act-equals-pow Z₃.c-ε  Z₂.c-ε α = refl
act-equals-pow Z₃.c-ε  Z₂.c-ε β = refl
act-equals-pow Z₃.c-ε  Z₂.c-ε γ = refl
act-equals-pow Z₃.c-a  Z₂.c-ε e = refl
act-equals-pow Z₃.c-a  Z₂.c-ε α = refl
act-equals-pow Z₃.c-a  Z₂.c-ε β = refl
act-equals-pow Z₃.c-a  Z₂.c-ε γ = refl
act-equals-pow Z₃.c-aa Z₂.c-ε e = refl
act-equals-pow Z₃.c-aa Z₂.c-ε α = refl
act-equals-pow Z₃.c-aa Z₂.c-ε β = refl
act-equals-pow Z₃.c-aa Z₂.c-ε γ = refl
act-equals-pow Z₃.c-ε  Z₂.c-a e = refl
act-equals-pow Z₃.c-ε  Z₂.c-a α = refl
act-equals-pow Z₃.c-ε  Z₂.c-a β = refl
act-equals-pow Z₃.c-ε  Z₂.c-a γ = refl
act-equals-pow Z₃.c-a  Z₂.c-a e = refl
act-equals-pow Z₃.c-a  Z₂.c-a α = refl
act-equals-pow Z₃.c-a  Z₂.c-a β = refl
act-equals-pow Z₃.c-a  Z₂.c-a γ = refl
act-equals-pow Z₃.c-aa Z₂.c-a e = refl
act-equals-pow Z₃.c-aa Z₂.c-a α = refl
act-equals-pow Z₃.c-aa Z₂.c-a β = refl
act-equals-pow Z₃.c-aa Z₂.c-a γ = refl

-- S6: dihedral generator-level relation.
swap-rotate-twist : (v : V₄) → swap-αβ (rotate v) ≡ rotate (rotate (swap-αβ v))
swap-rotate-twist e = refl
swap-rotate-twist α = refl
swap-rotate-twist β = refl
swap-rotate-twist γ = refl

-- S7: rot-pow ↔ swap twist on canonical n.
rot-pow-swap-twist : ∀ {n} → Z₃.Canonical n → (v : V₄) →
                     swap-αβ (rot-pow n v) ≡ rot-pow (Z₃.inv n) (swap-αβ v)
rot-pow-swap-twist Z₃.c-ε  e = refl
rot-pow-swap-twist Z₃.c-ε  α = refl
rot-pow-swap-twist Z₃.c-ε  β = refl
rot-pow-swap-twist Z₃.c-ε  γ = refl
rot-pow-swap-twist Z₃.c-a  e = refl
rot-pow-swap-twist Z₃.c-a  α = refl
rot-pow-swap-twist Z₃.c-a  β = refl
rot-pow-swap-twist Z₃.c-a  γ = refl
rot-pow-swap-twist Z₃.c-aa e = refl
rot-pow-swap-twist Z₃.c-aa α = refl
rot-pow-swap-twist Z₃.c-aa β = refl
rot-pow-swap-twist Z₃.c-aa γ = refl

-- act-∙: per-block dispatch via the structural lemmas.
-- Block 00 first to validate the proof shape.
act-∙-canonical : ∀ {n₁ h₁ n₂ h₂} →
                  Z₃.Canonical n₁ → Z₂.Canonical h₁ →
                  Z₃.Canonical n₂ → Z₂.Canonical h₂ →
                  ∀ v →
                  act ((n₁ , h₁) S₃.∙ (n₂ , h₂)) v ≡
                  act-on-canonical n₁ h₁ (act-on-canonical n₂ h₂ v)
-- Block 00: h₁ = [] forces no swap on n₂; h₂ = [] makes the H-component trivial.
act-∙-canonical {n₁} {.[]} {n₂} {.[]} c-n₁ Z₂.c-ε c-n₂ Z₂.c-ε v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , [])) v ≡ rot-pow n₁ (rot-pow n₂ v)
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-ε v)
      (trans (cong (λ w → rot-pow w v) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) v))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) v)
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ v))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ [] v) ≡ rot-pow n₁ (rot-pow n₂ v)
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ [] v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-ε v))
-- Block 01: h₁ = [], h₂ = [a]. Same shape as block 00 with swap-αβ v
-- threaded through the inner argument of rot-pow.
act-∙-canonical {n₁} {.[]} {n₂} {.(Z₂.a ∷ [])} c-n₁ Z₂.c-ε c-n₂ Z₂.c-a v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.normalize n₂))) Z₂.c-a v)
      (trans (cong (λ w → rot-pow w (swap-αβ v)) (Z₃.normalize-idem (n₁ ++ Z₃.normalize n₂)))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.normalize n₂) (swap-αβ v)))
      (trans (rot-pow-append n₁ (Z₃.normalize n₂) (swap-αβ v))
             (sym (cong (rot-pow n₁) (rot-pow-normalize-eq n₂ (swap-αβ v)))))))
    RHS-to-pow : act-on-canonical n₁ [] (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (rot-pow n₂ (swap-αβ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-ε (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (rot-pow n₁) (act-equals-pow c-n₂ Z₂.c-a v))

-- Block 10: h₁ = [a], h₂ = []. SP twist inverts n₂. Uses rot-pow-swap-twist.
act-∙-canonical {n₁} {.(Z₂.a ∷ [])} {n₂} {.[]} c-n₁ Z₂.c-a c-n₂ Z₂.c-ε v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    LHS-to-pow =
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) Z₂.c-a v)
      (trans (cong (λ w → rot-pow w (swap-αβ v)) (Z₃.normalize-idem (n₁ ++ Z₃.inv (Z₃.normalize n₂))))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.inv (Z₃.normalize n₂)) (swap-αβ v)))
      (trans (rot-pow-append n₁ (Z₃.inv (Z₃.normalize n₂)) (swap-αβ v))
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) (swap-αβ v))) (Z₃.canonical-is-fixed-Z3 c-n₂))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ v)))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ [] v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ v))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-a (act-on-canonical n₂ [] v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ Z₂.c-ε v))

-- Block 11: h₁ = [a], h₂ = [a]. SP twist inverts n₂; swaps collapse via swap-αβ²-id.
act-∙-canonical {n₁} {.(Z₂.a ∷ [])} {n₂} {.(Z₂.a ∷ [])} c-n₁ Z₂.c-a c-n₂ Z₂.c-a v =
  trans LHS-to-pow (sym RHS-to-pow)
  where
    LHS-to-pow : act ((n₁ , Z₂.a ∷ []) S₃.∙ (n₂ , Z₂.a ∷ [])) v ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    LHS-to-pow =
      -- Note: h₁ Z₂G.· h₂ = Z₂.normalize ([a] ++ [a]) = [], so swap-pow [] v = v on the outside.
      -- But after the twist + sym, we want to match RHS's form `swap-αβ (rot-pow n₂ (swap-αβ v))`.
      -- LHS chain produces `rot-pow n₁ (rot-pow (Z₃.inv n₂) v)`; bridge to `swap-αβ (...)` via twist+swap².
      trans (act-equals-pow (Z₃.normalize-canonical (Z₃.normalize (n₁ ++ Z₃.inv (Z₃.normalize n₂)))) Z₂.c-ε v)
      (trans (cong (λ w → rot-pow w v) (Z₃.normalize-idem (n₁ ++ Z₃.inv (Z₃.normalize n₂))))
      (trans (sym (rot-pow-normalize-eq (n₁ ++ Z₃.inv (Z₃.normalize n₂)) v))
      (trans (rot-pow-append n₁ (Z₃.inv (Z₃.normalize n₂)) v)
      (trans (cong (λ w → rot-pow n₁ (rot-pow (Z₃.inv w) v)) (Z₃.canonical-is-fixed-Z3 c-n₂))
      -- Now we have rot-pow n₁ (rot-pow (Z₃.inv n₂) v). Bridge to rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v))).
      -- v = swap-αβ (swap-αβ v) via sym swap-αβ²-id.
      -- Then rot-pow (Z₃.inv n₂) (swap-αβ (swap-αβ v)) = swap-αβ (rot-pow n₂ (swap-αβ v)) via sym twist.
      (trans (cong (λ x → rot-pow n₁ (rot-pow (Z₃.inv n₂) x)) (sym (swap-αβ²-id v)))
             (cong (rot-pow n₁) (sym (rot-pow-swap-twist c-n₂ (swap-αβ v)))))))))
    RHS-to-pow : act-on-canonical n₁ (Z₂.a ∷ []) (act-on-canonical n₂ (Z₂.a ∷ []) v) ≡
                 rot-pow n₁ (swap-αβ (rot-pow n₂ (swap-αβ v)))
    RHS-to-pow =
      trans (act-equals-pow c-n₁ Z₂.c-a (act-on-canonical n₂ (Z₂.a ∷ []) v))
            (cong (λ x → rot-pow n₁ (swap-αβ x)) (act-equals-pow c-n₂ Z₂.c-a v))

-- Bridge: act-∙ for arbitrary (n, h) pairs, via act-cong + S₃.∙-cong over normalize-idem.
-- Implicit args of act-cong made explicit to avoid Agda's normalize-unification block.
act-∙ : ∀ s₁ s₂ v → act (s₁ S₃.∙ s₂) v ≡ act s₁ (act s₂ v)
act-∙ (n₁ , h₁) (n₂ , h₂) v =
  trans
    (act-cong {s₁ = (n₁ , h₁) S₃.∙ (n₂ , h₂)}
              {s₂ = (Z₃.normalize n₁ , Z₂.normalize h₁) S₃.∙ (Z₃.normalize n₂ , Z₂.normalize h₂)}
              {v₁ = v} {v₂ = v}
      (S₃.∙-cong {a₁ = n₁ , h₁} {a₂ = Z₃.normalize n₁ , Z₂.normalize h₁}
                  {b₁ = n₂ , h₂} {b₂ = Z₃.normalize n₂ , Z₂.normalize h₂}
                  (sym (Z₃.normalize-idem n₁) , sym (Z₂.normalize-idem h₁))
                  (sym (Z₃.normalize-idem n₂) , sym (Z₂.normalize-idem h₂)))
      refl)
    (act-∙-canonical (Z₃.normalize-canonical n₁) (Z₂.normalize-canonical h₁)
                     (Z₃.normalize-canonical n₂) (Z₂.normalize-canonical h₂) v)
