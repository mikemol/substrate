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
