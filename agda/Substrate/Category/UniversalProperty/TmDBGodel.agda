------------------------------------------------------------------------
-- Substrate.Category.UniversalProperty.TmDBGodel
--
-- ⟡odecode-B-godel (Phase B of ⟡ta-upterm-O-decode): the OBJECT-SYNTAX
-- Gödel codec — the DEFINITIONS (proof-free; the round-trip proofs + the
-- split-Canonical apex live in the .Properties sibling, per the def/proof
-- separation policy so this datatype-exporting module's closure stays lean).
--
-- The object universe O (ObjectUniverse.agda) is the witness tower; its rungs
-- carry OBJECT CODES. This module builds the code carrier: `TmDB` — de-Bruijn
-- combinator terms (SKI + `var : ℕ → TmDB`, where var IS the de-Bruijn
-- rung-to-rung reference) — plus the codec:
--   * godel : TmDB → List ℕ    — constructor-tagged preorder serialize (the section)
--   * ungodel : List ℕ → TmDB  — the fuel-bounded well-founded parser (the retraction)
-- The SKI backbone mirrors AgdaExtrude.Tm; `var` (the de-Bruijn index) is the only
-- addition (there was no existing de-Bruijn/var type in the tree). That a TYPE is
-- syntax and syntax is Gödel-numberable is what dissolves the earlier "un-codeable
-- carrier" wall — PROVEN in TmDBGodel.Properties (godel-retract, TmDB-Canonical).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.UniversalProperty.TmDBGodel where

open import Substrate.Foundation.Nat using (ℕ; zero; suc; _+_)
open import Substrate.Foundation.List using (List; []; _∷_; _++_)
open import Substrate.Foundation.List.Length using (length)
open import Substrate.Foundation.Product using (_×_; _,_; proj₁; proj₂)

------------------------------------------------------------------------
-- 1. The de-Bruijn combinator terms: SKI + var (var IS the de-Bruijn ref).
------------------------------------------------------------------------

data TmDB : Set where
  var   : ℕ → TmDB
  S K I : TmDB
  app   : TmDB → TmDB → TmDB

size : TmDB → ℕ
size (var _)   = suc zero
size S         = suc zero
size K         = suc zero
size I         = suc zero
size (app f x) = suc (size f + size x)

------------------------------------------------------------------------
-- 2. godel: constructor-tagged preorder serialization to List ℕ (the section).
------------------------------------------------------------------------

godel : TmDB → List ℕ
godel (var k)   = 0 ∷ k ∷ []
godel S         = 1 ∷ []
godel K         = 2 ∷ []
godel I         = 3 ∷ []
godel (app f x) = 4 ∷ (godel f ++ godel x)

------------------------------------------------------------------------
-- 3. The parser (well-founded via an explicit fuel; no nested `with`, so it
--    reduces cleanly under `rewrite` in the .Properties proofs). Malformed
--    input / out of fuel → I.
------------------------------------------------------------------------

parse-fuel : ℕ → List ℕ → TmDB × List ℕ
parse-fuel zero    ts           = I , ts
parse-fuel (suc f) []           = I , []
parse-fuel (suc f) (0 ∷ k ∷ ts) = var k , ts
parse-fuel (suc f) (0 ∷ [])     = I , []
parse-fuel (suc f) (1 ∷ ts)     = S , ts
parse-fuel (suc f) (2 ∷ ts)     = K , ts
parse-fuel (suc f) (3 ∷ ts)     = I , ts
parse-fuel (suc f) (4 ∷ ts)     =
  let r1 = parse-fuel f ts
      r2 = parse-fuel f (proj₂ r1)
  in app (proj₁ r1) (proj₁ r2) , proj₂ r2
parse-fuel (suc f) (t ∷ ts)     = I , ts

------------------------------------------------------------------------
-- 4. ungodel (the retraction F): decode with fuel = the token count.
------------------------------------------------------------------------

ungodel : List ℕ → TmDB
ungodel ts = proj₁ (parse-fuel (length ts) ts)
