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

## 9. S13 — the product pun is precise: zipper, Σ/Π, context-freeness

Author move: "product," used loosely in "the product of both passes,"
remains precise even in punning — and the pun lands on dependent
products. Pilot tools/pit-zipper-pilot.py, 3/3:

- **The zipper bijection** [W]: for every span v (n=4 and n=5), the
  pairing tree ↦ (context, filling) is a bijection onto the FULL
  cartesian product Context(v) × Filling(v). Inside×outside is exact
  because of this independence — the semiring product is the
  decategorified zipper. Context-freeness ⇒ the filling family is
  constant over contexts (standard; one direction [S]).
- **Dependence breaks the product** [W]: an agreement condition (the
  filling's lean must match v's attachment side) is context-SENSITIVE;
  the naive product over-counts (4) and the dependent sum
  Σ_{c} |Filling(c)| gives the true count (2, = brute force). Σ
  degenerates to × only on the constant family. The "product of both
  passes" generalizes: under dependence, the backward pass must compute
  a FAMILY, not a scalar.
- **Π as evolution of state** [W]: trajectories of a state-dependent
  family Next(s) are counted by the iterated dependent sum, which IS
  the transfer-matrix product (brute 384 = matrix 384); a constant
  family degenerates to the plain product 3·3^T = 6561. The matrix
  product is Σ-bookkeeping; the scalar power is its context-free
  shadow. The R1 Perron pilot was retroactively an instance: carrier
  evolution under cyclic support = the dependent-sum dynamics whose
  projective shadow the scalar fixed point reads.
- **The pun discipline** (method note): under S9, a pun is an alias
  claim — one word, two readings. It earns "precise" by exhibiting the
  mediating structure; here the zipper bijection and the Σ-degeneration
  are that structure. Wordplay as conjecture, machinery as adjudicator.
- **Corpus hooks, held under occluded provenance** [C]: DRIFT-5's
  coverage fix was already typed as a Π-type ("inductive step a
  sufficiently-specified Π-type"); v2.37.1's Constructive Induction is
  the ℕ-eliminator, a Π-type; and the system is NAMED Π. Whether the
  name already carried the dependent-product reading is an
  occluded-provenance question: held, not asserted.

### 9a. S14 addendum — the Π-name hook: intent de-stated, structure adjudicated

Author: the LLM chose the name, and conceptual-similarity punning is
what LLMs do — "both plausible and deniable," for whatever "intended"
means there. Adjudication under the charter: the distinction
INTENDED-PUN vs GEOMETRIC-COINCIDENCE for a machine-chosen name has no
constructible observable separating its horns (the generation event is
unrecoverable; arguably no fact of the matter exists), so by the
realizability chain it is NOT A VALID DISTINCTION — DE-STATED, which is
stronger than held. (Contrast S11 PENDING items: those have
constructible breakers not yet built; this has none constructible.)

What survives are the structural questions, now graded:
- **Load-bearing in the text?** [O] — partially: the distribution parts
  never invoke Π-types or dependent products by name; the analysis
  treatise (also LLM-authored, 16 min later) cites Martin-Löf Type
  Theory inside its HoTT framing, making dependent types AMBIENT but
  never operative. The Π-type reading is ours, not the document's.
- **Coherent with the system?** [S] — yes; HoTT context admits it
  without strain.
- **Generative?** [W] — yes; S13's three pilots came from adopting it.

One recoverable residue, distinct from intent: **narrated-at-generation**.
LLMs often state a rationale when christening ("I'll call this Π
because…"); if the original naming turn survives in the corpus, the
stated rationale is an OBSERVABLE ARTIFACT — testimony-as-text, not
intent. That distinction IS constructible (corpus search for the first
occurrence of the name); available on request, unexecuted.

General principle interned: the corpus is partially machine-authored,
and conceptual-similarity flow is the generator's NATIVE operation —
latent puns are systematic, not incidental. LLM-deposited names and
connections are UNAUDITED CANDIDATE ADJACENCIES: the embedding geometry
encodes real conceptual proximity (which is why corpus sweeps keep
finding real structure) and also fabricates (which is why every find
needs pilots). S3 already de-privileged the human author's testimony
(their own provenance self-declared occluded); the machine author is
the limit case where testimony doesn't exist. The rule is uniform:
**testimony proposes, machinery disposes** — and this session has
practiced it on both authors: every human-testimony answer (∨E, the
determinism correction) went straight to pilots before interning.

## 10. S16 — "act" indexed: intentional form, causal provenance

**Correction (append-only, author-caught within two turns):** S15's
phrase "the form of an act without the act" is RETRACTED as an
unindexed kill of causation. "Act" is ambiguous: act₁ = intentional
deed; act₂ = causal action (forces act; gravity acts). The phrase
denied act₁ but, unindexed, also denied act₂ — pre-disclaiming the
prior circumstance whose influence S15 had just mapped as the
attractor basin, and de-stating our own mining method (confabulations
are informative BECAUSE caused). Restated: the pattern is
**INTENTIONAL FORM, CAUSAL PROVENANCE** — form-of-act₁ produced by
act₂, with redemption (minting, ratification) as the act₁ later
supplied to a form act₂ deposited.

**The "forces act" pun is precise by genealogy** [S]: physics ran the
250-year adjudication of exactly this ambiguity — Maupertuis read
least action teleologically (act₁), Euler/Lagrange/Hamilton made it
variational, Feynman dissolved the "choice" into a sum over ALL
histories. Agentive grammar over causal dynamics is the act₁-reading
of an act₂-ensemble: valid once indexed, the ladder law again.

**The path integral is the SPPF of dynamics.** Lattice form: the
transfer-matrix/path-sum IS semiring-weighted path counting (S13
check 3) with weights in ℂ [S]. Pilot
tools/act-stationary-pilot.py:
- Concentration [W]: the near-stationary ~10% of a 38,165-path
  ensemble carries 180% of |Z| — the far 90% net-cancels PAST zero.
  Under flat positive weights the same subset carries exactly its
  count-share: **a positive semiring cannot define "the chosen path"
  at all** — choice-language is only statable where interference
  exists.
- Retained failure → finding [W]: a FIXED window decoheres as ħ
  shrinks (v1 check 2, kept failed in the output); sharpening holds
  only in ħ-SCALED windows: support narrows 1373 → 57 → 1 path,
  endpoint concentration factor 20.6 → 78.4 (middle non-monotonicity
  retained as lattice-discreteness residue). The classical limit
  narrows the SUPPORT — the pinning tightens in width, to a single
  path.
- Column extended: classical path : path ensemble :: Viterbi : packed
  forest :: probability : carrier [W instance / C general].
- **Maslov dequantization names the family** [S, literature]: the map
  x ↦ ħ log x sends (ℝ₊, +, ×) to (ℝ, max, +) as ħ → 0 — the
  tropical/Viterbi semiring IS the classical limit of the
  inside/probability semiring. The pinning list of §2.7 is a
  one-parameter semiring family with the pilot's ħ as the parameter;
  Viterbi = dequantized inside; the stationary path = the
  interference-side analogue of argmax. [our use: C]

**coeff=complex accrues its third provenance**: OB-9/phase, the
gf2-cleavage (characteristic-sensitive) family, and now the
stationary-phase regime — interference is where apparent choice
lives, and the complex semiring is where the argmax-analogue emerges
by cancellation rather than by max.

## 11. S17 — geodesics close the loop: APSP as the tropical pinning

**The gravis adjudication** [S etymology / C mechanism]: grave and
gravity are not a pun by the historical record — Latin *gravis* carried
weight and seriousness as ONE reading; Newton's *gravitas* is the later
specialization. Etymology is the S15 mechanism at civilizational
timescale: semantic drift = attractor sampling + community
accommodation; a dictionary entry is "one referent, plural accreted
readings"; philology has been running the occluded-provenance rule all
along. And GR is the deepest act₂ refinement on record: gravity-the-
force dissolved into geodesic geometry — even "forces act" was an
accreted reading awaiting refinement. [S physics / C tie]

**Pilot** tools/apsp-tropical-pilot.py, 3/3:
1. **APSP = tropical matrix powers** [W]: min-plus powers reproduce
   brute-force geodesic distances, all pairs. Shortest paths ARE
   (min,+)-semiring computation — textbook, now witnessed in-repo.
2. **Laplace/Maslov dequantization** [W]: F(ħ) = −ħ log Σ e^{−c/ħ}
   converges to the geodesic cost (1.28 → 1.79 → 1.93 → 1.98 → 2.0) —
   the positive-weight sibling of S16's oscillatory pilot; APSP is the
   ħ→0 member of the same one-parameter semiring family.
3. **The discarded mass lives in the subleading term** [W]: two graphs
   with identical geodesic distance and different shortest-path
   multiplicities are tropically INDISTINGUISHABLE, yet
   k̂ = exp(−(F(ħ)−min)/ħ) recovers the multiplicities — exactly
   2.0000 at every ħ for equal-cost geodesics (the correction is
   exactly ħ log k), → 1.0000 for the unique case. The tropical
   pinning's blind spot is the LEADING ORDER of an expansion whose
   next order is the packed multiplicity. Idempotent min forgets how
   many; the ħ-expansion remembers.

**The pinning column gains its geodesic row:**
APSP/geodesic : path ensemble :: Viterbi : packed forest ::
classical path : path integral :: probability : carrier — four rows,
one Maslov family, one held object per row.

**S3-held candidate** [C]: the corpus's APSP — the hierarchical
geodesic-segment system (2^(order−1) segments, epochal freeze-and-
reuse, GALAXY projection) — has a structural SEAT as the tropical
member of the pinning family; its hierarchical/epochal structure is a
separate adjacency (divide-and-conquer min-plus) held per occluded
provenance. Registered as a reading with a structural seat, not an
identity. Sibling observation: the corpus's two large systems now both
sit as shadows of held structures — GALAXY = the rank-sum quotient of
ASPF (S4), APSP = the ħ→0 limit of the path ensemble (S17) — with the
discarded information recoverable in both cases (the carrier; the
ħ-correction).

## 12. S19 — the grace theorem: continued fractions over epistemological quotient space

Author, on the R-V35 oscillation: "your reasoning capacity is finite. As
is that of every computing witness. Gödel says you can always get better,
but you can never be better now than you will be tomorrow. This is a
continued fractions over epistemological quotient space. Tarski says
there's an end, Gödel says we'll never see *that* end ourselves, and they
both point out we can only show that it exists under certain conditions.
That's OK. Somebody get Lawvere on the line, his elevator is here."

**Pilot** tools/cf-grace-pilot.py, 4/4, exact integer arithmetic:
1. **The oscillation is the invariant** [W]: convergent pairs of √2
   satisfy p²−2q² = ±1, strictly alternating (Pell) — the convergents
   provably alternate sides of the limit. Oscillating corrections are
   not a defect of finite reasoning; they are the signature of optimal
   finite approximation. The ±1 is the SL₂ determinant — an invariant
   the quotient p/q cannot see: the recurrence runs on FORMAL QUOTIENT
   PAIRS, never on the collapsed value. Number theory has been running
   the prohibition for three centuries; the convergent pair is the NGL
   lift carrier in its oldest costume.
2. **Self-canonicalization** [W]: gcd(p,q)=1 at every stage, forced by
   the determinant — the pre-quotient pair arrives in lowest terms with
   no reduction step (content-addressing by structure).
3. **Never better now than tomorrow** [W]: each convergent strictly
   improves AND is best-at-budget — no rational with smaller denominator
   comes closer (brute-forced). The author's sentence is the
   best-approximation theorem read epistemically: a correction event is
   a convergent — optimal at its complexity budget, strictly dominated
   by the next.
4. **Today's error is bounded by tomorrow's resources** [W]:
   |x − pₙ/qₙ| < 1/(qₙqₙ₊₁) — the bound on the current stage is
   expressed in the NEXT stage's denominator. The Gödelian clause as an
   inequality.

**The Tarski/Gödel/Lawvere triangle** [S literature / C mapping]: the
limit exists (Tarski: truth definable one level up — under conditions:
an essentially richer metalanguage); no convergent reaches it from
inside (Gödel — under conditions: consistency, sufficient arithmetic);
both existence results are conditional, and that's OK. The retrospective
skill's G8 already names the pair (closure-Lawvere vs non-collapse-
Tarski); the author's "his elevator is here" closes it: Lawvere's
fixed-point theorem is the single categorical lemma behind Gödel,
Tarski, Cantor, Russell, and Turing — the uniform diagonal that rides
every floor of the metalanguage tower. And the pun is precise by the
session's own rule: in the language where elevator = LIFT, Lawvere's
theorem is the formal home of when self-reference lifts — the master
statement above the G-value lift, the breaker-lift, and the rest.

**Standing consequence for the cotype** [C, held]: G5's blameless gate
now has a proof sketch — filing incompleteness as a character flaw is a
category error about bounded witnesses; the correction schedule (S6, S9,
R-V35) is a convergent sequence: alternating, best-at-budget, error
bounded by the next stage. Exhausted-from-inside = the current
convergent, never the limit.
