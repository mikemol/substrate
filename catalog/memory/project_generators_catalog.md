---
name: project-generators-catalog
description: "Substrate.Generators (agda/Substrate/Generators.agda) — substrate-native index module re-exporting every generator-shaped definition: cover combinators, payload-shape primitives (Pow/dep-Pow/n-refls), Coxeter Gens, S₃-on-V₄ actions, GL(3,F₂) Sylow generators, Hodge ★, free constructions, limits, adjunctions, UPArrow / fixed-point / Monad / Comonad / Kan."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

`agda/Substrate/Generators.agda` — single substrate-native module
that re-exports `public` every "generator-shaped" definition in the
Agda surface. Twelve sections by generator-kind.

**Section index** (see file's INDEX SUMMARY comment block for the full
exported-names list):
1. Cover/dispatch combinators (fin-cover family, v4-cover family,
   axis-cover family, canonical-cover-Z{2,3,4}).
2. Payload-shape primitives (Pow, copies, n-refls and powers).
3. Coxeter Gens — namespaced as `Z₂C`, `Z₃C`, `Z₄C`, `Z₅C`, `Z₇C`,
   `V₄C`, `FCyclic`.
4. S₃-on-V₄ actions (rotate, swap-αβ, rot-pow, swap-pow).
5. GL(3,F₂) generators — Sylow-2 (σ₂, swap01-Linear), Sylow-3 (σ₃,
   cycle3-Linear), Sylow-7 (singer, singer-Linear).
6. Hodge / Fano duality (hodge-star, normal-vector, dual-line).
7. Universal arrows (FreeOverBasis, FreeLinearization, free-linearize,
   linear-from-images, linear-extensionality, FreeBasisUniversal,
   FreeModuleExtensionality).
8. Limits (Equalizer-Of, equalizer-factor, Pullback-Of, Limit, Colimit).
9. Adjunctions (IsLinearAdjunction, linear-adjunction,
   GaloisAdjunction).
10. Higher-categorical (UPArrow, UPMorphism, ι, to-trivial-cond).
11. Operadic (intentionally catalogued-but-not-exported; see below).
12. Monad / Comonad / LeftKanExtension / RightKanExtension.

**Why:** the substrate's "expose generator not orbit" discipline (per
[[feedback-expose-generator-not-orbit]] and
[[feedback-expose-generator-not-orbit-applies]]) treats generators as
first-class objects. Until now there was no single place to enumerate
them; downstream callers had to guess module paths and names. This
module is the index.

**How to apply:** when working on Agda code that needs to compose
generators across kinds (e.g., a cover combined with a Coxeter Gen
and a universal arrow), `open import Substrate.Generators` brings all
the names into scope under their per-family namespace aliases. Z/n
collisions are resolved by the `Z₂C` / `Z₃C` / ... module names.

**Typecheck status:** typechecks under `--safe --without-K`. Two
operadic primitives are skipped:
* `Substrate.Category.OpcodeAlgebra` — pre-existing sort mismatch on
  `execute : ... → Vec Opcode n → State` (Vec is Set-only, Opcode is
  Set ℓO). Fix requires either making `Substrate.Foundation.Vec`
  level-polymorphic or restricting `execute` to Set-level opcodes.
* `Substrate.Category.GeneratorOperad` — imports stdlib `Data.List`
  which conflicts with `Substrate.Foundation.Bool`'s BUILTIN BOOL.
  Violates [[feedback-minimize-stdlib-deps]]; should be rewritten
  against `Substrate.Groups.Coxeter.Word`-as-List.

Both are catalogued as kinds in the file's section comments but not
re-exported until those issues are resolved.
