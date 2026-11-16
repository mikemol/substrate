---
name: project-varc-closure
description: "V-arc full closure status — Cocycle framework / Coxeter framework / V4 chain / Hedberg / Σ-≡ all substrate-native; only GCD remains as stdlib offender (deferred per parallel agent's \"Coprime parametric\" verdict)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 20608575-0873-42b7-b664-8addeb8207d9
---

The V-arc (Phase-2 stdlib-elimination beyond the basic Foundation
modules) executed across multiple sessions and has reached effective
closure:

- **Cocycle framework** (`Substrate.Cocycle`, `Substrate.Algebra.{GroupAction,Torsor,IsomorphicCocycle,SemidirectProduct}`):
  monomorphic at Set, uniformly SetoidGroup-parametric, no stdlib.
- **Coxeter framework** (`Substrate.Groups.Coxeter.{GroupAdapter,SemidirectProductGroup}`):
  parametric over `Substrate.Algebra.SetoidGroup`. Stdlib eliminated.
- **V4 chain** (V4/{Axioms,Bundle}, S3, S4, S4-Composed, SFin):
  stdlib `Algebra.*` + `Relation.Binary.*` eliminated. V₄-Group is
  now `Substrate.Algebra.Group V₄` (substrate-native). S₄-Group is
  `SetoidGroup` (substrate-native).
- **S4-Iso chain** (Embedding, Foundation, ForwardHom, IsoTransport,
  Extract, ExtractCorrect, Roundtrip, V4Normal, etc.):
  `Algebra.Properties.Group.inverseˡ-unique` replaced by
  `Substrate.Algebra.SetoidGroup.Properties.Props.inverseˡ-unique`.
  `proj₁ S₃.inv-inverse` / `proj₂ S₃.inv-inverse` references migrated
  to the substrate-native `S₃.inv-left` / `S₃.inv-right` pair-form.
- **V4Signature/S4GroupIso**: stdlib `IsMagma`/`IsSemigroup`/`IsMonoid`/`IsGroup`
  bundle + `Algebra.Morphism.Structures.IsGroupHomomorphism` /
  `IsGroupIsomorphism` removed. The substrate-native
  `TotalSpace-Group : Substrate.Algebra.Group TotalSpace` replaces
  the stdlib bundle; homomorphism / injectivity / surjectivity
  witnesses kept as standalone functions for future
  GroupHomomorphism-record consumption.
- **ReservedToBivectorAffine**: stdlib
  `Axiom.UniquenessOfIdentityProofs.Decidable⇒UIP` →
  `Substrate.Foundation.Hedberg.Decidable⇒UIP`.
  `Data.Product.Properties.Σ-≡,≡→≡` →
  `Substrate.Foundation.Product.Σ-≡,≡→≡`.
- **Discipline.agda**: ICS / WCS / Section / RigidifiedWCS monomorphic;
  `Group.Carrier Gauge` → `SetoidGroup.Carrier Gauge` via explicit
  module qualification.

**Why:** The substrate's stdlib-elimination discipline (per
[[user-no-stdlib-we-can-grow-ourselves]]) requires bridges, not
imports. The V-arc closed the largest residual chains. Cocycle
abstraction is now self-contained.

**How to apply:** When migrating new code that touches V₄ / S₃ / S₄ /
F₂³ / Coxeter / Cocycle, use the V-arc Substrate.Algebra.SetoidGroup-
parametric infrastructure. Coerce propositional Groups via
`Substrate.Algebra.Group.ToSetoid.to-setoid` at consumer sites.

**Remaining residue:** `Substrate.Algebra.Nat.GCD.agda` still imports
`Data.Nat.{Divisibility,DivMod,Induction}` + `Induction.WellFounded`.
A parallel agent's investigation flagged the right resolution as
making `Coprime` parametric in `gcd-ℕ` (rather than rewriting EEA
substrate-natively). Queued for a follow-up arc.

**Capstone re-export:** [[Substrate.Algebra.V-Arc.Capstone]].
