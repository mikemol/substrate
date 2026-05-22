# Shadow architecture: four substrate disciplines

This subdirectory holds the **shadow-architecture trio + meta-frame** —
the substrate's project-culture disciplines for substantive work that
spans session boundaries.

## Why these are governance

Contributors to the substrate — human or LLM — face a recurring failure
mode: **monolithic attack on a large task, context exhausted mid-way,
half-solutions produced with no reusable intermediate value.** The
shadow-architecture disciplines exist to convert what would otherwise
be a fragmented session into one that produces *named, reusable
substructure* — shadows — that survive context loss and accumulate
across sessions.

The four disciplines are formally **S₃-symmetric** (any permutation of
the three component disciplines preserves the lattice structure) but
**operationally asymmetric** in practice. Each has its own firing
conditions, its own intervention protocol, and its own complementary
behaviour with the others.

## The disciplines

| File | Move | When to use |
| --- | --- | --- |
| [decompose_by_entailment.md](decompose_by_entailment.md) | Forward: intact goal → shadows | Starting a substantive task; mid-task thrash recovery |
| [regroup_from_shadows.md](regroup_from_shadows.md) | Sideways: existing artefact → shadows + recomposition | Refactoring working code; extracting common patterns |
| [snap_to_grid.md](snap_to_grid.md) | Backward: accumulated shadows → goal | Cross-session continuation; lost-context recovery |
| [shadow_architecture.md](shadow_architecture.md) | Meta: 3-skill lattice + orchestration | Classifying which region the current work occupies; detecting mid-session region transitions |

## Agda formalisation

The shadow-architecture meta-frame is formalised in Agda at
[`agda/Substrate/ShadowArchitecture.agda`](../../../agda/Substrate/ShadowArchitecture.agda)
+ submodules. The Fano-plane labelling (`FanoLabeling`,
`Duality`, `Weight`, `SelfReference`, `AxisDualLine`, `Mode`) maps
the three disciplines + a guard region onto the 7 lines of the Fano
plane, with the 8-region 3-skill lattice covered by the `Mode`
submodule's coverage theorem.

This means the discipline is not just a project-culture statement — it
is a **load-bearing structural primitive** with mechanical formal
content. Contributors writing substrate code or proofs can rely on
the meta-frame being checked, not just suggested.

## Where these live in different contexts

| Audience | Source |
| --- | --- |
| Human contributors / project culture | This directory (`docs/governance/shadow_architecture/`) |
| LLM assistant skill firing | [`skills/<name>/SKILL.md`](../../../../.claude/skills) (user-settings) — frontmatter triggers firing |
| Formal Agda content | [`agda/Substrate/ShadowArchitecture/`](../../../agda/Substrate/ShadowArchitecture/) |

Single source of truth for the *content*: this directory. The skill
files in user-settings exist because Claude Code needs the YAML
frontmatter to know when to fire each skill; the body content is
equivalent to (and could be regenerated from) the docs here.

## Reading order for new contributors

If you have not encountered shadow-architecture before, read in this order:

1. **[shadow_architecture.md](shadow_architecture.md)** — the meta-frame,
   sets up the lattice and explains why the trio exists.
2. **[decompose_by_entailment.md](decompose_by_entailment.md)** — the
   forward discipline; it's the one you'll use most often.
3. **[snap_to_grid.md](snap_to_grid.md)** — the backward discipline;
   essential for cross-session continuation.
4. **[regroup_from_shadows.md](regroup_from_shadows.md)** — the sideways
   discipline; the refactoring move.

## Cross-references

* The trio is referenced collectively as `[[shadow-architecture]]` in
  Agda code comments.
* Individual disciplines are referenced as `[[decompose-by-entailment]]`,
  `[[snap-to-grid]]`, `[[regroup-from-shadows]]`.
* Related governance: see `../generator_over_orbit.md` (the trio's
  output — shadows — IS the substrate's named-generator artefact),
  `../universal_property_discipline.md` (shadows often turn out to be
  universal-property witnesses), `../cover_pattern.md` (the Cayley-table
  cover combinators are themselves substrate-wide shadows).
