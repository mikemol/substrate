-- ============================================================================
-- Populate the elaborator-sketch database.
--
-- Encodes the depth-2/3/4 sketch produced under decompose-by-entailment +
-- structural-strictifier. The data shape mirrors the prose:
--   * 1 root (arch)
--   * 4 layer-1 clusters (C1..C4)
--   * 12 layer-2 sub-shadows
--   * ~31 layer-3 sub-sub-shadows (depth-3 expansion)
--   * 8 productive layer-4 expansions + 4 cross-cutting (X1..X4)
--   * leaves and research-frontiers marked, not forced into pseudo-decomposition
-- ============================================================================

BEGIN TRANSACTION;

-- ============================================================================
-- ROOT
-- ============================================================================
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('arch', NULL, 'sequent-indexed-elaborator', 0, NULL, 'root',
   'R(reach, role-labeled-graphs)',
   'Route Agda Signature and MetaStore through a sequent-indexed SPPF; live state bounded by unique productions in Gamma rather than total subterm count.');

-- Root role edges (the layer-1 PENMAN tree)
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':hosts',                 'h',  'agda-elaborator'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':replaces-internals-of', 'old','signature-as-intmap + metastore-as-intmap'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':decomposes-into',       'c1', 'Gamma-store'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':decomposes-into',       'c2', 'Delta-queue'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':decomposes-into',       'c3', 'cut-engine'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':decomposes-into',       'c4', 'soundness-discipline'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':bound-by',              'b',  '|Gamma-unique-productions|'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':discharges',            'd',  'oom-on-monolithic-All-target'),
  ((SELECT id FROM shadows WHERE code='arch'), 'arch', ':preserves',             'p',  'agda-typechecking-semantics');

-- ============================================================================
-- LAYER 1 — four clusters
-- ============================================================================
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C1', (SELECT id FROM shadows WHERE code='arch'), 'Gamma-store', 1, 'C1', 'productive',
   'R(reach, transitions)',
   'Signature as content-addressed grammar: holds Agda definitions as production rules.'),
  ('C2', (SELECT id FROM shadows WHERE code='arch'), 'Delta-queue', 1, 'C2', 'productive',
   'R(reach, transitions)',
   'MetaStore as open right-sequent: holds unresolved metavariables and their constraints.'),
  ('C3', (SELECT id FROM shadows WHERE code='arch'), 'cut-engine', 1, 'C3', 'productive',
   'R(reach, transitions)',
   'Unification as sequent proof-search; composes left-rule applications with cut-elimination.'),
  ('C4', (SELECT id FROM shadows WHERE code='arch'), 'soundness-discipline', 1, 'C4', 'productive',
   'R(reach, transitions)',
   'Per-rule invariants licensing cut: cut-soundness, structural rules, subformula property.');

-- C1 transitions
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1'), 1, 'empty-Gamma',         'ingest-definition(name, type, body)', 'body-typechecks-in-current-Gamma', 'production-registered'),
  ((SELECT id FROM shadows WHERE code='C1'), 2, 'production-registered','link-references(prod-key, sub-term-keys)','all-sub-terms-have-Gamma-keys',   'production-linked'),
  ((SELECT id FROM shadows WHERE code='C1'), 3, 'production-linked',   'snapshot(persistent-store)',          'transaction-boundary-reached',    'persistent-Gamma-snapshot');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C1'),
   'foldM ingest-definition over module-imports in topological order; each fold step adds productions to Gamma.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C1'),
   'each ingest-definition preserves Gamma-consistency (C4.1) AND link-references is total',
   'whole Gamma-snapshot is consistent and queryable by C3');

-- C2 transitions
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C2'), 1, 'closed-Delta (empty)','allocate-meta(scope, type-ctx)',          'type-ctx-well-formed-in-Gamma-snapshot', 'Delta-open-by-one'),
  ((SELECT id FROM shadows WHERE code='C2'), 2, 'Delta-open-by-one',   'pose-constraint(meta-id, shape)',         'shape-references-only-known-metas',       'constraint-queued'),
  ((SELECT id FROM shadows WHERE code='C2'), 3, 'constraint-queued',   'try-discharge-via-left-rule(meta-id, Gamma)','Gamma-snapshot-current',               'meta-resolved OR constraint-pending');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C2'),
   'Delta shrinks monotonically under successful left-rule applications; grows under fresh meta-allocation. Outer loop is C3.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C2'),
   'every left-rule application is cut-sound (C4.1)',
   'Delta -> empty implies the original elaboration goal is closed');

-- C3 transitions
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C3'), 1, '(Gamma, Delta)-state',     'select-pending-constraint(Delta)',           'Delta-nonempty',                    'constraint-focused'),
  ((SELECT id FROM shadows WHERE code='C3'), 2, 'constraint-focused',       'search-Gamma-for-matching-production(constraint)','Gamma-indexed-by-conclusion-shape','candidate-production-found'),
  ((SELECT id FROM shadows WHERE code='C3'), 3, 'candidate-production-found','apply-cut(candidate, focused-constraint)',  'arities-match AND types-unify',     'Delta-reduced OR unification-failure'),
  ((SELECT id FROM shadows WHERE code='C3'), 4, 'Delta-reduced OR unification-failure','cut-normalize(reduced-Delta)',       'no-stuck-redexes',                  '(Gamma, Delta-prime)-state with |Delta-prime| <= |Delta|');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C3'),
   'Outer fixed-point loop: until Delta stable, select-focus-search-apply-normalize. Termination guaranteed if cut-elimination terminates (delegated to C4.3).');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C3'),
   'cut-elimination preserves sequent-validity (C4.1 per-step)',
   'outer fixed-point gives Delta -> empty (success) OR unification-failure');

-- C4 transitions
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4'), 1, 'candidate-right-rule-introduction','verify-RHS-expansion-equals-LHS',            'expansion-well-typed-in-Gamma-snapshot','cut-sound-introduction'),
  ((SELECT id FROM shadows WHERE code='C4'), 2, 'cut-sound-introduction',           'register-as-production(name, RHS, expansion)','name-unique-in-Gamma',                 'Gamma-extended'),
  ((SELECT id FROM shadows WHERE code='C4'), 3, 'Gamma-extended',                   'check-subformula-property',                  'RHS-mentions-only-bound-vars',          'locality-verified'),
  ((SELECT id FROM shadows WHERE code='C4'), 4, 'locality-verified',                'apply-structural-rules(exchange, contraction)','siblings-have-mirror-form',           'Gamma-consistent-after-introduction');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C4'),
   'Each extraction event passes C4.1 -> C4.3 -> C4.2 before committing to Gamma. Order: soundness first, then locality, then structural form.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C4'),
   'every introduction is cut-sound AND subformula-local AND structurally-well-formed',
   'Gamma-as-a-whole is consistent and admits cut-elimination');

-- ============================================================================
-- LAYER 2 — twelve sub-shadows
-- ============================================================================

-- C1 sub-shadows
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C1.1', (SELECT id FROM shadows WHERE code='C1'), 'structural-hash', 2, 'C1', 'leaf',
   'R(reach, transitions)',
   'Content-addressed key for each subterm via canonical de-Bruijn encoding + BLAKE3.'),
  ('C1.2', (SELECT id FROM shadows WHERE code='C1'), 'production-ref-index', 2, 'C1', 'productive',
   'R(reach, role-labeled-graphs)',
   'Inverted index sub-term-key -> set of containing productions; enables left-rule search.'),
  ('C1.3', (SELECT id FROM shadows WHERE code='C1'), 'persistence-layer', 2, 'C1', 'productive',
   'R(obs, role-labeled-graphs)',
   'On-disk Gamma store; sqlite or LMDB; tables for productions, subterm_refs, snapshots.');

-- C2 sub-shadows
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C2.1', (SELECT id FROM shadows WHERE code='C2'), 'meta-allocator', 2, 'C2', 'productive',
   'R(reach, transitions)',
   'Generates fresh meta-id with reverse-link into the constraint graph.'),
  ('C2.2', (SELECT id FROM shadows WHERE code='C2'), 'constraint-graph', 2, 'C2', 'productive',
   'R(reach, role-labeled-graphs)',
   'Directed graph of dependencies between unresolved metas; cycles trigger C3.3.'),
  ('C2.3', (SELECT id FROM shadows WHERE code='C2'), 'left-rule-applicator', 2, 'C2', 'productive',
   'R(reach, transitions)',
   'Given meta + constraint, queries C3.1 for productions whose RHS unifies.');

-- C3 sub-shadows
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C3.1', (SELECT id FROM shadows WHERE code='C3'), 'production-index', 2, 'C3', 'productive',
   'R(reach, role-labeled-graphs)',
   'Gamma indexed by RHS-shape (head-symbol + arity) for O(1)-ish candidate lookup.'),
  ('C3.2', (SELECT id FROM shadows WHERE code='C3'), 'unifier', 2, 'C3', 'productive',
   'R(cov, types)',
   'The trusted kernel; typed-term cell. Decidable type-equality up to reduction in Gamma.'),
  ('C3.3', (SELECT id FROM shadows WHERE code='C3'), 'cut-normalizer', 2, 'C3', 'productive',
   'R(reach, transitions)',
   'Eager reduction of composed applications; terminates by subformula property (C4.3).');

-- C4 sub-shadows
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C4.1', (SELECT id FROM shadows WHERE code='C4'), 'cut-soundness-check', 2, 'C4', 'productive',
   'R(reach, transitions)',
   'RHS == expansion under Gamma; corresponds to `agda --safe --without-K` per-extraction.'),
  ('C4.2', (SELECT id FROM shadows WHERE code='C4'), 'structural-rule-discipline', 2, 'C4', 'productive',
   'R(reach, role-labeled-graphs)',
   'Chirality-pair completeness + section-then-lemma exposure at file boundaries.'),
  ('C4.3', (SELECT id FROM shadows WHERE code='C4'), 'subformula-property-check', 2, 'C4', 'productive',
   'R(reach, transitions)',
   'RHS only mentions variables bound on LHS; guarantees cut-elimination terminates.');

-- ============================================================================
-- LAYER 3 — depth-3 sub-sub-shadows (31 total)
-- ============================================================================

-- C1.2 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.2.1', (SELECT id FROM shadows WHERE code='C1.2'), 'edge-representation', 3, 'C1', 'leaf',
   '(parent_prod_key, child_term_key, position-in-RHS). Tuples in sqlite or HashMap in memory.'),
  ('C1.2.2', (SELECT id FROM shadows WHERE code='C1.2'), 'index-update-protocol', 3, 'C1', 'productive',
   'On ingest-definition, walk body AST and insert one edge per subterm reference, in a single transaction.'),
  ('C1.2.3', (SELECT id FROM shadows WHERE code='C1.2'), 'query-by-subterm-API', 3, 'C1', 'productive',
   'Given a content-key, return the set of productions containing it. Called by C3.1 during cut search.');

-- C1.3 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.3.1', (SELECT id FROM shadows WHERE code='C1.3'), 'schema', 3, 'C1', 'leaf',
   'Three tables: productions(key PK, name UNIQUE, type-key, body-key), subterm_refs(parent_key, child_key, pos), snapshots(snapshot_id PK, root_productions, created_at).'),
  ('C1.3.2', (SELECT id FROM shadows WHERE code='C1.3'), 'transaction-boundaries', 3, 'C1', 'productive',
   'One transaction per module-load; commit at end-of-module, rollback on any C4 verification failure.'),
  ('C1.3.3', (SELECT id FROM shadows WHERE code='C1.3'), 'incremental-load-protocol', 3, 'C1', 'productive',
   'On agda Foo.agda, load Gamma-snapshot for transitive imports first, then begin a fresh transaction for Foo.');

-- C2.1 children (leaves)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C2.1.1', (SELECT id FROM shadows WHERE code='C2.1'), 'scope-context-bookkeeping', 3, 'C2', 'leaf',
   'Per-meta record: lexical scope under which it was allocated.'),
  ('C2.1.2', (SELECT id FROM shadows WHERE code='C2.1'), 'id-generation', 3, 'C2', 'leaf',
   'Monotone counter; metas are ephemeral and need not be content-addressed across sessions.');

-- C2.2 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C2.2.1', (SELECT id FROM shadows WHERE code='C2.2'), 'node-representation', 3, 'C2', 'leaf',
   '(meta-id, constraint-shape, status: open|resolved|failed).'),
  ('C2.2.2', (SELECT id FROM shadows WHERE code='C2.2'), 'edge-representation', 3, 'C2', 'leaf',
   '(meta_a, meta_b) = discharge of meta_a depends on prior discharge of meta_b.'),
  ('C2.2.3', (SELECT id FROM shadows WHERE code='C2.2'), 'cycle-detection', 3, 'C2', 'productive',
   'Tarjan SCC; cycles trigger C3.3 fixed-point.');

-- C2.3 children (leaves — pipeline plumbing)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C2.3.1', (SELECT id FROM shadows WHERE code='C2.3'), 'shape-extractor', 3, 'C2', 'leaf',
   'Maps a constraint to its head-symbol-plus-arity signature for index lookup.'),
  ('C2.3.2', (SELECT id FROM shadows WHERE code='C2.3'), 'candidate-filter', 3, 'C2', 'leaf',
   'Iterates the index hit-set, attempting unification via C3.2.'),
  ('C2.3.3', (SELECT id FROM shadows WHERE code='C2.3'), 'cut-request-emitter', 3, 'C2', 'leaf',
   'Hands the (production, meta-id, unifier) triple to C3 for substitution.');

-- C3.1 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C3.1.1', (SELECT id FROM shadows WHERE code='C3.1'), 'rhs-shape-extractor', 3, 'C3', 'leaf',
   'Same algorithm as C2.3.1; maps a production-body to (head-symbol, arity).'),
  ('C3.1.2', (SELECT id FROM shadows WHERE code='C3.1'), 'hash-table', 3, 'C3', 'leaf',
   'HashMap<(symbol, arity), Set<production-key>>. In-memory, rebuilt from C1.3 on session start.'),
  ('C3.1.3', (SELECT id FROM shadows WHERE code='C3.1'), 'rebuild-on-mutation', 3, 'C3', 'leaf',
   'Subscribes to C4.1 register-as-production events; appends to the relevant value-set.');

-- C3.2 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C3.2.1', (SELECT id FROM shadows WHERE code='C3.2'), 'type-equality-decision', 3, 'C3', 'research-frontier',
   'Definitional equality up to reduction in Gamma. Pattern-fragment higher-order unification. Open research at depth 4+.'),
  ('C3.2.2', (SELECT id FROM shadows WHERE code='C3.2'), 'substitution-composition', 3, 'C3', 'leaf',
   '(s1 . s2) x = s1 (s2 x). Standard, but content-addressed terms re-hash on substitution.'),
  ('C3.2.3', (SELECT id FROM shadows WHERE code='C3.2'), 'occurs-check', 3, 'C3', 'leaf',
   'Prevents ?m -> f(?m) cycles. O(subterm-count) via C1.2.3 queries.');

-- C3.3 children (leaves — textbook fixed-point)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C3.3.1', (SELECT id FROM shadows WHERE code='C3.3'), 'redex-detection', 3, 'C3', 'leaf',
   'Scans term tree for nodes whose head is a Gamma-production-key.'),
  ('C3.3.2', (SELECT id FROM shadows WHERE code='C3.3'), 'beta-reduction-step', 3, 'C3', 'leaf',
   'Replaces redex with production RHS, instantiated with the redex arguments.'),
  ('C3.3.3', (SELECT id FROM shadows WHERE code='C3.3'), 'normal-form-predicate', 3, 'C3', 'leaf',
   'True when no redex remains; equivalent to "term contains no cut sites".');

-- C4.1 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.1.1', (SELECT id FROM shadows WHERE code='C4.1'), 'candidate-rhs-extraction', 3, 'C4', 'leaf',
   'Parses proposed production into (name, formal-params, RHS-body, claimed-expansion).'),
  ('C4.1.2', (SELECT id FROM shadows WHERE code='C4.1'), 'expansion-typecheck', 3, 'C4', 'research-frontier',
   'Calls existing Agda typechecker on RHS == expansion under Gamma. Bootstrap is non-trivial when the typechecker is itself being routed.'),
  ('C4.1.3', (SELECT id FROM shadows WHERE code='C4.1'), 'registration-commit-reject', 3, 'C4', 'leaf',
   'On ok: emit Gamma-mutation event. On fail: emit error with failing equation pinned.');

-- C4.2 children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.2.1', (SELECT id FROM shadows WHERE code='C4.2'), 'chirality-pair-detector', 3, 'C4', 'productive',
   'Recognises Left.agda / Right.agda pairs; verifies both exist with mirror-structured contents. Maps to exchange rule.'),
  ('C4.2.2', (SELECT id FROM shadows WHERE code='C4.2'), 'section-then-lemma-detector', 3, 'C4', 'productive',
   'Recognises parametric-module layouts: Section/ + sibling lemmas sharing parameter set. Maps to contraction rule.'),
  ('C4.2.3', (SELECT id FROM shadows WHERE code='C4.2'), 'completion-suggester', 3, 'C4', 'productive',
   'On unpaired chirality file, emits diagnostic suggesting the mirror.');

-- C4.3 children (leaves)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.3.1', (SELECT id FROM shadows WHERE code='C4.3'), 'bound-var-collection', 3, 'C4', 'leaf',
   'From cong-trans f p q = ..., bound-vars = {f, p, q} plus implicit type vars.'),
  ('C4.3.2', (SELECT id FROM shadows WHERE code='C4.3'), 'rhs-traversal-predicate', 3, 'C4', 'leaf',
   'Walks RHS term tree; any variable not in bound set is a free escape and fails the check.');

-- ============================================================================
-- LAYER 4 — productive sub-sub-sub-shadows (depth-4 expansion)
-- ============================================================================

-- C1.2.2 (index-update-protocol) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.2.2.1', (SELECT id FROM shadows WHERE code='C1.2.2'), 'traversal-order', 4, 'C1', 'leaf',
   'Top-down BFS so a parent production exists before its child-reference edges are inserted (FK satisfaction).'),
  ('C1.2.2.2', (SELECT id FROM shadows WHERE code='C1.2.2'), 'batch-policy', 4, 'C1', 'leaf',
   'Single batched-insert per module-load transaction; size capped at backend optimal (few thousand rows for sqlite).'),
  ('C1.2.2.3', (SELECT id FROM shadows WHERE code='C1.2.2'), 'rollback-semantics', 4, 'C1', 'leaf',
   'On C4.1.2 fail, whole module transaction rolls back atomically; in-memory index replays from last snapshot.');

-- C1.2.3 (query-by-subterm-API) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.2.3.1', (SELECT id FROM shadows WHERE code='C1.2.3'), 'query-shape-normalization', 4, 'C1', 'leaf',
   'Maps two structurally equivalent queries to the same shape-key (alpha-renaming + implicit elision).'),
  ('C1.2.3.2', (SELECT id FROM shadows WHERE code='C1.2.3'), 'lazy-iterator', 4, 'C1', 'leaf',
   'Cursor-style iteration avoids materialising the full hit-set when the caller stops at the first match.'),
  ('C1.2.3.3', (SELECT id FROM shadows WHERE code='C1.2.3'), 'type-filter-pushdown', 4, 'C1', 'leaf',
   'Push the type constraint through to the backend WHERE clause rather than filtering in Haskell.');

-- C1.3.2 (transaction-boundaries) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.3.2.1', (SELECT id FROM shadows WHERE code='C1.3.2'), 'isolation-level', 4, 'C1', 'leaf',
   'Serializable. Multiple readers; single writer at a time; matches Agda single-process model.'),
  ('C1.3.2.2', (SELECT id FROM shadows WHERE code='C1.3.2'), 'read-snapshot-pinning', 4, 'C1', 'leaf',
   'Reads within a transaction observe the snapshot taken at begin-transaction; writes are buffered until commit.'),
  ('C1.3.2.3', (SELECT id FROM shadows WHERE code='C1.3.2'), 'abort-path', 4, 'C1', 'leaf',
   'On any C4.1 fail during transaction, entire module work rolls back; user sees one error.');

-- C1.3.3 (incremental-load-protocol) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C1.3.3.1', (SELECT id FROM shadows WHERE code='C1.3.3'), 'import-graph-walk', 4, 'C1', 'leaf',
   'Agda already does this; new piece is mapping each module to a snapshot-id rather than in-memory load.'),
  ('C1.3.3.2', (SELECT id FROM shadows WHERE code='C1.3.3'), 'snapshot-caching', 4, 'C1', 'leaf',
   'Module -> snapshot-id sidecar table; cache invalidated when module source-hash changes.'),
  ('C1.3.3.3', (SELECT id FROM shadows WHERE code='C1.3.3'), 'rebuild-on-cache-miss', 4, 'C1', 'leaf',
   'Re-elaborate the dependency, writing its Gamma-extensions to a new snapshot.');

-- C2.2.3 (cycle-detection) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C2.2.3.1', (SELECT id FROM shadows WHERE code='C2.2.3'), 'dfs-state-machine', 4, 'C2', 'leaf',
   'Standard per-node (visited, on-stack, low-link, index) tuple.'),
  ('C2.2.3.2', (SELECT id FROM shadows WHERE code='C2.2.3'), 'low-link-tracking', 4, 'C2', 'leaf',
   'Post-order update: low-link[v] := min(low-link[v], low-link[w]) for tree edges; min(..., index[w]) for back edges.'),
  ('C2.2.3.3', (SELECT id FROM shadows WHERE code='C2.2.3'), 'scc-enumeration', 4, 'C2', 'leaf',
   'When low-link[v] = index[v], pop the stack until v is popped; popped set is one SCC.');

-- C4.2.1 (chirality-pair-detector) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.2.1.1', (SELECT id FROM shadows WHERE code='C4.2.1'), 'name-pattern-matcher', 4, 'C4', 'leaf',
   'Regex over Left.agda/Right.agda or any user-defined pair convention; loaded from project config.'),
  ('C4.2.1.2', (SELECT id FROM shadows WHERE code='C4.2.1'), 'mirror-structure-verifier', 4, 'C4', 'leaf',
   'Compares ASTs up to a declared bijection on identifier names (the mirror map).'),
  ('C4.2.1.3', (SELECT id FROM shadows WHERE code='C4.2.1'), 'completeness-predicate', 4, 'C4', 'leaf',
   'A pair is complete iff (both files exist) AND (mirror-structure-verifier returns aligned).');

-- C4.2.2 (section-then-lemma-detector) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.2.2.1', (SELECT id FROM shadows WHERE code='C4.2.2'), 'directory-structure-matcher', 4, 'C4', 'leaf',
   'Cluster = one parametric Section module + >=2 sibling modules opening it with the same parameters.'),
  ('C4.2.2.2', (SELECT id FROM shadows WHERE code='C4.2.2'), 'parameter-set-extractor', 4, 'C4', 'leaf',
   'Parses section module parameter list into canonical form for comparison.'),
  ('C4.2.2.3', (SELECT id FROM shadows WHERE code='C4.2.2'), 'sibling-consistency-verifier', 4, 'C4', 'leaf',
   'Every sibling instantiates the section with the same parameter set; mismatches flag heterogeneity.');

-- C4.2.3 (completion-suggester) children
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C4.2.3.1', (SELECT id FROM shadows WHERE code='C4.2.3'), 'gap-detector', 4, 'C4', 'leaf',
   'Driven by C4.2.1 unpaired output; queue of gaps awaiting suggestion.'),
  ('C4.2.3.2', (SELECT id FROM shadows WHERE code='C4.2.3'), 'template-generator', 4, 'C4', 'leaf',
   'Apply inverse mirror-map to existing file ASTs identifiers; emit a new file template with ? holes for the proof body.'),
  ('C4.2.3.3', (SELECT id FROM shadows WHERE code='C4.2.3'), 'noise-suppression', 4, 'C4', 'leaf',
   'Cooldown table: suppress if user dismissed in last N sessions, or while file is being edited.');

-- ============================================================================
-- CROSS-CUTTING infrastructure shadows (X1-X4)
-- ============================================================================
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('X1', NULL, 'wire-format', 1, 'X', 'cross-cutting',
   'R(reach, transitions)',
   'Content-addressed key encoding: in-memory AST -> canonical bytes -> BLAKE3 -> backend blob.'),
  ('X2', NULL, 'concurrency-model', 1, 'X', 'cross-cutting',
   'R(reach, role-labeled-graphs)',
   'Single-writer-many-reader on Gamma-store; readers pin a snapshot-id; writers publish new snapshot on commit.'),
  ('X3', NULL, 'error-ux', 1, 'X', 'cross-cutting',
   'R(reach, transitions)',
   'On C4.1.2 fail, resolve content-key to source-span via C1.3 sidecar; emit LSP-compatible diagnostic.'),
  ('X4', NULL, 'parametric-module-handling', 1, 'X', 'cross-cutting',
   'R(reach, role-labeled-graphs)',
   'Module parameters as a tagged family of metas; productions with parametric LHS; instantiation substitutes across all of the module productions in one pass.');

-- X1 children (wire format)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('X1.1', (SELECT id FROM shadows WHERE code='X1'), 'canonical-encoder', 2, 'X', 'leaf',
   'Recursive AST walk producing a byte sequence; de-Bruijn binders, sorted implicit args, normalized whitespace.'),
  ('X1.2', (SELECT id FROM shadows WHERE code='X1'), 'hash-function', 2, 'X', 'leaf',
   'BLAKE3 (fast, parallelisable, 256-bit). Collision-resistance bounds memory-confusion attacks.'),
  ('X1.3', (SELECT id FROM shadows WHERE code='X1'), 'backend-marshaling', 2, 'X', 'leaf',
   'Raw 32-byte blobs in sqlite; key-prefix-friendly for LMDB. Identical bytes across backends.');

-- X2 children (concurrency)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('X2.1', (SELECT id FROM shadows WHERE code='X2'), 'writer-lock', 2, 'X', 'leaf',
   'Single-writer at a time; readers proceed against the most recently committed snapshot.'),
  ('X2.2', (SELECT id FROM shadows WHERE code='X2'), 'reader-snapshot-pinning', 2, 'X', 'leaf',
   'Each reader bound to a snapshot-id at session-start; never sees writes from other processes until re-attach.'),
  ('X2.3', (SELECT id FROM shadows WHERE code='X2'), 'handoff-protocol', 2, 'X', 'leaf',
   'On commit, writer publishes new snapshot-id; new readers default to it, existing readers keep their pinned id.');

-- X3 children (error UX)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('X3.1', (SELECT id FROM shadows WHERE code='X3'), 'error-context-parser', 2, 'X', 'leaf',
   'Reads typechecker existing error format; extracts the failing subterm reference.'),
  ('X3.2', (SELECT id FROM shadows WHERE code='X3'), 'key-to-source-span-resolver', 2, 'X', 'leaf',
   'Reverse lookup through C1.3 source_spans sidecar table (depth-4 schema extension).'),
  ('X3.3', (SELECT id FROM shadows WHERE code='X3'), 'diagnostic-emitter', 2, 'X', 'leaf',
   'Formats span + reason in LSP-compatible diagnostic form.');

-- X4 children (parametric module)
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('X4.1', (SELECT id FROM shadows WHERE code='X4'), 'abstract-parameter-representation', 2, 'X', 'leaf',
   'Module parameters as a fresh family of module-bound metas tagged as not-discharged-during-elaboration.'),
  ('X4.2', (SELECT id FROM shadows WHERE code='X4'), 'production-with-parametric-lhs', 2, 'X', 'leaf',
   'Each parametric module production has LHS containing module-parameter references; C3.1 keys on head-symbol but tracks parameter dependency.'),
  ('X4.3', (SELECT id FROM shadows WHERE code='X4'), 'instantiation-rule', 2, 'X', 'leaf',
   'When a downstream module applies the parametric module with concrete arguments, C3.3 substitutes concrete terms for parameter metas across all of the module productions in one pass.');

-- ============================================================================
-- CROSS-SHADOW ENTAILMENT EDGES
-- ============================================================================
INSERT INTO cross_entailments (from_shadow_id, to_shadow_id, claim) VALUES
  ((SELECT id FROM shadows WHERE code='C4.1.2'), (SELECT id FROM shadows WHERE code='C4'),
   'existing typechecker (axiomatic) ⊢ each extraction is cut-sound'),
  ((SELECT id FROM shadows WHERE code='C4.3.2'), (SELECT id FROM shadows WHERE code='C3.3'),
   'subformula-property check ⊢ cut-normalizer terminates'),
  ((SELECT id FROM shadows WHERE code='C2.2.3'), (SELECT id FROM shadows WHERE code='C3'),
   'cycle detection ⊢ C3 outer loop terminates'),
  ((SELECT id FROM shadows WHERE code='C1.2.2'), (SELECT id FROM shadows WHERE code='C1'),
   'transactional update + ACID persistence ⊢ Γ remains consistent'),
  ((SELECT id FROM shadows WHERE code='C3.1.3'), (SELECT id FROM shadows WHERE code='C2.3'),
   'index sync on mutation ⊢ left-rule queries return complete candidate set'),
  ((SELECT id FROM shadows WHERE code='C3.2.1'), (SELECT id FROM shadows WHERE code='C2.3'),
   'unifier soundness ⊢ every emitted cut-request is valid'),
  ((SELECT id FROM shadows WHERE code='X1.1'), (SELECT id FROM shadows WHERE code='C1.1'),
   'canonical encoder injectivity ⊢ structural-hash is well-defined for terms-up-to-α'),
  ((SELECT id FROM shadows WHERE code='X2.1'), (SELECT id FROM shadows WHERE code='C1.3.2'),
   'single-writer + snapshot-pinning ⊢ isolation enforceable across processes'),
  ((SELECT id FROM shadows WHERE code='X3.2'), (SELECT id FROM shadows WHERE code='C4.1.3'),
   'source-span sidecar maintained ⊢ error path is user-meaningful'),
  ((SELECT id FROM shadows WHERE code='X4.3'), (SELECT id FROM shadows WHERE code='C4.2.2'),
   'instantiation is substitution-respecting ⊢ section-then-lemma is observable');

-- ============================================================================
-- LIBRARY-DISCIPLINE CORRESPONDENCE
-- ============================================================================
INSERT INTO library_correspondence (shadow_id, library_discipline, notes) VALUES
  ((SELECT id FROM shadows WHERE code='C1'),       'Foundation.Eq cong-trans / sym-trans / trans-sym extractions',     'Each is a right-rule introduction registered in Γ during library-load.'),
  ((SELECT id FROM shadows WHERE code='C4.1.2'),   'agda --safe --without-K per-file typecheck',                       'This is literally cut-soundness verification at the library-discipline level.'),
  ((SELECT id FROM shadows WHERE code='C4.2.1'),   'chirality-pair-completeness rule',                                 'Solo *-right / *-left flags an incomplete exchange-rule symmetry.'),
  ((SELECT id FROM shadows WHERE code='C4.2.2'),   'section-then-lemma for parametric modules',                        'Contraction structural rule made explicit at the file boundary.'),
  ((SELECT id FROM shadows WHERE code='C4.3'),     'file-per-lemma boundary',                                          'Subformula-property check naturally aligns with single-lemma files.'),
  ((SELECT id FROM shadows WHERE code='C3.1'),     'agda_similarity --skeleton --typed-holes',                         'Read-only view of the production-index residue surface.'),
  ((SELECT id FROM shadows WHERE code='C2.2'),     'section-then-lemma topology hint',                                 'Parametric modules induce constraint-graph shape predictable from file layout.');

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================
-- Sanity-check counts (commented to keep populate.sql idempotent against a
-- fresh schema; uncomment if running with --bail):
-- SELECT 'shadows', COUNT(*) FROM shadows;
-- SELECT 'transitions', COUNT(*) FROM transitions;
-- SELECT 'role_edges', COUNT(*) FROM role_edges;
-- SELECT 'compositions', COUNT(*) FROM compositions;
-- SELECT 'entailments', COUNT(*) FROM entailments;
-- SELECT 'cross_entailments', COUNT(*) FROM cross_entailments;
-- SELECT 'library_correspondence', COUNT(*) FROM library_correspondence;
