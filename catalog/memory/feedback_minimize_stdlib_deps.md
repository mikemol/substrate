---
name: feedback-minimize-stdlib-deps
description: "Stdlib dependencies are unwanted; the user does not normally have stdlib installed. Even basic Data.Fin / Data.Nat / PropositionalEquality should migrate to substrate-native when feasible."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Stdlib dependencies are unwanted, not merely minimised.** The user does
not normally have agda-stdlib installed; any stdlib import is a friction
point for them. Strengthened twice now:
- (2026-05-20) "Build it in the substrate" if missing — was previously "minimize heavy subsystems."
- (2026-05-21) "I don't want stdlib dependencies. I normally don't even have stdlib installed." Even basic Data.X imports should migrate to substrate-native when an in-tree alternative is feasible.

**Why:** Each stdlib import drags in its own ecosystem AND requires the
user to have stdlib installed at all. The substrate is intended to
stand on its own universal-property machinery; pulling stdlib means the
substrate is not actually self-contained. Coalgebraic discipline (per
[[feedback-coalgebraic-not-consumer-driven]]): unfold gauge structure
in-tree rather than borrow it from a fixed library.

**How to apply:**
1. **No new stdlib imports.** If a slice would add one, instead extend a
   `Substrate.X` module to cover the needed primitive.
2. **Migrate existing stdlib uses opportunistically.** When touching a
   file that imports stdlib, consider whether the import can be replaced
   with a substrate-local definition. Substrate already covers:
   - `Substrate.Algebra.{Magma, Semigroup, Monoid, Group, ...}` for the
     stdlib `Algebra.Bundles` / `Algebra.Structures` hierarchy
   - `Substrate.Algebra.Z` for `Data.Integer`
   - `Substrate.Algebra.Bijection` for `Function.Bundles._↔_`
   - `Substrate.Groups.Coxeter.Word` for `Data.List` style cons-lists
3. **When stdlib must stay (transitionally),** mark it as a *single*
   gating bridge — never let stdlib types leak through internal
   module boundaries. Example: `Data.Fin.Properties.*↔×` is the only
   piece blocking `Cardinality/Product` from full migration; the path
   forward is a substrate-native combine/divide proof, not adopting
   stdlib's `Inverse` shape downstream.
4. **Don't revert substrate migrations to "match" stdlib downstream.**
   If a substrate-side migration breaks a downstream file because that
   file still uses stdlib, the fix is to ALSO migrate the downstream
   file (or write the bridge cleanly), not to roll the substrate side
   back to stdlib. Per (2026-05-21): I reverted Cardinality.agda to
   restore Cardinality/Product.agda; user corrected: the right move
   was to bridge Product through a substrate adapter.

Pairs with [[feedback-roll-our-own-via-word-algebra]] ("stdlib too
heavy" ≠ "blocked"; the Coxeter Word algebra handles most fancy-stdlib
cases natively).
