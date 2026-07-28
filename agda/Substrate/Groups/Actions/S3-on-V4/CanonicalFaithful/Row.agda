{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.Row where

-- The six canonical rows as a finite index.

data Row : Set where
  id r r² s sr sr² : Row
