------------------------------------------------------------------------
-- Substrate.Algebra.PontryaginDual.Sites.Manifest
--
-- Aggregates all concrete PontryaginDual sites. Currently wired:
--   Zn         — Z/(suc n) as self-dual carrier (the dual OPERATIONS).
--   ZnLaws     — those operations proved an AbelianGroup (M1–M5 ladder).
--   ZnDuality  — the LCA instance + the duality theorem at that site.
--   ZnCharacter— the character family χ_k + the homomorphism law.
--
-- ⚑ THIS IS AN AGGREGATOR OF IMPORTS, NOT A RE-EXPORT.  The `import`s below
-- bind nothing into this module's scope (no `open`, no `public`), so a
-- consumer cannot reach ZnLaws' names through here — it must import the leaf.
-- The manifest exists to make the site set BUILDABLE as one target, which is
-- why adding a site means adding a line here.
------------------------------------------------------------------------

{-# OPTIONS --safe --without-K #-}

module Substrate.Algebra.PontryaginDual.Sites.Manifest where

import Substrate.Algebra.PontryaginDual.Sites.Zn
import Substrate.Algebra.PontryaginDual.Sites.ZnLaws
import Substrate.Algebra.PontryaginDual.Sites.ZnDuality
import Substrate.Algebra.PontryaginDual.Sites.ZnCharacter
