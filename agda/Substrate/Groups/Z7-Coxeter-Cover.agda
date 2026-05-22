------------------------------------------------------------------------
-- Substrate.Groups.Z7-Coxeter-Cover
--
-- Canonical-cover for Z₇-Coxeter: dispatches a 7-tuple of per-position
-- proofs onto any `Z₇.Canonical w`. Sibling of the in-core
-- canonical-cover-Z2 / canonical-cover-Z3 / canonical-cover-Z4 and the
-- companion file Z5-Coxeter-Cover.
--
-- Lives in a separate module because Z7-Coxeter is over the one-pass-
-- rewrite threshold (queued for decomposition).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Z7-Coxeter-Cover where

open import Substrate.Foundation.Product using (_×_; _,_)
open import Substrate.Groups.Z7-Coxeter
  using (Canonical; c-ε; c-a; c-aa; c-aaa; c-aaaa; c-aaaaa; c-aaaaaa)

canonical-cover :
  ∀ {ℓ} (P : ∀ {w} → Canonical w → Set ℓ) →
  P c-ε × P c-a × P c-aa × P c-aaa × P c-aaaa × P c-aaaaa × P c-aaaaaa →
  ∀ {w} (c : Canonical w) → P c
canonical-cover _ (p , _ , _ , _ , _ , _ , _) c-ε      = p
canonical-cover _ (_ , p , _ , _ , _ , _ , _) c-a      = p
canonical-cover _ (_ , _ , p , _ , _ , _ , _) c-aa     = p
canonical-cover _ (_ , _ , _ , p , _ , _ , _) c-aaa    = p
canonical-cover _ (_ , _ , _ , _ , p , _ , _) c-aaaa   = p
canonical-cover _ (_ , _ , _ , _ , _ , p , _) c-aaaaa  = p
canonical-cover _ (_ , _ , _ , _ , _ , _ , p) c-aaaaaa = p
