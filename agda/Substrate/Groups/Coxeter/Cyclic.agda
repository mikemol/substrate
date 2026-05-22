------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic
--
-- Path 2 of the typed-holes-Fin study: a length-indexed Canonical
-- for the cyclic Coxeter family, parametric in the order.
--
-- Phase 1 (this slice): foundational types + the structural floor
-- of the bijection chain. The per-n constructor enumeration (c-ε,
-- c-a, c-aa, …) is replaced by a single Fin-indexed constructor.
-- canonical-to-Fin / Fin-to-canonical / canonical-cover come free.
-- σ + σ-HasOrderPerm pull in from cyclic-suc / cyclic-suc-HasOrderPerm
-- (Slice 4).
--
-- Phase 2 (next slice): prove the insert/insert-canonical bridge to
-- the existing Coxeter.Core / GroupAdapter / Strict2Monoid frameworks
-- (requires aligning insert's length-check with-clause with cyclic-suc's
-- mod-suc-bound with-clause — non-trivial proof work).
--
-- Phase 3: integrate with Coxeter-Fin-Generic + collapse each
-- Zₙ-Coxeter-Fin to a single-line `open import` of `Cyclic <order>`.
--
-- Phase 4: migrate per-Zₙ-Coxeter cores to use this module (touches
-- 5 core files + the downstream chain).
--
-- Per [[expose-generator-not-orbit]]: the structural floor surfaced
-- by the typed-holes study (per-n c-aᵏ constructors in Fin-to-canonical's
-- payload) IS exactly the named-constructor enumeration this module
-- obsoletes. After Phase 4, the entire cyclic-Coxeter family becomes
-- a single parametric module + 5 thin Zₙ-instance shims.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_; _∸_; _<_; _<?_; s≤s; z≤n)
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r; <-irrefl)
open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ; fromℕ<)
open import Substrate.Foundation.Fin.Properties using (toℕ-bound; toℕ-fromℕ<)
open import Substrate.Foundation.Eq using (_≡_; refl; cong; sym; trans; subst)
open import Substrate.Foundation.Empty using (⊥-elim)
open import Substrate.Foundation.Negation using (Dec; yes; no; ¬_)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Algebra.Nat.Mod
  using (_mod-suc_; mod-suc-bound; suc-mod-suc-lt; suc-mod-suc-self)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation
  using (HasOrderPerm)
open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Cyclic
  using (cyclic-suc; cyclic-suc-toℕ; cyclic-suc-HasOrderPerm)

module Substrate.Groups.Coxeter.Cyclic (n : ℕ) where

------------------------------------------------------------------------
-- 1. The shared single-generator Gen.
--
-- Every cyclic Coxeter instance shares this: ⟨a | aⁿ⁺¹ = ε⟩. We
-- parameterize by `n` where the group order = suc n; the Fin index
-- ranges over Fin (suc n).
------------------------------------------------------------------------

data Gen : Set where
  a : Gen

------------------------------------------------------------------------
-- 2. power k = aᵏ as a Word.
------------------------------------------------------------------------

power : ℕ → Word Gen
power zero    = []
power (suc k) = a ∷ power k

length-power : (k : ℕ) → length (power k) ≡ k
length-power zero    = refl
length-power (suc k) = cong suc (length-power k)

------------------------------------------------------------------------
-- 3. Canonical w k — length-indexed, one structural constructor.
--
-- The per-Zₙ named constructors (c-ε / c-a / c-aa / …, n+1 of them
-- per file) collapse into one structural constructor `c-here k` for
-- k : Fin (suc n). The Fin index packages "which canonical position";
-- the word `power (toℕ k)` is determined by the index.
------------------------------------------------------------------------

data Canonical : Word Gen → Fin (suc n) → Set where
  c-here : (k : Fin (suc n)) → Canonical (power (toℕ k)) k

------------------------------------------------------------------------
-- 4. canonical-cover — Fin-indexed dispatch.
--
-- Replaces per-Zₙ canonical-cover (n+1-tuple of values + n+1-case
-- pattern-match on c-ε / c-a / …). One uniform combinator: supply
-- a per-position function f : (k : Fin (suc n)) → P (c-here k).
------------------------------------------------------------------------

canonical-cover :
  ∀ {ℓ} (P : ∀ {w k} → Canonical w k → Set ℓ) →
  ((k : Fin (suc n)) → P (c-here k)) →
  ∀ {w k} (c : Canonical w k) → P c
canonical-cover P f (c-here k) = f k

------------------------------------------------------------------------
-- 5. Bijection between Canonical and Fin (suc n) — by construction.
--
-- canonical-to-Fin = the position index.
-- Fin-to-canonical = the inhabitant at each position.
-- Both round-trips are refl by definition.
------------------------------------------------------------------------

canonical-to-Fin : ∀ {w k} → Canonical w k → Fin (suc n)
canonical-to-Fin (c-here k) = k

Fin-to-canonical : (k : Fin (suc n)) → Canonical (power (toℕ k)) k
Fin-to-canonical k = c-here k

Fin-roundtrip : (k : Fin (suc n)) →
  canonical-to-Fin (Fin-to-canonical k) ≡ k
Fin-roundtrip _ = refl

-- The dependent roundtrip would need a heterogeneous-equality form
-- since `Fin-to-canonical k` returns a Canonical at a specific word
-- determined by k. The Fin-side roundtrip + the c-here invariant
-- (which makes the position determine the word) suffice for downstream
-- use; the dependent direction lives at Phase 3.

------------------------------------------------------------------------
-- 6. σ — the cyclic successor + structural HasOrderPerm.
--
-- σ is cyclic-suc {n} : Fin (suc n) → Fin (suc n); the order-(suc n)
-- property is cyclic-suc-HasOrderPerm {n} from Slice 4 — derived
-- structurally via mod-suc reasoning, no per-position enumeration.
------------------------------------------------------------------------

σ : Fin (suc n) → Fin (suc n)
σ = cyclic-suc {n}

σ-HasOrderPerm : HasOrderPerm σ (suc n)
σ-HasOrderPerm = cyclic-suc-HasOrderPerm {n}

------------------------------------------------------------------------
-- 7. insert — the cyclic Word-level shift.
--
-- For length w < n (room to advance), prepend `a`; for length w ≥ n
-- (must wrap), produce ε. On canonical inputs at position k, this
-- realises cyclic-suc k (the next-position word).
--
-- The proof that `insert a (power (toℕ k)) ≡ power (toℕ (σ k))` —
-- the bridge to insert-canonical — is Phase 2 (requires aligning
-- insert's length-check with-clause with cyclic-suc's mod-suc-bound
-- with-clause via mod-suc-id + the length-power identity above).
------------------------------------------------------------------------

insert : Gen → Word Gen → Word Gen
insert g w with length w <? n
... | yes _ = g ∷ w
... | no  _ = []

------------------------------------------------------------------------
-- 8. The bridge: insert a (power (toℕ k)) ≡ power (toℕ (σ k)).
--
-- Case-splits on `toℕ k <? n` (the "room to advance" vs "wrap"
-- decision); in each case aligns insert's length-check with-clause
-- (via length-power) and cyclic-suc's mod-suc-bound with-clause
-- (via suc-mod-suc-lt / suc-mod-suc-self).
------------------------------------------------------------------------

private
  -- For k : Fin (suc n) where ¬ (toℕ k < n), toℕ k must equal n
  -- (since toℕ k < suc n by Fin's bound).
  not-lt-aux : (x y : ℕ) → x < suc y → ¬ (x < y) → x ≡ y
  not-lt-aux zero    zero    _              _      = refl
  not-lt-aux zero    (suc y) _              ¬0<sy  = ⊥-elim (¬0<sy (s≤s z≤n))
  not-lt-aux (suc x) zero    (s≤s ())       _
  not-lt-aux (suc x) (suc y) (s≤s x<sy)     ¬sx<sy = cong suc
    (not-lt-aux x y x<sy (λ x<y → ¬sx<sy (s≤s x<y)))

  not-lt-eq-n : (k : Fin (suc n)) → ¬ (toℕ k < n) → toℕ k ≡ n
  not-lt-eq-n k ¬k<n = not-lt-aux (toℕ k) n (toℕ-bound k) ¬k<n

  -- Bridge cases.
  insert-power-eq-yes : (k : Fin (suc n)) → toℕ k < n →
                        insert a (power (toℕ k)) ≡ power (toℕ (cyclic-suc {n} k))
  insert-power-eq-yes k k<n
    rewrite cyclic-suc-toℕ k
          | suc-mod-suc-lt (toℕ k) n k<n
    with length (power (toℕ k)) <? n | length-power (toℕ k)
  ... | yes _  | _     = refl
  ... | no  ¬p | l≡tk  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡tk) k<n))

  insert-power-eq-no : (k : Fin (suc n)) → ¬ (toℕ k < n) →
                       insert a (power (toℕ k)) ≡ power (toℕ (cyclic-suc {n} k))
  insert-power-eq-no k ¬k<n
    rewrite cyclic-suc-toℕ k
          | not-lt-eq-n k ¬k<n
          | suc-mod-suc-self n
    with length (power n) <? n | length-power n
  ... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
  ... | no  _  | _    = refl

insert-power-eq : (k : Fin (suc n)) →
                  insert a (power (toℕ k)) ≡ power (toℕ (cyclic-suc {n} k))
insert-power-eq k with toℕ k <? n
... | yes p  = insert-power-eq-yes k p
... | no  ¬p = insert-power-eq-no k ¬p

------------------------------------------------------------------------
-- 9. insert-canonical: the cyclic property at the Canonical level.
------------------------------------------------------------------------

insert-canonical : (g : Gen) {w : Word Gen} {k : Fin (suc n)} →
                   Canonical w k → Canonical (insert g w) (cyclic-suc {n} k)
insert-canonical a (c-here k) =
  subst (λ w → Canonical w (cyclic-suc {n} k))
    (sym (insert-power-eq k))
    (c-here (cyclic-suc {n} k))

------------------------------------------------------------------------
-- 10. action-of-a-is-σ — structurally trivial at the position-index level.
------------------------------------------------------------------------

action-of-a-pos : (k : Fin (suc n)) →
                  canonical-to-Fin (c-here (σ k)) ≡ σ (canonical-to-Fin (c-here k))
action-of-a-pos _ = refl

------------------------------------------------------------------------
-- 11. inv-pos — the inverse position via (suc n ∸ toℕ k) mod-suc n.
--
-- For k = zero: inv-pos zero = zero (since (suc n) mod-suc n = 0).
-- For k > 0: inv-pos k has toℕ = suc n ∸ toℕ k.
-- Involutive: inv-pos (inv-pos k) ≡ k.
--
-- Cyclic-group inversion at the index level: for cyclic Zₙ₊₁, the
-- inverse of position k is position (n+1 ∸ k) mod (n+1).
------------------------------------------------------------------------

inv-pos : Fin (suc n) → Fin (suc n)
inv-pos k = fromℕ< (mod-suc-bound (suc n ∸ toℕ k) n)

------------------------------------------------------------------------
-- 12. Word-level inv via length-check + inv-pos.
--
-- For canonical inputs (length w ≤ n, i.e., < suc n), inv computes
-- the canonical word at the inverse position. For non-canonical
-- inputs (length > n), fallback to the input itself.
------------------------------------------------------------------------

inv : Word Gen → Word Gen
inv w with length w <? suc n
... | yes p = power (toℕ (inv-pos (fromℕ< p)))
... | no  _ = w

------------------------------------------------------------------------
-- 13. inv-canonical — the structural property.
--
-- For Canonical w k, the inv-result is Canonical at position inv-pos k.
-- Proved via the bridge `inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))`
-- using fromℕ<-toℕ + length-power roundtrips.
------------------------------------------------------------------------

private
  -- For k : Fin (suc n), `fromℕ< (length-bound)` recovers k.
  fromℕ<-power-toℕ : (k : Fin (suc n))
                   → (p : length (power (toℕ k)) < suc n)
                   → fromℕ< p ≡ k
  fromℕ<-power-toℕ k p
    rewrite length-power (toℕ k) = fromℕ<-toℕ-id k p
    where
      open import Substrate.Foundation.Eq using (sym)
      -- fromℕ< using toℕ-bound equals the original. We prove via
      -- toℕ-injective + toℕ-fromℕ<.
      fromℕ<-toℕ-id : ∀ (k : Fin (suc n)) (p : toℕ k < suc n) → fromℕ< p ≡ k
      fromℕ<-toℕ-id k p = aux k p
        where
          open import Substrate.Foundation.Fin using (Fin; zero; suc; toℕ)
          aux : ∀ {m} (k : Fin m) (p : toℕ k < m) → fromℕ< p ≡ k
          aux {suc m} zero    (s≤s _)   = refl
          aux {suc m} (suc k) (s≤s p')  = cong suc (aux k p')

  inv-power-eq : (k : Fin (suc n)) →
                 inv (power (toℕ k)) ≡ power (toℕ (inv-pos k))
  inv-power-eq k with length (power (toℕ k)) <? suc n | length-power (toℕ k)
  ... | yes p | _    = cong (λ x → power (toℕ (inv-pos x))) (fromℕ<-power-toℕ k p)
  ... | no ¬p | l≡tk = ⊥-elim (¬p (subst (λ x → x < suc n) (sym l≡tk) (toℕ-bound k)))

inv-canonical : ∀ {w} {k : Fin (suc n)} → Canonical w k → Canonical (inv w) (inv-pos k)
inv-canonical (c-here k) =
  subst (λ w → Canonical w (inv-pos k)) (sym (inv-power-eq k)) (c-here (inv-pos k))

------------------------------------------------------------------------
-- Capstone — Phase 1 complete.
--
-- Landed: Gen, power, length-power, Canonical (Fin-indexed),
-- canonical-cover, canonical-to-Fin, Fin-to-canonical, round-trips,
-- σ, σ-HasOrderPerm, insert, action-of-a-pos.
--
-- Pending (Phase 2):
--   * insert-canonical : (g) {w k} → Canonical w k → Canonical (insert g w) (σ k)
--     Requires the algebraic bridge `insert a (power (toℕ k)) ≡ power (toℕ (σ k))`,
--     which case-splits on `toℕ k < n` vs `toℕ k = n` and aligns with
--     cyclic-suc's mod-suc-bound with-clause via mod-suc-id /
--     mod-suc periodicity. ~30-50 lines of careful proof work.
--
-- Pending (Phase 3):
--   * Integrate with Substrate.Groups.Coxeter-Fin-Generic. The Generic
--     currently takes `Canonical : Word Gen → Set` (single-index); the
--     Cyclic version is Fin-indexed. Either generalise the Generic or
--     provide a `Canonical-existential w = Σ (Fin (suc n)) (Canonical w)`
--     view that bridges.
--
-- Pending (Phase 4):
--   * Migrate each Zₙ-Coxeter to use Cyclic — converts the per-Zₙ
--     constructor enumeration + insert table + inv table into thin
--     instances. Downstream code that pattern-matches on c-ε / c-a /
--     c-aa needs updating; compatibility shims may help.
------------------------------------------------------------------------
