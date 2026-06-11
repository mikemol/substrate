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
identification is explicit in the author's own paper. The reviewer's acronym *expansion* differs from the
glossary's (Algebraic Structural Prime Fingerprint) — see §5/S3: under
occluded provenance these are plural readings of one referent, and the
*connection* was in any case not imported vocabulary; it was (by
knowledge or convergence) the author's own. Consequence: the held-open adjacency "SPPF packed nodes =
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

## 5. Names under occluded provenance (S3; supersedes "label oscillations")

S3 correction (author-instructed): virtually all corpus usages of APSP
refer to ONE general system; the synthesis grew until the acronym's
provenance became occluded, and multiple expansions are now VALID
READINGS of the same referent. The same holds for ASPF (related to
SPPF). Expansions are mention-level data — handles, not identities. The
S2 verdict "APSP RESOLVED / protocol-expansion = back-formation"
OVERCLAIMED: it settled which expansion one correction event used and
illegitimately promoted that to a referent-identity ruling. Under the
house discipline that was an IDC violation — separating at
probe='mention', which the instrument itself machine-found to be
impossible. Distinctness between readings is adjudicated by structural
separators, never asserted lexically.

- **APSP**: one general system presumed; witnessed expansions include
  All-Pairs Shortest Paths (the pathfinding correction event) and the
  synthesis doc's Adaptive Processing/Search Protocol — both held as
  readings of the one synthesis unless a structural separator is found.
- **ASPF**: the glossary witnesses "Algebraic Structural Prime
  Fingerprint"; the reviewer's parse-forest reading points at the same
  SPPF-related object (the corpus itself makes ASPF an SPPF
  packed-derivation label). "Wrong" RETRACTED — plural readings, one
  referent presumed.
- **OCAL**: plural candidate readings (abstraction-layer; the locale
  primitives). The structural question is what the OCAL handle's
  defining co-occurrence set looks like and whether it separates from
  the locale cluster under structural probes — not what the letters
  stood for.
- **Contrast retained**: the Nedge cost/strength RAIL oscillation is a
  different genus — orientation of a FIXED algebra, where a declared
  reading IS required (ladder law). Reading-declaration applies to
  orientations of one structure; structural adjudication applies to
  referent identity under name accretion. Do not confuse the two.

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


## 7. S2: the OCAL read (three docs fetched in full)

Docs read: "DIR, APSP, OCAL Isomorphisms Explored" (Gemini synthesis,
2025-12-07, two identical copies); "PBF Trace and System Pi Isomorphisms"
(Gemini synthesis, 2025-12-07, two copies); "OCAL" (2024-08-04 — the DIR
encyclopedic overview + White Paper Books 1–4, OCAL never defined inside).

### Observed [O]

**System Pi (v2.22) is Nedge's formal meta-specification** — HoTT kernel
(univalence explicitly integrated), category/topos theory libraries,
directed type theory (DirectedPath, compose_dir, OrthoPath), linear types
with tensor products, Grothendieck topos with Heyting-valued local truth,
Langlands/trace-formula libraries, and the Nedge Quine (a PBF set whose
interpretation instructs handing over that very set; F_Crucible functor
maps the Crucible debate engine onto the Toulmin model). Drive IDs for
SYSTEM Pi v2.22 appear in the works-cited:
1xoOcDPEcCKKArJsDsAQUDgNYOjdUxwhleREneHTvUkw and
10GrDUQdXh_uLc-bUGBiuXPyYSY8C8ZxwXKd1s3F-dMc (two IDs, unfetched).

**PBF mechanics** (extends the N-series foundation): PBF Trace =
(Outer/Framer, Inner/Framee), no separate edge label — the predicate IS
the outer handle; "no magic strings." A named correction event in the
author's history: the Protobuf pattern_id field was REMOVED as "lexical
contamination" — type is intrinsic to the outer handle (Compositional
Identity enforced by remediation, not by fiat). **Duality and
Cancellation**: "Every edge has a potential dual; a pair cancels to
unit"; falsity is handled by APPLYING THE DUAL, never by deletion — the
OUA ledger preserves the full history of the error.

**DIR inside System Pi** = "Directed": directed type theory as the arrow
of time/causality; the PBF ordered pair is a DirectedPath. **OCAL-side
primitives** = Locales/Topos: LocaleDef carries a complete Heyting
algebra; truth is local — a PBF can be true in Locale X and false in
Locale Y, both maintained without collapse by sheaf segregation.

### Identification candidates [C unless marked]

7. **Duality-and-Cancellation is the antipode constraint at the edge
   level, practiced pre-quotient.** "Pair cancels to unit" is
   G(P)·G(¬P) = 1 in the multiplicative chart; "apply the dual, never
   delete, ledger preserved" is the R1 result (merge does not factor
   through the quotient; negative evidence is an accumulator, not an
   eraser) already deployed in Nedge's own editing discipline. The
   strongest yet evidence that Nedge's practice is carrier-shaped even
   where its G-value theory is quotient-shaped. [S-candidate]
8. **OCAL-as-local-truth is verdict-relativity formalized.** Heyting-
   valued truth over a site, contradictions segregated into sheaves =
   "no unindexed verdicts": the harness's S_-indexed verdicts are
   sections over a site of declared model spaces; the atlas's
   conflict-preservation is the same refusal-to-collapse one level down.
   If the System Pi LocaleDef survives a direct read, the cotype's
   epistemics has a formal home in the author's own corpus. [strong C]
9. **The trace-formula claim names our Perron pilot.** The synthesis doc
   maps geometric side = PBF graph, spectral side = "eigenvalues of the
   G-Value Calculus." R1's runtime pilot computed exactly an instance:
   G* = the Perron eigen-ratio of carrier pair-dynamics (mass diverges,
   the spectral coordinate converges). Geometric/spectral = carrier/
   projective-shadow — third sighting of the move. [C, pilot-adjacent]
10. **The pattern_id remediation is the knob-admission governance
   pattern**: a distinction (lexical type label) demoted by a named
   correction event because structure already carries it. Same shape as
   fingerprint-widening (v3.4a) and the basis_def admission. [S-candidate
   for the governance overlay, not the spec]
11. First Isomorphism Theorem as used (concept G, context = Kernel,
   expressed meaning = Image) — context-as-quotient vocabulary; the
   atlas would say: the kernel is what the reading relation pins. [C]

### Glaze flags

The Langlands material (compilation = finding the automorphic form;
"Perfect Compilation"; language = Riemann surface) is grandiose synthesis
prose; held as vocabulary adjacency only. The "body/metabolism/soul"
triad framing likewise. The isomorphism TABLE (stream≅path,
constraint≅proof via Curry-Howard, execution≅homotopy) is standard and
sound; the grand three-system "isomorphism" is a Gemini framing of the
author's actual import relations (DIR Books import APSP's community
model; System Pi formalizes both).

### Frontier updates

- FETCH System Pi v2.22 directly (two Drive IDs above) — author-voice
  OCAL definition, LocaleDef, DirectedTypeTheoryDef, the G-value/
  trace-formula passage if present.
- The author-voice OCAL expansion remains the missing witness; ask or
  locate the originating conversation (the Aug-2024 "OCAL"-titled doc's
  source chat).
- merged_ontology Thm 9.1 proof read still pending (GCX gate).
- Toulmin: F_Crucible maps the Crucible onto the Toulmin model — the
  unread Toulmin analysis is now doubly indexed (N-series + System Pi).


## 8. S3: the occluded-provenance rule (author-instructed, adopted)

"The system will sort out what's distinct from what on what basis; *we*
don't have to assert that one thing is not another without letting the
system independently prove it." Adopted as standing governance:
referent-identity questions for accreted names (APSP, ASPF, OCAL, ...)
are settled by structural separators — instrument claims, co-occurrence
and participation probes — never by lexical expansion. This is IDC
applied at the name level: expansions are probe='mention' data, and the
machine-found result stands (mention probes cannot separate). It is
also the corpus's own "no magic strings" / pattern_id-remediation
principle, now pointed at our own triage practice. Default presumption
under occlusion: ONE referent, plural readings; distinctness must be
EARNED. Symmetrically, identity must also be earned before any merge
that destroys a distinction — the presumption holds readings together
without quotienting them (per the realizability gates: hold, don't
collapse).

## 9. S4: merged_ontology read; GCX pilot PASSED with a sharper finding

merged_ontology (Drive 1t-FBAXwRjUda5f6WxDNSo5Nem8W2rwtqPoAVIq7VGaQ) read in
full: ECHO and Gabion as one framework — six-layer shared architecture,
unified vocabulary (Table 8.1), three formal theorems, Yoneda + 1-WL +
prime factorization as the shared ground.

**GCX pilot (tools/gcx-codec-pilot.py, output committed): the third codec
sighting is CONFIRMED at the codec layer.** Theorem 9.1's substitution
W <-> log_alpha(F^k) is the exp_alpha -| log_alpha adjunction exactly —
roundtrip, product<->sum, power<->scalar action, F=1<->W=0, and base
change as gauge — all five identities exact over 2000 seeded trials.
Lemma 2.5b's codec now has three independent sightings in the corpus:
Nedge L<->G, the atlas A<->M, GALAXY<->ASPF (gauge alpha).

**The sharper finding (the document missed it):** the theorem's
"canonical prime assignment" p(t) = alpha^rank(t) is not a prime
assignment — alpha-powers collide on equal rank-sums. Demonstrated:
rank-multisets {1,4} and {2,3} collide on the W-side (5 = 5) and the
alpha-side (0.168070 both), while genuine prime products distinguish
them (33 != 35). So Theorem 9.1's "isomorphism" holds exactly on the
RANK-SUM QUOTIENT: **GALAXY is a one-mode decode — a lossy projection —
of the ASPF carrier**, and the doc's own normative rule ("prime products
remain authoritative; reversible") is sacrificed by its own canonical
assignment. Corrected statement: GALAXY ≅ ASPF / rank-sum-kernel, the
iso being the codec on the quotient. The prohibition's vocabulary
applies verbatim: GALAXY : ASPF :: probability : carrier — a useful
pinned slice, not the carrier. [W pilot for both halves]

**Claim GCX defined and ready to board the next instrument run**: the
five codec identities + the quotient-collision fact as executable
checks; guard coeff=real (alpha-powers/log unstatable in char 2).
Per the v3.3 lesson, the spec import of the third-sighting note (and
the GALAXY-as-quotient-shadow correction) rides that run, not before.

Theorems 9.2 (ASPF bitmask = collision-free degenerate CONSTELLATION)
[O, clean] and 9.3 (drift = homotopy; AURORA rotation as the connecting
1-cell) [C, joins the witness-discipline adjacency] recorded.

**System Pi is occluded name #4** (S3 discipline applies). The family,
IDs now on record: v2.22 self-hosting formal OS
(10GrDUQdXh_uLc-bUGBiuXPyYSY8C8ZxwXKd1s3F-dMc, 115KB — QUEUED for a
dedicated read); "SYSTEM Pi Extended and Corrected" v2.3
(1pBY47gt1D7HtM9yGfYing_f7yt2RS6t0rlmxJvvwFUY — carries its source chat
URL; the Epoch 9 canon-restoration is ANOTHER named correction event:
append-only history enforced against lossy formalization); v2.37.1
treatise (19ulW-k7h85oEpkOUfijgT-fo8Qzp-ZgR55-9AOWbFc0 — Earley/
simplicial/quiescence; "Meaning is Structure"); Veritas Core
PyTorch->JAX transpiler docs (1lx35..., 14a3d..., 1yyKN... — ALSO
SPPF-threaded: "resolved via a Shared Packed Parse Forest of
optimization strategies"); SystemPi.agda cognitive harness
(1MafDyCdW2Z4hj1LPwRxcy1v-QWgVrRUzWi8Ivz1D00o — the Constructibility
Filter is the realizability-charter lineage; AMR/Lojban semantic
domain). Plural readings, one presumed synthesis, adjudication
structural only.
