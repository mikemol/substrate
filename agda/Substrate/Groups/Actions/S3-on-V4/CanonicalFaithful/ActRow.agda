{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.ActRow where

-- A row's action on V₄ — relational (both words), one definition.

open import Substrate.Groups.V4.Bijection using (V₄)
open import Substrate.Groups.Actions.S3-on-V4.Dispatch.ActOnCanonical using (act-on-canonical)
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.Row
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.NOf using (n-of)
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.HOf using (h-of)

act-row : Row → V₄ → V₄
act-row ρ v = act-on-canonical (n-of ρ) (h-of ρ) v
