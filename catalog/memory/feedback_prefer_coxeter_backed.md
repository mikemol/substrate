---
name: prefer-coxeter-backed
description: "Coxeter-backed (word-algebra) group constructions are FAVORED over non-Coxeter-backed alternatives — even when a non-Coxeter alternative already exists. Word algebras (Coxeter.Word / Canonical / insert / normalize) are substantively cheaper in memory allocation, leading to faster and more scalable group infrastructure."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 28a7490c-cf4a-4933-8773-215362d96f13
---

**Rule.** When building or extending group infrastructure in the substrate, **prefer Coxeter-backed (word-algebra) constructions** over alternatives like Permutation-on-Fin, matrix enumeration, set-theoretic carriers, etc. — even when a non-Coxeter alternative already exists for the same group.

**Why:** Word-algebra derivations (Canonical / insert / normalize over an abstract Coxeter.Core) are substantively cheaper in memory allocation than the alternatives. Coxeter representations:

* Encode group elements as bounded-length normal-form words, not as data-rich objects (matrices, function-tables).
* Inherit the entire abstract surface (group ops, equivalences, bridge lemmas, clash macro, composition helpers) from the abstract Core via parametrics — minimal per-instance work.
* Scale well in compilation/typechecking time because normalization is purely syntactic on small finite carriers.

**How to apply:** When the next slice asks for a group G:

1. If G is a Coxeter group or has a known finite presentation, build it Coxeter-style via `Substrate.Groups.Coxeter.{Word, Core, ListPresentation}` mirroring the Z3/Z4/Z5/Z7 pattern.
2. If a non-Coxeter version of G already exists (e.g., Permutation-on-Axis S_4), DO NOT treat it as a reason to skip the Coxeter version. The Coxeter version is preferred for downstream performance.
3. If G is not naturally Coxeter (e.g., GL(3, F₂) is not a Coxeter group, though it has Sylow-2 ≅ S₄ which is A₃-type Coxeter), build it via generators-and-relations using word algebra over a small generating set — leverage the substrate's existing Word + Canonical + normalize infrastructure rather than reaching for matrix carriers.
4. Permutation-on-Fin / matrix carriers are acceptable when truly necessary (e.g., for displaying concrete actions on small sets, or when the group has no compact presentation), but should not be the default.

**The previous mistake.** I had argued (in the multi-route equivariance arc) that Coxeter-backed S_4 was "redundant" because a Permutation-Axis S_4 already existed. That reasoning was wrong: the Coxeter-backed version would still be preferred for performance even when a non-Coxeter version exists.

**Cross-references:**

* [[v4-typeclass-architecture]] — the architectural pattern that this feedback extends: V_4 and other finitely-presented small groups go through the Coxeter framework.
* [[roll-our-own-via-word-algebra]] — the related rule that "stdlib too heavy" doesn't mean "blocked" — the substrate's Coxeter Word handles most fancy-stdlib cases natively.
* [[composable-primitives-over-flat-enumeration]] — Coxeter-backed constructions exemplify the composable-primitives discipline.
* [[minimize-stdlib-deps]] — Coxeter-backed avoids deep stdlib pulls (Data.Fin.Permutation, etc.).
