------------------------------------------------------------------------
-- Substrate.Groups.Coxeter.Cyclic.Core
--
-- The lemmas that complete the Coxeter framework:
--   * power-canonical-bounded: normalize is identity on bounded power
--   * canonical-is-fixed (via canonical-cover-ex + the bounded lemma)
--   * iter / iter-insert-pos / insert-cycle-id-word
--   * normalize-power-prepend
--   * insert-append-lemma
--   * Opens WithLemmas — final layer giving _·_, _≈_, normalize-distrib, etc.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

open import Substrate.Foundation.Nat.Le
open import Substrate.Foundation.Nat.Lt
open import Substrate.Foundation.Nat.Lt2
open import Substrate.Foundation.Nat.Nat
open import Substrate.Foundation.Nat.Properties.Order using (≤-suc-r; <-irrefl)
open import Substrate.Foundation.Fin.Fin
open import Substrate.Foundation.Fin.To
open import Substrate.Foundation.Fin.Properties using (toℕ-bound)
open import Substrate.Foundation.Empty.BotElim
open import Substrate.Foundation.Negation.Dec
open import Substrate.Foundation.Negation.Not
open import Substrate.Foundation.Product using (_,_)

open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_; _++_)
open import Substrate.Groups.Coxeter.Word.Length using (length)
open import Substrate.Foundation.Fin.Iterate
  using (σ-iterate)
open import Substrate.Foundation.Eq
open import Substrate.Foundation.Eq.Cong
open import Substrate.Foundation.Eq.Sym
open import Substrate.Foundation.Eq.Trans
open import Substrate.Foundation.Eq.Subst
open import Substrate.Groups.Coxeter.Cyclic.Base.Gen
open import Substrate.Groups.Coxeter.Cyclic.Base.CanonicalAt

module Substrate.Groups.Coxeter.Cyclic.Core (n : ℕ) where

-- ⚑ WAS `open import …Cyclic.Bridge n using (…4 names…)` — a module DISSOLVED by
-- the ban-decompose commit (771283c8) into one leaf per theorem.  The split ran
-- correctly; the REWIRE did not, so this line named a module with no file and the
-- build reported [FileNotFound] here.  That is the `file-not-found` reservoir the
-- re-export census warns about, arriving by the other route: not a retired
-- conduit, but a decomposed parent whose consumer was never repointed.
--
-- ⚑ AND IT IS THE ROOT OF A 14-MODULE BLOCK.  Every Zn-Coxeter, -Fin and -Group
-- module in the tree is `dependency`-failing behind this single line.
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerAdvance n
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerEq n
open import Substrate.Groups.Coxeter.Cyclic.Bridge.NotLtEqN n
open import Substrate.Groups.Coxeter.Cyclic.Bridge.InsertPowerWrap n
open import Substrate.Groups.Coxeter.Cyclic.Base n using (power; insert; a; Gen; σ; c-here; σ-HasOrderPerm)
-- ⛑ Ⓡ2ᵈ: the `Defs` LEAVES this shard cites, derived by
-- `rewire_fcr --siblings Defs <file>` — a SET, not a prefix. `Defs`'s
-- re-opens are bare (Ⓡ1), so a leaf-defined name no longer arrives
-- through the root. Each leaf carries its OWN minimal telescope, so the
-- argument lists differ by leaf and are read from each header.
open import Substrate.Groups.Coxeter.Cyclic.Base.HasOrderPerm n
open import Substrate.Groups.Coxeter.Cyclic.Base.Insert n
open import Substrate.Groups.Coxeter.Cyclic.Base.Op n
open import Substrate.Groups.Coxeter.Cyclic.Base.Power
open import Substrate.Groups.Coxeter.Cyclic.Existential n
-- ⚑⚑ `normalize` / `normalize-canonical` / `WithLemmas` CAME THROUGH A SECOND
-- CONDUIT (Ⓑ2c-BRIDGE10″).  Pre-split, `Core` read `open import …Existential n
-- public` and `Existential` in turn opened `ListPresentation` — so all three
-- arrived two hops away, named nowhere.  `--provides` now shows `Existential`
-- exporting six names, none of them these.
--
-- ⚑ AND `normalize` HAS NINE HOMES, so no tool could pick one: what makes it
-- decidable is PROVENANCE, not the index — the pre-split parent's own comment
-- ("Opens ListPresentation's outer module — provides normalize +
-- normalize-canonical") names which of the nine this is.  That is the case
-- `agda_defs <name>` correctly refuses and `--at <rev>` answers.
-- ⚑ APPLIED to its five-parameter telescope (Gen, Canonical, canonical-ε,
-- insert, insert-canonical) — the arguments the dissolved conduit was supplying
-- invisibly.  Naming them here is the dependency becoming explicit.
open import Substrate.Groups.Coxeter.ListPresentation
  Gen Canonical-ex c-ε insert insert-canonical-ex

------------------------------------------------------------------------
-- power-canonical-bounded: normalize fixes power words within bound.
------------------------------------------------------------------------

power-canonical-bounded : (k : ℕ) → k < suc n → normalize (power k) ≡ power k
power-canonical-bounded zero    _         = refl
power-canonical-bounded (suc k) (s≤s k<n) =
  trans (cong (insert a) (power-canonical-bounded k (≤-suc-r k<n)))
        (insert-power-advance k k<n)

------------------------------------------------------------------------
-- canonical-is-fixed for the existential view.
------------------------------------------------------------------------

canonical-is-fixed : {w : Word Gen} → Canonical-ex w → normalize w ≡ w
canonical-is-fixed =
  canonical-cover-ex (λ {w} _ → normalize w ≡ w)
    (λ k → power-canonical-bounded (toℕ k) (toℕ-bound k))

------------------------------------------------------------------------
-- iter / iter-insert-pos / insert-cycle-id-word — the Word-level
-- cycle property derived from σ-HasOrderPerm via insert-power-eq.
------------------------------------------------------------------------

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
-- normalize-power-prepend: normalize (power k ++ w₂) ≡ iter k (insert a) (normalize w₂).
------------------------------------------------------------------------

normalize-power-prepend : (k : ℕ) (w₂ : Word Gen) →
                         normalize (power k ++ w₂) ≡ iter k (insert a) (normalize w₂)
normalize-power-prepend zero    w₂ = refl
normalize-power-prepend (suc k) w₂ = cong (insert a) (normalize-power-prepend k w₂)

------------------------------------------------------------------------
-- insert-append-lemma: case-split on whether k is the last position.
------------------------------------------------------------------------

insert-append-lemma : (g : Gen) {w : Word Gen} (w₂ : Word Gen) → Canonical-ex w →
                     normalize (insert g w ++ w₂) ≡ insert g (normalize (w ++ w₂))

open WithLemmas canonical-is-fixed insert-append-lemma public
insert-append-lemma a w₂ (k , c-here .k) with toℕ k <? n
... | yes p
  rewrite insert-power-advance (toℕ k) p
  = refl
... | no ¬p
  rewrite not-lt-eq-n k ¬p
        | insert-power-wrap
        | normalize-power-prepend n w₂
  = sym (insert-cycle-id-word (normalize-canonical w₂))

------------------------------------------------------------------------
-- Open WithLemmas to inherit the abstract Core surface
-- (_·_, _≈_, ε, normalize-distrib, etc.).
------------------------------------------------------------------------

