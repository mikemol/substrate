# Theory threads intern (T-series): Tarski, parsing, grammar theory

Prompted by the v2.37.1 recovery and the S6 correction. Threads that had
been ambient across the corpus are now load-bearing; this document interns
them with grades. NO spec import here (v3.3 lesson); candidate claims are
defined for boarding.

## 1. The Tarski thread [all C unless marked]

1. **Truth-as-parse-success is a Tarskian truth definition with a
   decidable truth predicate.** Lemma_ParsingAsTruth ("Success in the
   Earley Sieve is the definition of Truth") defines truth for the object
   language in a metalanguage (grammar + parser) — Convention-T shape.
   Because parse-success is SYNTACTIC and decidable (CFG, O(n^3)), no
   undefinability violation arises — *under the deflationary reading*.
2. **The v2.37.1 reading oscillation is oscillation across the Tarski
   boundary.** The distribution alternates between truth-as-
   grammaticality (consistent, deflationary) and truth-as-mathematical-
   validity (hosts ZFC/reals; undefinability and Gödel bite). The fix is
   a declared reading — the ladder law, again. The oscillation is the
   document's deepest flaw and it is a *declaration* flaw, not a
   structural one.
3. **Indexed verdicts are truth-in-a-context.** The harness's
   "unseparated-in-S" discipline = Tarskian relativization to a declared
   model space; the OCAL locale thread (Heyting-valued, sheaf-segregated
   truth) is its topos-theoretic generalization (Kripke–Joyal adjacency).
   "No unindexed verdicts" = no truth predicate without its metalanguage
   named. [strong C; joins S2 candidate 8]
4. **The scrutiny strata are a truth-predicate hierarchy.** knob values →
   knob set → test semantics → claim formalization is an object/meta
   tower: each stratum is the metalanguage in which the one below is
   adjudicated. [C]

## 2. The parsing/grammar thread

5. **The Earley commitment is one commitment, corpus-wide** [S]:
   v2.37.1's KernelProver; the Maildir-Earley continuation machine; the
   CYK/Earley hybrid; gabion's Forest = Earley chart; the constraint-
   propagation monograph organized by SPPF node ontology. Completeness
   over speed, every time — the parsing-layer form of non-pruning.
6. **The SPPF is the pre-quotient of the parse** [S; author-voice S6]:
   "the parser takes nondeterministic input and produces a deterministic
   result; the SPPF preserves the ambiguity — ambiguity recognized is
   deterministic." carrier : probability :: SPPF : pruned parse tree.
   Genealogy of the move: NFA subset construction (the set of
   possibilities as one determined object) → SPPF (CFG instance) →
   the evidence carrier (epistemic instance). One design principle:
   when an operation would lose information, encode it (Remark 3.6).
7. **Semiring parsing is the rigorous prior-art bridge** [W — pilot
   tools/swp-carrier-parsing-pilot.py, output committed]. Goodman-style
   weighted deduction: ONE chart computation, pluggable semiring — and
   the semiring choice IS the quotient choice. Pilot results (CKY,
   S→SS|a, 'aaaa', 5 derivations):
   - carrier weights (product semiring on pairs): root E+ = 5 — the
     mass axis carries the multiplicity the SPPF packs (counting
     shadow);
   - probability = a SECTION of carrier parsing: positive-rail-only,
     locally normalized weights → root E+ = inside probability exactly
     (5p³q⁴), E- ≡ 0 — the no-conflict rail;
   - Viterbi = an idempotent PINNING: (max,×) returns the best single
     derivation; the multiplicity is unrecoverable — argmax is pruning,
     the forced disambiguation;
   - conflation witness: lexicons (2,1) and (4,2) give equal G-shadow
     (16.0) with masses 85 vs 1360 — the ratio-quotient cannot see
     evidence volume at the parse level either.
   Projection plurality for parsing: Boolean/counting/Viterbi/inside are
   lossy reads of one weighted forest; the carrier semiring keeps what
   they each discard. Provenance note: the v2.37.1 analysis treatise's
   own works-cited includes "Efficient Semiring-Weighted Earley Parsing."
8. **The packed node is the equality witness** [S]: two derivations,
   same span, same yield — packed = the 2-cell (AspfTwoCellWitness in
   embryo in v2.37.1's associativity proof, per S6). Drift = no 2-cell =
   unpacked.
9. **Nedge's open ∨E — ANSWERED (author, S8)** [W pilot]: the
   single/double pin split/join carrier expansion plus the Wheatstone
   bridge (nedge-decomposition §8; tools/nve-bridge-pilot.py). The
   packed-node reading below survives as the same answer one layer up:
   the pack is the storage of the held disjunction, the split/join is
   its arithmetic, the bridge is its measurement. Claim NVE defined;
   boards with GCX and SWP.
10. **LangSec convergence** [S]: default-deny as parse failure; the
   parser as the security boundary; v2.37.1's Contextual Security is the
   corpus's independent arrival at language-theoretic security.

## 3. Candidate claims for the next instrument run

- **SWP** (semiring-weighted parsing): pilot-backed above. Checks: the
  four pilot facts as executable tests; guards: coeff=real (the weight
  semirings need char 0; over GF(2) counting collapses mod 2), pins≥2
  for the carrier checks. Boards with GCX.
- GCX already defined and pilot-backed (S4).
- DCN / locale-verdict candidates still await the System Π v2.22 read.

## 4. Frontier

- Tarski thread: does the spec want a remark ("the indexed-verdict
  discipline is a truth-definition discipline")? Only after SWP/GCX
  board a run.
- ∨E packed-node semantics: needs a worked pilot against the N4 source's
  Phase-4 flag before any decomposition-doc upgrade.
- Semiring-weighted EARLEY (not just CKY) with the carrier semiring over
  an ambiguous natural-language-ish grammar — the runtime-bridge story
  (R1) meets the parse chart: source-indexed carrier weights per packed
  alternative.
- Subset-construction genealogy: is determinization-as-reification
  worth a spec overlay row (NFA→DFA, SPPF, carrier)? [C]

## 5. S9 revision note — "superseded" over-executed; item 9 adjudicated as alias

Author rule adopted: **a supersession event is an alias circumstance**
until the delta is validated — the kill-verb may be an over-executed
"in this context, this, not that." The S8 edit to item 9 was the case in
point: an in-place rewrite plus the verb "superseded," while the
replacement text itself asserted "the same answer one layer up." The
textual delta survived only because git is append-only at the storage
layer (15a6954..d221ef3); the semantic delta is now validated by pilot
(tools/nve-alias-delta-pilot.py, 3/3):

- **Alias at n=2** [W]: against the balanced reference, the bridge
  reading of a case-pair equals half its L1-normalized internal bias,
  exactly. The pack's storage-level bias read and the bridge's
  measurement-level read are the same number — one referent, plural
  layer-readings (the S3 shape, not supersession).
- **Separated at n≥3** [W]: the delta is ARITY. Packs (1,2,3) and
  (1,2.5,2.5) share mass and the partition-{1} reading; differ on
  partition-{2}: one binary bridge under-determines an n-pack.
- **Reconciliation** [W, advancing the open n-ary item]: pack tomography
  = the mass channel + exactly (n−1) partition bridge readings —
  necessity by the blindness witness, sufficiency by exact linear
  reconstruction. The multi-arm answer is a bridge LATTICE.

Both formulations of item 9 are therefore RETAINED as layer-readings of
one referent at n=2, with the packed node strictly richer at n≥3 until
the lattice is built. Future instrument work may formalize the pack
checks and bridge checks as separate claims and let depsort confirm
same-circle at pins=2 — the full-machinery version of this adjudication.

## 6. S10 note — the Gödel tension is reading-indexed

Correcting an over-broad survival claim from S6: the Gödel tension in
v2.37.1 does not "stand on its own witnesses" unconditionally. It is
indexed by the same reading whose oscillation §1.2 names: real under the
validity reading; DISSOLVED under the deflationary reading, where the
Total Coherence Proposition asserts only that the artifact parses — a
decidable claim with no consistency-of-arithmetic exposure. Same
correction shape as S6's Earley-determinism retraction: a criticism
pinned to one reading, stated as absolute. See kill-audit.md item 11.

## 7. S11 — the parsing-liar breaker for the reading oscillation [S]

The T1 breaker, constructed. v2.37.1 claims self-description capacity
(Lemma_TheKnot; grammar reflexivity), so parse-predicates are
expressible; by the standard diagonal construction there is a string λ
whose content, under the validity reading's interpretation, is
¬Parses(P, λ, G).

Validity reading (truth = the interpreted content holds): if λ parses,
Lemma_ParsingAsTruth makes λ true, so ¬Parses(λ) — contradiction. If λ
does not parse, then ¬Parses(λ) is TRUE but λ is "ontologically
nonexistent" — a truth the topos cannot contain, violating the
Completeness quality (no Gaps). Either horn breaks a system commitment.

Deflationary reading (truth := parse-success): λ's content is Noise by
Asemantic Materialism (axiom 1.3); Parses(λ) is a bare syntactic fact;
no interpretation map participates in truth; nothing breaks.

So the breaker separates the readings, and the distribution's own axiom
1.3 is what survives it — the system's axioms adjudicate the oscillation
toward the deflationary side; the validity-flavored prose drifts against
the system's own foundation. Tarski undefinability is the general
theorem behind the asymmetry: the validity reading needs the truth
predicate inside the language; the deflationary reading keeps it
syntactic and decidable. Grade [S]: structural derivation (diagonal
availability via TheKnot assumed, standard); the executable form — an
actual grammar-quine λ — is constructible if ever wanted.

## 8. S12 — bidirectionality: completeness is purchased by alternation

Author principle: "all thorough reasoning requires iterating over
forward and backward passes, or at least iterating over alternating
generators." Held in the strong universal form as [C]; witnessed
instances graded individually:

- **Earley itself** [S, textbook]: the predictor is the top-down
  generator (goal-driven expectation), scanner/completer the bottom-up
  one (data-driven confirmation), interleaved over a shared chart to a
  fixpoint. Pure top-down (LL) dies on left recursion; pure bottom-up
  (LR) demands determinism; the corpus's Earley-for-completeness
  commitment is secretly a BIDIRECTIONALITY commitment.
- **Inside–outside** [W — tools/bdp-inside-outside-pilot.py]: the SWP
  pilot's forward pass answers only the root question. (1) At every
  span, inside×outside = the count of derivations containing it,
  exactly; (2) forward under-determination witnessed: spans with equal
  inside (both 1) have different participation totals (5 vs 2) — the
  backward pass is not optional for per-node questions; (3) on the
  carrier semiring the identity holds in pairs, and the (2,1)/(4,2)
  conflation is POINTWISE: equal G-shadow at every span, masses
  differing at every span. SWP gains this as its fifth check.
- **The adjunction is the canonical forward-back/backward-forward** [S]:
  unit and counit with the triangle identities — Lemma 2.5b's exp ⊣ log
  already in the spec; iterating a Galois connection stabilizes at
  closure. Quiescence (v2.37.1 Phase 5: every Question answered by a
  Fact; the agenda empties) = the alternation's fixpoint, which is also
  exactly Earley chart saturation. [C/S]
- **The governance instance, OBSERVED in-session** [O]: S10's backward
  pass (kill audit) generated forward obligations (T2/T4/T5); S11's
  forward pass (tension ledger) sharpened a backward criticism (the
  Gödel adjudication via the parsing-liar). One full alternation cycle.
  The S9/S11 pair makes the cotype an Earley-style agenda algorithm
  over the workstream's own claims: tensions = predictions, witnesses
  and breakers = completions, quiescence = empty agenda.
- **AJ = alternating generators at design level** [S, N-series]:
  proposal/critique as the two generators; the admission rule as the
  chart discipline.
- Wider family, held as context [C]: forward–backward (HMM posteriors),
  backpropagation (forward eval + reverse adjoint), bidirectional
  typing (synthesis ⇑ / checking ⇓), CDCL (decide forward, learn
  backward), belief propagation, bidirectional search; the user's own
  APSP epochal system.
