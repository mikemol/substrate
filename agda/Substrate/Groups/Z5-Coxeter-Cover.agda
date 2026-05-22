------------------------------------------------------------------------
-- Substrate.Groups.Z5-Coxeter-Cover
--
-- Canonical-cover for Z₅-Coxeter: dispatches a 5-tuple of per-position
-- proofs onto any `Z₅.Canonical w`. Sibling of the in-core
-- canonical-cover-Z2 / canonical-cover-Z3 / canonical-cover-Z4 from
-- their respective Z_n-Coxeter modules.
--
-- Lives in a separate module because Z5-Coxeter is already over the
-- one-pass-rewrite threshold (queued for decomposition; see slice
-- plan). Once Z5-Coxeter is decomposed, this cover will move back into
-- a per-concern submodule (`Z5-Coxeter/Cover.agda`).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z5-Coxeter-Cover where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.Z5-Coxeter using (Canonical; c-ε; c-a; c-aa; c-aaa; c-aaaa)

canonical-cover-Z5 :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa × P c-aaaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover-Z5 _ (p , _ , _ , _ , _) c-ε    = p
canonical-cover-Z5 _ (_ , p , _ , _ , _) c-a    = p
canonical-cover-Z5 _ (_ , _ , p , _ , _) c-aa   = p
canonical-cover-Z5 _ (_ , _ , _ , p , _) c-aaa  = p
canonical-cover-Z5 _ (_ , _ , _ , _ , p) c-aaaa = p
