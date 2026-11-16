# Automating the pushout of reach + the recursive-typeholer path (design, 2026-07-10)

Prompted by: "combine numpy enumeration with the typeholer to automate the pushout of our
reach; draw a PATH over recursive application of the typeholer to orchestrate a decomposition
and refactor." Grounded in what the tools ALREADY do (--json = "LLM accelerator"; interner
reads .py AND .agdai mixably; --extract/--recursive climb one rung).

## The common structure (both asks are ONE mechanism)
The interner's SHARED CANONICAL NODE *is* the pushout; RECURSIVE interning *is* the abstraction
path. A single closure on the interned forest, pushed in two directions:
  · HORIZONTAL (numpy): extend the corpus with new computational REACH (a finite-verified law).
  · VERTICAL (recursion): re-intern the lifts to climb to the next ABSTRACTION rung.
Iterate {intern mixed corpus → read shared nodes → lift/name/prove → add lift to corpus} to
fixpoint (no new sharing). numpy feeds reach; recursion climbs; the LLM is the lift-synthesizer.

## Ⓐ auto-pushout  (numpy ⊗ typeholer)  — the horizontal push
- numpy DISCOVERS/VERIFIES a law on finite data (this session: the ⊗-over-◂ recursion, verified
  m,n≤4; earlier: the 225 Laplaza commutations). Ground truth at the frontier.
- The typeholer finds the STRUCTURAL skeleton across proven Agda cores (--shape: shared-shell +
  carrier-holes).
- PUSHOUT = law ∧ skeleton: the generic whose SHAPE = the typeholer skeleton and whose
  COMPUTATIONAL CONTENT = the numpy law. Mechanically: the shared node when numpy-law-as-term and
  the cores are interned together; the carrier-holes are the two legs (⊕-instance, ⊗-instance).
- BRIDGE (the minimal missing glue): a `numpy-law → interner-unit` serializer. numpy already IS
  Python; wrap the verified rule as a def IN THE AGDA COMBINATOR VOCABULARY (combine=div/mod,
  insert_at, oplus/otimes) so its AST interns in the same node-space as the .agdai cores. Then
  `jea_pysim --shape cores… law.py` consolidates law with cores → the pushout node.
  CAVEAT (honest): cross-language sharing lives at the abstract-combinator level, not raw ASTs;
  the serializer must speak the shared vocabulary. Not free, but small + one-time.

## Ⓑ typeholer-path  (recursive extract) — the vertical climb
- Each --extract pass emits parametric-helper candidates (shared subtrees). PROTOTYPE (this
  session, over 24 Orientation cores): PASS 1 surfaced combine/remQuot (fanin 8-10, the ⊗
  structure), lookup (the readout ρ), tabulate (the ⊗ def), +/*/Fin (grading+carrier) — exactly
  the raw material of the invariants I lifted BY HAND (GradedProductOver/HomOver/Braid/…).
- Re-intern the extracts, run --extract again → shared structure AMONG the helpers = the next
  rung. The PATH = extract→lift→re-intern to fixpoint: a DAG, nodes = generics, edges =
  instantiation obligations (carrier-hole fillings).
- THIS PATH IS THE REFACTOR PLAN. Walked by hand this session:
    concrete lemmas → GradedProductOver → {GradedHomOver, GradedBraid, GradedBifunctor,
    GradedBraidNatural} → GradedSymMonoidal.   Each rung a module; each edge an Agda instance.
- Missing automation: the DRIVER (run to fixpoint, record rungs+obligations) + the NAMING/PROOF
  step (LLM). The tool surfaces the rungs' material; naming a shared-subtree into a named record
  + writing the instance proofs is the synthesis the LLM does (not yet auto).

## Honest scope (what's auto vs LLM)
AUTO (exists): numpy verify; typeholer --shape/--extract/--recursive/--json; the shared-node =
pushout; the rung-material surfacing. LLM (in the loop): name a shared-subtree into a record,
write the generic + instance proofs, decide the fixpoint. The pipeline = a DRIVER wiring the two
oracles + the LLM synthesizer + re-intern. It does NOT auto-emit proven Agda; it auto-surfaces
the WHAT (pushout object + obligations) and hands the LLM a filled template per rung.

## Labels
- ⟡auto-pushout: build the numpy-law→interner-unit serializer (shared combinator vocab) +
  demo: feed the ⊗-over-◂ law + Perm cores to --shape, read the pushout node.
- ⟡typeholer-path: build the recursive-extract DRIVER (extract→re-intern→extract to fixpoint,
  emit rung-DAG + per-rung obligations) — the auto-decomposition/refactor plan.
- ⟡rig-UP-wreath: NOW TRACTABLE (was wrongly "deep"). numpy gave the constructive input — the
  ◂-recursion for ⊗: (insert_at p σ)⊗τ = [row<p: keep σ⊗τ | row=p: m·n+τ | row>p: shift-down].
  Build RigAlgebra C = LehmerAlgebra + (one,times) + this recursion; ONE fold respects ⊕ AND ⊗
  by the SAME ◂-induction (the common witness = the tower rung acting synchronously on both).

---
## EMPIRICAL RESULTS (2026-07-10, both prototypes built + tested)

### Ⓑ typeholer-path — BUILT (jea/metalanguage/typeholer_path.py), verdict: works, naming is the gap
Drives the Corpus object directly (--json lacks the extract/containment data). Over 23 Orientation
cores: builds a containment tower (rungs 0-4) + fixpoint iterate. RECOVERS the rung MATERIAL for every
named layer — combine/remQuot (GradedProductOver), lookup/tabulate/⊕map/⊗map (HomOver/Bifunctor),
subst/sym (Braid/BraidNatural) — ordered primitives→composites, with per-node instantiation
obligations. GAPS (honest): (a) NAMING — surfaces raw subtrees not records (the LLM step); the named
records aren't shared SUBTREES (they're the defs being built). (b) the 4 mid-band records sit at ONE
module-level but containment-height spreads their combinators across rungs 0-3. (c) fixpoint converges
in 1 level (SPPF is bottom-up-complete — re-interning finds no new shapes). So: auto structural
skeleton + obligations; LLM names + proves.

### Ⓐ auto-pushout — BUILT (jea/metalanguage/numpy_law_bridge.py), verdict: mechanism real, MY DESIGN
###   UNDER-ESTIMATED THE GLUE (correction to the "small + one-time serializer" claim above)
Naive .py emit → ZERO cross-language sharing (Python node.kind ≠ AgdaCore, confirmed). WITH a vocab-map
(NAME_MAP + emit AgdaCore-kind nodes): vocabulary SOLVED (100% head-match), BUT the pushout only
PARTIALLY materializes — three isolated obstructions: (1) hash-cons fires only on LEAF variable nodes;
combinator nodes get fresh ids (need the law instantiated at the cores' own leaf terms, not fresh vars);
(2) --shape aligns ROOT-to-ROOT, law's _≡_ root ≠ cores' Defn/Clause root → must enter subtree-to-
subtree; (3) ARITY — elaborated Agda lookup carries implicit-arg children (levels/sizes) the hand term
omits → PARTIAL 50% one level down. CORRECTION: my "small + one-time (just a vocab-map)" OVERSTATED it.
The real bridge needs vocab-map + arity-faithful emit (mirror the elaborated implicits) + subtree-entry
alignment. The "shared-node = pushout" mechanism is real but NOT delivered by a naive serializer.
