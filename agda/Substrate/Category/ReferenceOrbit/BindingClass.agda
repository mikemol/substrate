------------------------------------------------------------------------
-- Substrate.Category.ReferenceOrbit.BindingClass
--
-- The third (chirality) axis: binding-class distinction between
-- substrate-aligned references (ChamberBound) and structure-agnostic
-- references (ChamberFree).
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Category.ReferenceOrbit.BindingClass where

data BindingClass : Set where
  ChamberBound   : BindingClass
  ChamberFree    : BindingClass
