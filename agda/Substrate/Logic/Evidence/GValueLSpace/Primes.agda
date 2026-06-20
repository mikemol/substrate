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

open import Substrate.Foundation.Nat using (ℕ; zero; suc)
open import Substrate.Algebra.Q using (ℚ; 1ℚ)
open import Substrate.Algebra.Q.Mul using (_*ℚ_)
open import Substrate.Algebra.Q.Equiv using (_≈ℚ_; ≈ℚ-refl; ≈ℚ-sym; ≈ℚ-trans)
open import Substrate.Algebra.Q.Properties.Field using (*ℚ-assoc; *ℚ-comm; *ℚ-identityˡ)
open import Substrate.Algebra.Q.Properties.Congruence using (*ℚ-cong)
open import Substrate.Logic.Evidence.GValueLSpace using (powℚ)
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
