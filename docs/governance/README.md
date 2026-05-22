# Substrate governance

Policy documents that govern how the substrate codebase is grown, named,
and reviewed. Each policy was promoted here from the assistant's
project memory (`memory/discipline/`) once it became load-bearing — i.e.
once it was cited frequently enough in code comments that contributors
benefit from reading the policy directly.

These policies are **non-binding for prose** but are **structurally
enforced where possible** — most have Agda-level realisations that
make the policy a definitional commitment (records, universal
properties, cover combinators) rather than a documentation request.

## Index

| Policy | Concern | Agda enforcement |
| --- | --- | --- |
| [naming.md](naming.md) | Prefer established categorical names over substrate-local invention | Direct (universal properties are first-class Agda) |
| [agda_comment_hygiene.md](agda_comment_hygiene.md) | Don't overclaim in comments relative to what proofs establish | Cultural (Agda can't check prose) |
| [generator_over_orbit.md](generator_over_orbit.md) | When N-case enumeration grows, expose the generator | Direct (cover combinators + n-refls) |
| [cover_pattern.md](cover_pattern.md) | Three-layer composable Cayley-table cover pattern | Direct (Pow, copies, n-refls in Coxeter.CanonicalCover) |
| [universal_property_discipline.md](universal_property_discipline.md) | Reach for UP bridges before per-instance unfolding | Direct (linear-extensionality, FreeLinearization, etc.) |
| [project_culture_coalgebraic.md](project_culture_coalgebraic.md) | Defer work by slice-scope discipline, not consumer demand | Cultural (about work planning) |
| [file_size_one_pass_rewrite.md](file_size_one_pass_rewrite.md) | Files small enough to rewrite in one pass; decompose past 400-line warning zone | Cultural (judgement-based threshold) |
| [shadow_architecture/](shadow_architecture/README.md) | Four-discipline lattice for cross-session work: decompose / regroup / snap + meta | Direct (formalised at `Substrate.ShadowArchitecture/*`) |

## Status

These policies are mirrored back into the assistant's
`memory/discipline/` directory as short pointers so future sessions
that load memory see "policy lives at `docs/governance/X.md`" rather
than a full copy. Single source of truth: this directory.

## What's not here yet

Some structural disciplines remain memory-only because they involve
infrastructure not yet built:

- `homology-cohomology-recursion` — the substrate's deepest principle
  (observed = homology, cataloged = cohomology, recursive). Formalising
  this needs a meta-level encoding (theorem-as-object universe). Will
  land as `Substrate.Discipline.HomologyCohomologyRecursion.agda` when
  the relevant arc closes.

Others are encoded directly in Agda module headers rather than as
governance docs:

- 3+1 parity as cone instance → `Substrate.Category.Cone` +
  `Substrate.Algebra.F2.Cone-V4-3plus1`.
- Multi-route equivariance recovery → `Substrate.Category.MultiRouteEquivariance`.
- Prime-factored gauge arc → `Substrate.Algebra.PrimeFactoredGauge`.
- Grothendieck coherence rule → superseded by
  `Substrate.Category.UniversalProperty/*` (the UP-topos).
