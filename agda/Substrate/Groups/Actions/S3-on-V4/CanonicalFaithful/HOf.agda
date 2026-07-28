{-# OPTIONS --safe --without-K #-}

module Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.HOf where

-- The Z₂ word of a row. SINGLE carrier (index 1) — binding this at the
-- Z₃ index is exactly the merge that made the old combined module wrong.

import Substrate.Groups.Coxeter.Cyclic.Base 1 as Z₂-Base
open import Substrate.Groups.Coxeter.Word using (Word; []; _∷_)
open import Substrate.Groups.Actions.S3-on-V4.CanonicalFaithful.Row

h-of : Row → Word Z₂-Base.Gen
h-of id  = []
h-of r   = []
h-of r²  = []
h-of s   = Z₂-Base.a ∷ []
h-of sr  = Z₂-Base.a ∷ []
h-of sr² = Z₂-Base.a ∷ []
