------------------------------------------------------------------------
-- Substrate.Logic.Evidence.GValueLSpace.Primes
--
-- Ω3-L-primes, layer (1): the Ⓖ★ INVERTIBLE-POLE cross-coherence.
--
-- The exp⊣log codec ties an ADDITIVE L-space to the MULTIPLICATIVE G-space ℚ.
-- That is a cross-carrier tie (Wedge.CrossMul.CrossMix), and its coherence has
-- TWO species (the Ⓖ★ genus, Algebra.Wedge.Species):
--   * NILPOTENT pole  — cross term → z (the multiplicative ZERO): orthogonality
--     (CRT's e₁·e₂=0). This is `CrossMul.Coherent` = Nilpotent.
--   * INVERTIBLE pole — cross term → 1 (the multiplicative UNIT): a·a⁻¹ ≈ 1.
--     This is the codec ANTIPODE, the DUAL of CrossMul.Coherent.
--
-- The rank-1 base-power codec (GValueLSpace.Properties.ℕ-power-codec) is a
-- MONOID L=ℕ — no inverses, so codec-antipode only fires at 0+0. For a genuine
-- inverse↦recip the cyclic subgroup ⟨g⟩ must be used: the inverse of gᵏ is
-- (recip g)ᵏ, and they cancel. THAT cancellation — `pow-cancel-balanced` — is
-- the invertible-pole coherence at rank-1, and it needs NO unique factorisation
-- (FTA enters only at layer (2): surjectivity onto ℚ₊ / the log inverse /
-- L_OR=LogSumExp). It is the clean induction below, NOT the den-1 ℚ-grind the
-- "needs FTA, heavy" framing implied.
--
-- The headline: `gvalue-power-antipode` — for an el-atlas G-value g and its
-- antipode (reciprocal) h, gᵏ · hᵏ ≈ 1 for every k.  So G(P)ᵏ ⊣ G(¬P)ᵏ: the
-- el-atlas antipode constraint G·G(¬P)≈1 (k=1, `GValueAsQ.gvalue-antipode`)
-- EXTENDS to the whole cyclic subgroup — the invertible pole, machine-checked.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Logic.Evidence.GValueLSpace.Primes where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.Nat.Properties.Add using (+-suc)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym)
open import Substrate.Foundation.List using (List; []; _∷_)
open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)
open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Properties.Field using (*ℚ-assoc; *ℚ-comm; *ℚ-identityˡ; *ℚ-identityʳ)
open import Substrate.Algebra.Q.Properties.Congruence using (*ℚ-cong)
open import Substrate.Algebra.Z using (ℤ; +_; -suc_)
open import Substrate.Algebra.Z.Add using (_+ℤ_; _⊖_)
open import Substrate.Logic.Evidence.GValueLSpace using (powℚ; ExpLogCodec; ExpLogCodecℚ)
open import Substrate.Logic.Evidence.GValueLSpace.Properties using (pow-+; codec-antipode; ≡→≈ℚ)
open import Substrate.Logic.Evidence.GValueAsQ using (gvalue; antipode-of; gvalue-antipode)

------------------------------------------------------------------------
-- The 4-term multiplicative interchange: (a·b)·(c·d) ≈ (a·c)·(b·d).
-- (Pure *ℚ assoc + comm; the abelian-monoid rearrange the cancellation needs.)
------------------------------------------------------------------------

swap4 : (a b c d : ℚ) → ((a *ℚ b) *ℚ (c *ℚ d)) ≈ℚ ((a *ℚ c) *ℚ (b *ℚ d))
swap4 a b c d =
  ≈ℚ-trans {(a *ℚ b) *ℚ (c *ℚ d)} {a *ℚ (b *ℚ (c *ℚ d))} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-assoc a b (c *ℚ d))
  (≈ℚ-trans {a *ℚ (b *ℚ (c *ℚ d))} {a *ℚ ((b *ℚ c) *ℚ d)} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {b *ℚ (c *ℚ d)} {(b *ℚ c) *ℚ d}
       (≈ℚ-refl a) (≈ℚ-sym {(b *ℚ c) *ℚ d} {b *ℚ (c *ℚ d)} (*ℚ-assoc b c d)))
  (≈ℚ-trans {a *ℚ ((b *ℚ c) *ℚ d)} {a *ℚ ((c *ℚ b) *ℚ d)} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {(b *ℚ c) *ℚ d} {(c *ℚ b) *ℚ d}
       (≈ℚ-refl a) (*ℚ-cong {b *ℚ c} {c *ℚ b} {d} {d} (*ℚ-comm b c) (≈ℚ-refl d)))
  (≈ℚ-trans {a *ℚ ((c *ℚ b) *ℚ d)} {a *ℚ (c *ℚ (b *ℚ d))} {(a *ℚ c) *ℚ (b *ℚ d)}
    (*ℚ-cong {a} {a} {(c *ℚ b) *ℚ d} {c *ℚ (b *ℚ d)} (≈ℚ-refl a) (*ℚ-assoc c b d))
    (≈ℚ-sym {(a *ℚ c) *ℚ (b *ℚ d)} {a *ℚ (c *ℚ (b *ℚ d))} (*ℚ-assoc a c (b *ℚ d))))))

------------------------------------------------------------------------
-- The invertible-pole cancellation: if g·h ≈ 1 then gᵏ·hᵏ ≈ 1 for every k.
-- (h is the inverse of g; gᵏ and hᵏ are mutual inverses in the cyclic group.)
------------------------------------------------------------------------

pow-cancel-balanced : (g h : ℚ) → (g *ℚ h) ≈ℚ 1ℚ →
                      (k : ℕ) → (powℚ g k *ℚ powℚ h k) ≈ℚ 1ℚ
pow-cancel-balanced g h gh zero    = *ℚ-identityˡ 1ℚ
pow-cancel-balanced g h gh (suc k) =
  ≈ℚ-trans {(g *ℚ powℚ g k) *ℚ (h *ℚ powℚ h k)}
           {(g *ℚ h) *ℚ (powℚ g k *ℚ powℚ h k)}
           {1ℚ}
    (swap4 g (powℚ g k) h (powℚ h k))
  (≈ℚ-trans {(g *ℚ h) *ℚ (powℚ g k *ℚ powℚ h k)} {1ℚ *ℚ 1ℚ} {1ℚ}
    (*ℚ-cong {g *ℚ h} {1ℚ} {powℚ g k *ℚ powℚ h k} {1ℚ}
       gh (pow-cancel-balanced g h gh k))
    (*ℚ-identityˡ 1ℚ))

------------------------------------------------------------------------
-- THE HEADLINE: the el-atlas antipode extended to the whole cyclic subgroup.
-- G(P)ᵏ · G(¬P)ᵏ ≈ 1 — the rank-1 invertible pole, NO factorisation. (k=1 is
-- exactly `GValueAsQ.gvalue-antipode`.)
------------------------------------------------------------------------

gvalue-power-antipode : (na' db k : ℕ) →
  (powℚ (gvalue na' db) k *ℚ powℚ (antipode-of na' db) k) ≈ℚ 1ℚ
gvalue-power-antipode na' db k =
  pow-cancel-balanced (gvalue na' db) (antipode-of na' db) (gvalue-antipode na' db) k

------------------------------------------------------------------------
-- RANK-n: the free abelian group on n generators. An element of the free
-- abelian group on G-value generators g₁…gₙ is a product ∏ᵢ gᵢ^kᵢ; its
-- inverse is ∏ᵢ hᵢ^kᵢ (hᵢ = recip gᵢ), and they cancel — the rank-n
-- invertible pole, NO unique factorisation. (rank-1 = `pow-cancel-balanced`
-- with the constant list; the per-generator cancellation rides in the pair.)
--
-- A `CancelPair` is a pair (g, h) bundled with its OWN cancellation g·h≈1, so
-- the rank-n statement carries no separate hypothesis vector.
------------------------------------------------------------------------

CancelPair : Set
CancelPair = Σ ℚ (λ g → Σ ℚ (λ h → (g *ℚ h) ≈ℚ 1ℚ))

prodG : List CancelPair → ℚ                 -- ∏ first components
prodG []       = 1ℚ
prodG (p ∷ ps) = proj₁ p *ℚ prodG ps

prodH : List CancelPair → ℚ                 -- ∏ inverse components
prodH []       = 1ℚ
prodH (p ∷ ps) = proj₁ (proj₂ p) *ℚ prodH ps

-- The rank-n cancellation: (∏ gᵢ)·(∏ hᵢ) ≈ 1.  Same shape as the rank-1
-- balanced cancellation (swap4 + cancel head + recurse), now over an
-- ARBITRARY family of independent canceling pairs.
prod-cancel : (ps : List CancelPair) → (prodG ps *ℚ prodH ps) ≈ℚ 1ℚ
prod-cancel []       = *ℚ-identityˡ 1ℚ
prod-cancel (p ∷ ps) =
  ≈ℚ-trans {(proj₁ p *ℚ prodG ps) *ℚ (proj₁ (proj₂ p) *ℚ prodH ps)}
           {(proj₁ p *ℚ proj₁ (proj₂ p)) *ℚ (prodG ps *ℚ prodH ps)}
           {1ℚ}
    (swap4 (proj₁ p) (prodG ps) (proj₁ (proj₂ p)) (prodH ps))
  (≈ℚ-trans {(proj₁ p *ℚ proj₁ (proj₂ p)) *ℚ (prodG ps *ℚ prodH ps)} {1ℚ *ℚ 1ℚ} {1ℚ}
    (*ℚ-cong {proj₁ p *ℚ proj₁ (proj₂ p)} {1ℚ} {prodG ps *ℚ prodH ps} {1ℚ}
       (proj₂ (proj₂ p)) (prod-cancel ps))
    (*ℚ-identityˡ 1ℚ))

-- el-atlas G-values POPULATE CancelPair: each generator G(P)ᵏ pairs with its
-- antipode-power G(¬P)ᵏ, canceling by `gvalue-power-antipode`. So `prod-cancel`
-- over any list of these is the rank-n G-value antipode: a product of G-value
-- powers has the product of antipode powers as its inverse.
gvalue-pow-pair : (na' db k : ℕ) → CancelPair
gvalue-pow-pair na' db k =
  powℚ (gvalue na' db) k , powℚ (antipode-of na' db) k , gvalue-power-antipode na' db k

-- Non-vacuous concrete firing (rank-2): ⟨G(2/1), G(3/2)⟩ with exponents 3,2.
gvalue-rank2-antipode :
  (prodG (gvalue-pow-pair 1 0 3 ∷ gvalue-pow-pair 2 1 2 ∷ [])
   *ℚ prodH (gvalue-pow-pair 1 0 3 ∷ gvalue-pow-pair 2 1 2 ∷ [])) ≈ℚ 1ℚ
gvalue-rank2-antipode = prod-cancel (gvalue-pow-pair 1 0 3 ∷ gvalue-pow-pair 2 1 2 ∷ [])

------------------------------------------------------------------------
-- THE ℤ-POWER CODEC: wiring the invertible pole into the codec INTERFACE.
-- For a base g with an inverse h (g·h≈1), L=ℤ is a GROUP and z ↦ gᶻ is a
-- monoid hom (ℤ,+ℤ,0) → (ℚ,*ℚ,1) — the rank-1 GROUP codec, vs the rank-1
-- MONOID `ℕ-power-codec`. `codec-antipode` then fires NON-trivially through
-- the interface (a genuine inverse↦recip, not just 0+0↦1·1). NO factorisation.
--
-- Negative exponents land on h: expℤ(+n)=gⁿ, expℤ(-suc n)=hⁿ⁺¹. exp-⊕ over the
-- ℤ-addition (routed through `_⊖_`) is 4 cases; the two MIXED-sign cases are the
-- `_⊖_`-recursive cancellation `mix` (the conditional ∸ cancellation the rank-1
-- balanced pole did not need), itself a clean 3-case induction reusing `swap4`.
------------------------------------------------------------------------

module ZPow (g h : ℚ) (gh : (g *ℚ h) ≈ℚ 1ℚ) where

  expℤ : ℤ → ℚ
  expℤ (+ n)    = powℚ g n
  expℤ (-suc n) = powℚ h (suc n)

  -- one cancellation step: (g·gᵐ)·(h·hⁿ) ≈ gᵐ·hⁿ  (peel a matched g·h≈1 pair).
  cancel-step : (m n : ℕ) →
    ((g *ℚ powℚ g m) *ℚ (h *ℚ powℚ h n)) ≈ℚ (powℚ g m *ℚ powℚ h n)
  cancel-step m n =
    ≈ℚ-trans {(g *ℚ powℚ g m) *ℚ (h *ℚ powℚ h n)}
             {(g *ℚ h) *ℚ (powℚ g m *ℚ powℚ h n)}
             {powℚ g m *ℚ powℚ h n}
      (swap4 g (powℚ g m) h (powℚ h n))
    (≈ℚ-trans {(g *ℚ h) *ℚ (powℚ g m *ℚ powℚ h n)}
              {1ℚ *ℚ (powℚ g m *ℚ powℚ h n)} {powℚ g m *ℚ powℚ h n}
      (*ℚ-cong {g *ℚ h} {1ℚ} {powℚ g m *ℚ powℚ h n} {powℚ g m *ℚ powℚ h n}
         gh (≈ℚ-refl (powℚ g m *ℚ powℚ h n)))
      (*ℚ-identityˡ (powℚ g m *ℚ powℚ h n)))

  -- the mixed-sign cancellation: expℤ(a ⊖ b) ≈ gᵃ·hᵇ, by induction on `_⊖_`.
  mix : (a b : ℕ) → expℤ (a ⊖ b) ≈ℚ (powℚ g a *ℚ powℚ h b)
  mix a       zero    = ≈ℚ-sym {powℚ g a *ℚ 1ℚ} {powℚ g a} (*ℚ-identityʳ (powℚ g a))
  mix zero    (suc n) = ≈ℚ-sym {1ℚ *ℚ powℚ h (suc n)} {powℚ h (suc n)}
                          (*ℚ-identityˡ (powℚ h (suc n)))
  mix (suc m) (suc n) =
    ≈ℚ-trans {expℤ (m ⊖ n)} {powℚ g m *ℚ powℚ h n}
             {(g *ℚ powℚ g m) *ℚ (h *ℚ powℚ h n)}
      (mix m n)
      (≈ℚ-sym {(g *ℚ powℚ g m) *ℚ (h *ℚ powℚ h n)} {powℚ g m *ℚ powℚ h n}
        (cancel-step m n))

  exp-⊕ℤ : (x y : ℤ) → expℤ (x +ℤ y) ≈ℚ (expℤ x *ℚ expℤ y)
  exp-⊕ℤ (+ m)    (+ n)    = pow-+ g m n
  exp-⊕ℤ (+ m)    (-suc n) = mix m (suc n)
  exp-⊕ℤ (-suc m) (+ n)    =
    ≈ℚ-trans {expℤ (n ⊖ suc m)} {powℚ g n *ℚ powℚ h (suc m)}
             {powℚ h (suc m) *ℚ powℚ g n}
      (mix n (suc m)) (*ℚ-comm (powℚ g n) (powℚ h (suc m)))
  exp-⊕ℤ (-suc m) (-suc n) =
    -- (-suc m)+ℤ(-suc n) = -suc suc (m+n); pow-+'s index suc m + suc n
    -- = suc (m + suc n) needs +-suc to meet suc (suc (m + n)).
    ≈ℚ-trans {powℚ h (suc (suc (m + n)))} {powℚ h (suc m + suc n)}
             {powℚ h (suc m) *ℚ powℚ h (suc n)}
      (≡→≈ℚ {powℚ h (suc (suc (m + n)))} {powℚ h (suc m + suc n)}
         (cong (powℚ h) (cong suc (sym (+-suc m n)))))
      (pow-+ h (suc m) (suc n))

  ℤ-power-codec : ExpLogCodecℚ
  ℤ-power-codec = record
    { L     = ℤ
    ; _⊕_   = _+ℤ_
    ; 𝟘     = + zero
    ; expL  = expℤ
    ; exp-⊕ = exp-⊕ℤ
    ; exp-𝟘 = ≈ℚ-refl 1ℚ
    }

  -- The codec fires NON-trivially: (+1) +ℤ (-suc 0) = 1⊖1 = 0⊖0 = +0 = 𝟘, so
  -- codec-antipode gives g¹·h¹ ≈ 1 — a genuine inverse↦recip through the
  -- ExpLogCodec interface (vs ℕ-power-codec's degenerate 0+0).
  ℤpow-antipode-fires : (expℤ (+ 1) *ℚ expℤ (-suc 0)) ≈ℚ 1ℚ
  ℤpow-antipode-fires = codec-antipode ℤ-power-codec (+ 1) (-suc 0) refl

-- The el-atlas instance: every G-value g and its antipode form a ℤ-power codec.
gvalue-ℤ-codec : (na' db : ℕ) → ExpLogCodecℚ
gvalue-ℤ-codec na' db =
  ZPow.ℤ-power-codec (gvalue na' db) (antipode-of na' db) (gvalue-antipode na' db)
