---
name: project_realizability_charter_arc
description: "Realizability Charter — Agda backbone fully proved (§4 + cube-parametrized §5 reflections), zero postulates/holes, green; paper prose; not in All.agda"
metadata: 
  node_type: memory
  type: project
  originSessionId: b0f173b0-7c01-42e2-bd3c-cbed23f2d66a
---

Backbone for the paper "Grounding the Realizability Charter" (a governance
ontology: an LLM may *certify a distinction* only if constructible →
reachable → observable → coverable, each with a replayable witness).

**Agda:** `agda/Substrate/Realizability/Charter.agda` — verified green
under `--safe --without-K`, **zero postulates, zero open holes** (Agda
2.8.0). One common substructure (see
[[feedback_common_substructure_recursively]]): a typed cons-list `Chain`
of flag-gates (same shape as term-algebra `UPTerm`), `⟦_⟧?` (Bool test) /
`Wit` (inductive realizer family) bridged by `sound`. §4 generic in the
carrier `D`: Lemma 4.1 `drop`, 4.2 `_++ᵖ_` pipeline + category laws, 4.3
`Replay`, Theorem 4.4 `sound`/`intersection`/`reject`.

**§5 is now cube-parametrized + variance-corrected** (was: refutable
interior/right-adjoint `Conj-` holes). Carrier `Cube n = Fin n → Bool`,
generic in arity `n`; `Distinction = Cube 4` with coordinate projections
recipe/manifest/measure/bounded. A gate is a coordinate MASK; passes `d`
iff `mask ⊑ d` (pointwise). The reflection is the CLOSURE (left adjoint,
not interior/right) `rmask mask d = d ∨ mask` ("declare missing
resources"). `mkReflection` discharges `GateReflection` (ext/mono/idem +
`closed ⟺ passes` BOTH ways) generically for any mask, needing only two
∨-lemmas (no `Fin` decidable-equality). All four gates closed:
`refl-{con,rea,obs,cov}`; `·⇒mask`/`mask⇒·` prove `mask ⊑ d ⟺ gate? d`.
The old refuted `Conj-closed⇒observable` is now the *proved*
`obs-closed⇒passes`. Only residue: a noted ASYMMETRY (coverable has a
left adjoint, not a right one — passer-set is {⊤}); stated in prose, NOT
proved as universal non-existence (no negation-overclaim).

Key lesson: the original §5 conjecture had the **adjoint variance
inverted** — gates are necessary conditions ⇒ up-sets ⇒ want
closure/reflection ("smallest passing super-distinction" = remediation),
not interior/coreflection ("largest passing sub"). Parametrizing helped
§5 (not §4, which is already carrier-generic) — to the Boolean cube,
which supplies the join/closure structure.

**Paper prose:** `scratch/realizability_charter_proofs.md` (cites module
by name).

**Status / next:** module NOT in `Substrate.All` yet (wire in after
review). Skeleton's §1–§3, §6–§9 prose + citation ledger still to write.

**Tooling note:** Bash/Read harness was badly lag-prone across these
sessions (outputs dropped, flushed in bulk); first-ever `agda` typecheck
recompiles all Foundation (minutes). Budget for it.
