---
name: feedback_search_for_the_parametric_form
description: "Before grinding new machinery, find what's already built as a PARAMETRIC form over what — this repo builds once, parameterized, and the grind's shape usually exists waiting for instantiation."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a96a1d8c-75ae-47e6-807c-c4988d800d8f
---

User (2026-06-24): *"take a look at what has been built as a parameterized form over what; there are lots of generic things which only require parameterized instantiation. Chances are, that grind's resulting shape likely already exists in the repository somewhere waiting to be parameterized. Because that's how this repo is architected."*

The substrate's defining architecture: **build once, parametric over the index/data; each concrete case is a thin instantiation** (`Coxeter-Fin-Generic` over Zₙ; `Cyclic.{cyclic-suc, cyclic-Linear, cyclic-HasOrder}` over n; `Cycleₖ = cyclic-suc {k-1}`; the `Over` semiring bundle; `basis-permutation-Linear` over any Fin-perm). The `[[expose-generator-not-orbit]]` discipline is the same idea: the per-instance boilerplate is an ORBIT of one generic; expose the generator.

Caught live (Ⓕ.spectral (a)): I was about to GRIND a cyclic shift `σ_p : Linear p p` + `σ_p^p = id` + the rotation/mod/order machinery from scratch (and had started declaring it "gated on missing Foundation Vec-transport"). ALL of it already existed parametric over n in `FromImages.Permutation.Cyclic` — `σ_p = cyclic-Linear`, `σ_p^p=id = cyclic-HasOrder`, `cyclic-suc = (i+1) mod p` — waiting for one-line instantiation. The "grind's resulting shape" was sitting in the repo. (Third time the answer was "instantiate an existing parametric form," after the wedge/CrossMul and the Cyclotomic.Over reuses.)

**Why:** grinding from scratch in a build-once-parameterized repo is the [[feedback_read_structure_dont_rebuild]] reflex one level up — rebuilding the PARAMETRIC form, not just a lemma. It also tends to manufacture false "walls" (I claimed a Foundation gap that the parametric `Cyclic` module had already crossed via `mod-suc`).

**How to apply:** when a plan needs structure X at a concrete parameter (a cycle of order p, an n-dim space, a degree-d poly), FIRST ask *what is X the parametric-over-? form of, and is that generic already built?* Search the generic layers (`*-Generic`, `Cyclic`, `Over`-bundles, `*.FromImages.*`, the `Coalgebra`/`Category` parametric records, `Substrate.Generators`/`*.Registry`) for the parametric form and INSTANTIATE it. Only build new if the parametric form genuinely is absent — and then build it PARAMETRIC (the next caller instantiates). This is the CLAUDE.md reuse-search trigger sharpened to "find the parametric form, not just a lemma." Sibling: [[feedback_declaring_a_wall_is_the_rebuild_reflex]] (the grind I almost walled on was already built).
