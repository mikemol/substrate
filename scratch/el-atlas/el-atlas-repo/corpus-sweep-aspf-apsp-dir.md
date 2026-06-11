# Corpus sweep: ASPF, APSP, DIR (S-series intern)

Prompted by R1's erratum E3, which is hereby CORRECTED (see §3). Sweep run
2026-06-11 over (a) conversation history, (b) Google Drive. Scope of this
document: inventory, observed cores [O], identification candidates [C],
label-oscillation flags, frontier. NO spec import is made here — per the
v3.3 lesson, imports ride instrument extensions; everything below is held
at [C] unless marked.

## 1. Inventory

**Conversations** (titles; searchable):
- "Semantic strictness and operational bicategoricity in evaluator
  functors" — the gabion ASPF module tree read end-to-end
  (aspf_core/evidence/execution_fibration/lattice_algebra/morphisms/
  mutation_log/resume_state/stream/decision_surface/event_algebra_adapter/
  visitors); ASPF 0/1/2-cells; DataflowFiberBundle; naturality witnesses.
- "Context braiding playbook for slice auditing" — ASPF glossary entry §23:
  **ASPF = Algebraic Structural Prime Fingerprint**; "packed-forest label,
  not a hash"; carriers base/constructor/provenance/synth; normative rules
  (deterministic+reversible at base/constructor; provenance not erased by
  default; bitmask carriers are filters only, prime products authoritative).
- "Cofibrational analysis of five papers" — gabion_paper names ASPF as "a
  packed derivation label in a Shared Packed Parse Forest"; the Forest IS
  an Earley chart; GALAXY–ASPF isomorphism W_{v,k} <-> log_alpha(F(s)^k);
  CONSTELLATION–ASPF Bloom-filter isomorphism; Drift = Homotopy.
- "Lost formalisms recovery" — ASPF<->Yoneda (F(T) as homomorphic
  projection of the representable functor); DomainToAspfCofibration.
- "Reviewing old files and task framing" (2026-06-10, chart-archaeology) —
  APSP sub-corpus body-read: C017 (binary tree of geodesic segments,
  length 2^(order-1), epochal freeze-and-reuse), C048 (GALAXY =
  holographic dimensionality reduction of the APSP tree), C018
  (Mersenne-prime hop variant, computed), C063/M009/M010/M017 (DIR
  body-read; the coverage-grade correction).
- "Constraint propagation science and mathematics" — SPPF node ontology as
  the organizing spine of the CP monograph.

**Drive** (titles; IDs unfetched this pass):
- ASPF: gabion_paper; merged_ontology; "Gabion Design: Semantic Compression
  Engine"; "Formal System: The Fibration of Semantic Artifacts"; "ASPF
  Payload Alternation Ambiguity Example" (too large to fetch inline);
  "Parsing Video with Context-Free Grammars"; "Parsing Sound and Video
  with System" (too large).
- APSP: "DIR, APSP, OCAL Isomorphisms Explored" (synthesis doc, UNREAD);
  three FOLDERS: "DIR - Integration of APSP Concepts", "III. Algorithm
  Design (APSP)", "DIR - Research & Advanced Data Structures (APSP
  Review)"; exported conversations ("I point out again that APSP is a
  pathfinding system...", "Is the APSP work relevant here?").
- DIR: the White Paper in at least five iterations; "DIR book 1 ch 0",
  "DIR book 1 ch1"; "DIR introduction"; "OCAL" (contains an encyclopedic
  DIR overview).

## 2. Observed cores [O]

**ASPF** — Algebraic Structural Prime Fingerprint (gabion). Type/structure
identity encoded as prime products over orthogonal carriers (base,
constructor, provenance, synth); explicitly a *packed derivation label in
an SPPF*, not a hash; Forest nodes = Earley items; 2-cell witnesses
(AspfTwoCellWitness) prove derivation-path homotopy; drift = absence of a
2-cell; Yoneda-grounded (fingerprint = homomorphic projection of the
representable functor onto (N, x)); faithful prime-preserving cofibrations
embed domain vocabularies.

**APSP** — the corpus's hierarchical all-pairs-shortest-paths system.
Binary tree of geodesic segments, length 2^(order-1) (recursive midpoint
construction), built epochally with freeze-and-reuse and dedup "along the
grain of prior work"; GALAXY = holographic dimension-reduced projection of
the tree ("flattens the nodes into a kind of hologram"); Mersenne-prime
hop-length variant computed, not just proposed; HOM-APSP = homology
similarity assessment; LCA/descendant-set queries with Bloom-filter
membership (CONSTELLATION).

**DIR** — Declarative Intermediate Representation. "Declarative LLVM":
graph-structured common IR for declarative languages with
constraint-preserving optimization; the defining inversion is
constraint-as-negative-space — behavior is free except where constraints
forbid; white-papered with formal semantics, source-language mappings
(Haskell, SQL), WebAssembly target; Game-of-Life as the worked design
example (BSP/quadtree, Hashlife as related art). Specified and
white-papered; execution never witnessed (chart M010).

**OCAL** — Object/Constraint Abstraction Layer. Surfaced by this sweep;
the Drive synthesis doc claims DIR/APSP/OCAL are "isomorphic facets of a
singular theory of Unified Data Processing." UNREAD. [O for existence
only]

## 3. Correction to R1 erratum E3

E3 claimed ASPF/SPPF/"content-addressed memory"/"parse forest" appear
"NOWHERE in the corpus." That claim was true only of the EL-Atlas repo
documents and FALSE of the corpus at large: ASPF is a named, load-bearing,
white-papered framework of the author's (gabion), and the SPPF
identification is explicit in the author's own paper. The reviewer's
acronym *expansion* ("Abstract ... Parse Forest") was wrong — corpus says
Algebraic Structural Prime Fingerprint — but the *connection* was not
imported vocabulary; it was (by knowledge or convergence) the author's
own. Consequence: the held-open adjacency "SPPF packed nodes =
identity-collapse as storage discipline (IDC as content-address)" is
upgraded from unattributed [C] to **corpus-witnessed [S-candidate]**: the
gabion corpus already treats packed-node sharing as the identity
discipline of an interned carrier graph.

## 4. Identification candidates (held at [C]; two flagged stronger)

1. **GALAXY–ASPF is the codec, again** (strong candidate). The corpus's
   own Theorem 9.1, W_{v,k} <-> log_alpha(F(s)^k), is an exp/log
   correspondence between a multiplicative prime-product magnitude and an
   additive weight — Lemma 2.5b's adjunction pattern, discovered
   independently in the author's prior work. If it survives a read of the
   merged_ontology proof, the atlas's 2.5b becomes the third sighting of
   one codec (Nedge L<->G, atlas A<->M, GALAXY<->ASPF).
2. **The ASPF normative rules are the prohibition + projection plurality**
   (strong candidate). "Provenance must not be erased by default" =
   refuse the information-destroying quotient (§3); "bitmask carriers are
   filters only; prime products remain authoritative" = projections are
   lossy reads, the carrier is authoritative (Remark 3.5); "deterministic
   and reversible at base/constructor" = the codec contract (§5.7 CDC).
3. **This session already enacted an ASPF rule.** The v3.4a fingerprint
   widening (S_8fecfdc135c8 naming two test semantics; fix = hash the full
   module source) is the ASPF discipline applied to the instrument itself:
   a structural fingerprint must cover everything semantics-bearing, and
   provenance (the artifactual verdict) was retained, not erased.
4. **APSP's doubling tower.** Segment length 2^(order-1) with conjugate
   pairing and epochal freeze-and-reuse is a doubling-interface shape
   (§5.9 adjacency); GALAXY as dimension-reduced hologram is a
   quotient-shadow read — R1's projective-shadow finding (Perron
   convergence of G under mass divergence) is the same move one level up.
5. **DIR graph = APSP graph = Nedge graph** (chart M009, body-read): the
   author's compiler-architecture vision already unifies the three;
   constraint propagation through bottlenecks = path structure as
   constraint solver. The atlas's carrier would be the evidence type of
   that unified graph; DIR's constraint-as-negative-space is the
   realizability charter's shape (admissibility by what must not happen).

## 5. Label oscillations (declare before any import)

- **APSP**: "All-Pairs Shortest Paths" (conversation corpus, executable
  math) vs "Adaptive Processing/Search Protocol" (the Gemini-authored OCAL
  synthesis doc). Same ladder-law obligation as Nedge's cost/strength
  rails: the algebra may be stable under the renaming, but the reading
  must be declared. Current evidence favors All-Pairs Shortest Paths as
  the author's usage.
- **ASPF**: reviewer's expansion wrong, corpus expansion canonical
  (Algebraic Structural Prime Fingerprint).

## 6. Frontier

- READ: "DIR, APSP, OCAL Isomorphisms Explored" (what is OCAL; does the
  claimed three-way isomorphism survive scrutiny; resolve the APSP
  expansion oscillation at the source).
- READ: merged_ontology Theorem 9.1 proof (candidate 1 above hinges on it).
- FETCH strategy needed for the two too-large docs ("ASPF Payload
  Alternation Ambiguity Example", "Parsing Sound and Video with System").
- The three APSP Drive folders are unenumerated.
- Candidate instrument claim if candidate 1 survives: GCX ("the GALAXY
  codex"), the third codec sighting as an executable check — only then a
  spec import (v3.3 lesson).
