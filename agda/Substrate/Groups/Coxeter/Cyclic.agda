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
-- 14. Existential view of Canonical — needed to integrate with the
-- substrate's Coxeter.ListPresentation framework which expects a
-- single-index Canonical : Word Gen → Set.
------------------------------------------------------------------------

open import Substrate.Foundation.Product using (Σ; _,_; proj₁; proj₂)

Canonical-ex : Word Gen → Set
Canonical-ex w = Σ (Fin (suc n)) (Canonical w)

c-ε : Canonical-ex []
c-ε = zero , c-here zero

canonical-cover-ex :
  ∀ {ℓ} (P : ∀ {w} → Canonical-ex w → Set ℓ) →
  ((k : Fin (suc n)) → P (k , c-here k)) →
  ∀ {w} (c : Canonical-ex w) → P c
canonical-cover-ex P f (k , c-here .k) = f k

insert-canonical-ex : (g : Gen) {w : Word Gen} → Canonical-ex w → Canonical-ex (insert g w)
insert-canonical-ex g (k , c) = σ k , insert-canonical g c

inv-canonical-ex : ∀ {w} → Canonical-ex w → Canonical-ex (inv w)
inv-canonical-ex (k , c) = inv-pos k , inv-canonical c

------------------------------------------------------------------------
-- 15. Open ListPresentation's outer module — provides normalize +
-- normalize-canonical. WithLemmas (the inner sub-module) is opened
-- AFTER we prove canonical-is-fixed + insert-append-lemma below.
------------------------------------------------------------------------

open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex public

------------------------------------------------------------------------
-- 16. power-canonical-bounded: normalize is identity on power words
-- below the cycle boundary. Structural induction on k.
------------------------------------------------------------------------

private
  -- For k < n, insert a (power k) simply prepends `a`.
  insert-power-advance : (k : ℕ) → k < n → insert a (power k) ≡ a ∷ power k
  insert-power-advance k k<n
    with length (power k) <? n | length-power k
  ... | yes _  | _    = refl
  ... | no  ¬p | l≡k  = ⊥-elim (¬p (subst (λ x → x < n) (sym l≡k) k<n))

  -- For k = n, insert a (power n) wraps to [].
  insert-power-wrap : insert a (power n) ≡ []
  insert-power-wrap
    with length (power n) <? n | length-power n
  ... | yes p  | l≡n  = ⊥-elim (<-irrefl n (subst (λ x → x < n) l≡n p))
  ... | no  _  | _    = refl

power-canonical-bounded : (k : ℕ) → k < suc n → normalize (power k) ≡ power k
power-canonical-bounded zero    _         = refl
power-canonical-bounded (suc k) (s≤s k<n) =
  trans (cong (insert a) (power-canonical-bounded k (≤-suc-r k<n)))
        (insert-power-advance k k<n)

------------------------------------------------------------------------
-- 17. canonical-is-fixed for the existential Canonical-ex view.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical-ex w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover-ex (λ {w} _ → normalize w ≡ w)
    (λ k → power-canonical-bounded (toℕ k) (toℕ-bound k))

------------------------------------------------------------------------
-- 18. iter / iter-insert lemmas, derived insert-cycle-id-word.
--
-- iter m f x = f^m x. Connects per-Word iterated-insert to per-Fin
-- σ-iterate via the insert-power-eq bridge. Then σ-HasOrderPerm gives
-- iter (suc n) (insert a) w ≡ w for canonical w.
------------------------------------------------------------------------

open import Substrate.Algebra.F2.Linear.FromImages.Permutation.Iterate
  using (σ-iterate)

iter : ℕ → (Word Gen → Word Gen) → Word Gen → Word Gen
iter zero    f x = x
iter (suc m) f x = f (iter m f x)

private
  iter-insert-pos : (m : ℕ) (k : Fin (suc n)) →
                    iter m (insert a) (power (toℕ k)) ≡ power (toℕ (σ-iterate m σ k))
  iter-insert-pos zero    k = refl
  iter-insert-pos (suc m) k =
    trans (cong (insert a) (iter-insert-pos m k))
          (insert-power-eq (σ-iterate m σ k))

insert-cycle-id-word : ∀ {w} → Canonical-ex w → iter (suc n) (insert a) w ≡ w
insert-cycle-id-word (k , c-here .k) =
  trans (iter-insert-pos (suc n) k)
        (cong (λ k' → power (toℕ k')) (σ-HasOrderPerm k))

------------------------------------------------------------------------
-- 19. normalize-power-prepend: normalize on (power k ++ w₂) reduces
-- by iteration of insert a. Inductive on k.
------------------------------------------------------------------------

normalize-power-prepend : (k : ℕ) (w₂ : Word Gen) →
                         normalize (power k ++ w₂) ≡ iter k (insert a) (normalize w₂)
normalize-power-prepend zero    w₂ = refl
normalize-power-prepend (suc k) w₂ = cong (insert a) (normalize-power-prepend k w₂)

------------------------------------------------------------------------
-- 20. insert-append-lemma for the existential Canonical-ex view.
--
-- Case-splits on `toℕ k <? n`:
--   yes (k < last): insert advances, both sides reduce to insert a
--     (normalize (power (toℕ k) ++ w₂)) by normalize's definition.
--   no  (k = last): insert wraps to [], use insert-cycle-id-word +
--     normalize-power-prepend.
------------------------------------------------------------------------

insert-append-lemma : (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical-ex w →
                     normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))
insert-append-lemma a w₂ (k , c-here .k) with toℕ k <? n
... | yes p
  rewrite insert-power-advance (toℕ k) p
  = refl  -- normalize (a ∷ (power (toℕ k) ++ w₂)) = insert a (normalize (power (toℕ k) ++ w₂))
... | no ¬p
  rewrite not-lt-eq-n k ¬p
        | insert-power-wrap
        | normalize-power-prepend n w₂
  = sym (insert-cycle-id-word (normalize-canonical w₂))

------------------------------------------------------------------------
-- 21. Open WithLemmas — derives normalize-distrib + the abstract Core
-- surface (_·_, _≈_, ε, normalize-idem/append/distrib/triple/quad,
-- ≉-idem, clash, ++-assoc-4, etc.).
------------------------------------------------------------------------

open WithLemmas canonical-is-fixed insert-append-lemma public

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
