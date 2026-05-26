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

-- ============================================================================
-- STRUCTURAL BACKFILL — transitions / role-edges / compositions / entailments
-- for every productive shadow whose depth-3 or depth-4 prose described them.
--
-- The initial INSERTs above carried the spine (1 root, layer-1 transitions,
-- root role-edges). The depth-3 and depth-4 expansion described state-
-- transitions and role-edges for many sub-shadows; without this section the
-- database is structurally incomplete with respect to the prose sketch.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Transitions for depth-3 productive shadows.
-- ----------------------------------------------------------------------------

-- C1.1 structural-hash (leaf, but has explicit transition sequence)
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1.1'), 1, 'term-AST',              'canonical-encode(de-Bruijn, sort-implicit-args)', 'no-name-capture',           'canonical-byte-sequence'),
  ((SELECT id FROM shadows WHERE code='C1.1'), 2, 'canonical-byte-sequence','hash(BLAKE3 or xxhash3)',                         'hash-fn-collision-bound-known','256-bit content-key');

-- C2.1 meta-allocator
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C2.1'), 1, '(Gamma-snapshot, Delta)','gensym-meta-id(counter++)',           'counter-monotone',                                  'fresh-meta-id'),
  ((SELECT id FROM shadows WHERE code='C2.1'), 2, 'fresh-meta-id',          'record-scope(meta-id, type-ctx, src-loc)','type-ctx-references-only-Gamma-or-prior-metas','Delta union {meta-id -> open-with-type-ctx}');

-- C2.3 left-rule applicator
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C2.3'), 1, 'focused-meta(id, constraint)','extract-RHS-shape-from-constraint','constraint-has-canonical-RHS-form','shape-key'),
  ((SELECT id FROM shadows WHERE code='C2.3'), 2, 'shape-key',                'query-C3.1-index(shape-key)',          'index-current',                  'candidate-production-set'),
  ((SELECT id FROM shadows WHERE code='C2.3'), 3, 'candidate-production-set', 'filter-by-type-unification(candidates, constraint)','each-candidate-attempted','viable-production OR no-match (defer)'),
  ((SELECT id FROM shadows WHERE code='C2.3'), 4, 'viable-production',        'emit-cut-request(C3, viable, meta-id)','request-well-formed',             'cut-request-queued');

-- C3.3 cut-normalizer
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C3.3'), 1, 'term-with-cuts',          'find-leftmost-outermost-redex',         'redex-detected OR normal-form',         'redex-position'),
  ((SELECT id FROM shadows WHERE code='C3.3'), 2, 'redex-position',          'substitute(production-RHS-for-LHS)',    'substitution-from-C3.2.2',              'term-after-one-reduction'),
  ((SELECT id FROM shadows WHERE code='C3.3'), 3, 'term-after-one-reduction','repeat-until-no-redex',                 'subformula-property-guarantees-termination','normal-form');

-- C4.1 cut-soundness check
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4.1'), 1, 'proposed-extraction(name, RHS, expansion)','extract-RHS-and-expansion',  'both-syntactically-well-formed','(RHS-term, expansion-term)'),
  ((SELECT id FROM shadows WHERE code='C4.1'), 2, '(RHS-term, expansion-term)','invoke-typechecker(RHS == expansion in Gamma)','Gamma-snapshot-pinned','judgement (ok or fail)'),
  ((SELECT id FROM shadows WHERE code='C4.1'), 3, 'judgement',                'commit-or-reject',                       'no-partial-Gamma-mutation',     'Gamma-extended OR Gamma-unchanged');

-- C4.3 subformula-property check
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4.3'), 1, 'candidate-production(LHS, RHS)','collect-bound-vars(LHS)',             'LHS-is-applicative-spine',    'bound-var-set'),
  ((SELECT id FROM shadows WHERE code='C4.3'), 2, 'bound-var-set',                  'traverse-RHS-collecting-free-vars',   'RHS-is-Term',                 'free-var-set'),
  ((SELECT id FROM shadows WHERE code='C4.3'), 3, 'free-var-set',                   'check-subset(free-vars subset bound-vars)','predicate-decidable',    'ok (subformula-local) OR fail (escape-detected)');

-- ----------------------------------------------------------------------------
-- Transitions for depth-4 productive shadows.
-- ----------------------------------------------------------------------------

-- C1.2.2 index-update-protocol
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1.2.2'), 1, 'ingest-event(production-key, body-AST)','walk-body-AST(top-down-BFS)','parents-visited-before-children','pending-insert-set'),
  ((SELECT id FROM shadows WHERE code='C1.2.2'), 2, 'pending-insert-set',                    'batch-into-single-transaction','batch-size <= DB-page-budget','pending-transaction'),
  ((SELECT id FROM shadows WHERE code='C1.2.2'), 3, 'pending-transaction',                   'commit-or-rollback-on-C4-decision','C4.1.2-result-bound',    'index-updated OR index-untouched');

-- C1.2.3 query-by-subterm-API
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1.2.3'), 1, 'query(content-key, optional-type-filter)','normalize-query-shape',            'shape-canonical-form',          'canonical-shape-key'),
  ((SELECT id FROM shadows WHERE code='C1.2.3'), 2, 'canonical-shape-key',                     'lookup-in-index(shape-key)',       'index-current',                  'candidate-key-set'),
  ((SELECT id FROM shadows WHERE code='C1.2.3'), 3, 'candidate-key-set',                       'push-down-type-filter-if-present', 'filter-decidable-against-index-metadata','filtered-candidate-set (lazy iterator)');

-- C1.3.2 transaction-boundaries
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1.3.2'), 1, 'module-load-request',  'begin-transaction(isolation = serializable)','no-other-writer-in-flight OR rejected','in-flight-transaction'),
  ((SELECT id FROM shadows WHERE code='C1.3.2'), 2, 'in-flight-transaction','execute-all-module-mutations',              'each-passes-C4',                'pending-commit'),
  ((SELECT id FROM shadows WHERE code='C1.3.2'), 3, 'pending-commit',       'commit-or-abort',                            'C4-aggregate-result',           'persistent-Gamma-updated OR unchanged');

-- C1.3.3 incremental-load-protocol
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C1.3.3'), 1, 'agda-invocation(target-module)','topological-walk-of-imports','import-DAG-acyclic',            'ordered-dependency-list'),
  ((SELECT id FROM shadows WHERE code='C1.3.3'), 2, 'ordered-dependency-list',       'for-each-dep: load-snapshot-or-rebuild','snapshot-id-cached', 'Gamma-snapshot-ready-for-target'),
  ((SELECT id FROM shadows WHERE code='C1.3.3'), 3, 'Gamma-snapshot-ready-for-target','begin-transaction-for-target', 'C1.3.2-pre',                    'ready-for-elaboration');

-- C2.2.3 cycle-detection (Tarjan SCC)
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C2.2.3'), 1, 'constraint-graph-G',           'DFS-walk(G, push-to-stack-on-visit)','graph-has-finite-nodes',     'nodes-with-low-link-annotations'),
  ((SELECT id FROM shadows WHERE code='C2.2.3'), 2, 'nodes-with-low-link-annotations','emit-SCC-on-low-link-equals-id',     'low-link-computed',           'SCC-partition-of-G'),
  ((SELECT id FROM shadows WHERE code='C2.2.3'), 3, 'SCC-partition-of-G',           'flag-non-trivial-SCCs-as-cycles',    '|SCC| >= 2 or self-loop',     'cycle-set');

-- C4.2.1 chirality-pair-detector
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4.2.1'), 1, 'file-registered(path, AST)',     'match-name-pattern',                'conventions-loaded',         'name-match(side = Left | Right | ...)'),
  ((SELECT id FROM shadows WHERE code='C4.2.1'), 2, 'name-match',                     'look-for-mirror(opposite-side)',    'filesystem-readable',        'mirror-found OR mirror-absent'),
  ((SELECT id FROM shadows WHERE code='C4.2.1'), 3, 'mirror-found',                   'verify-structural-mirror',          'mirror-AST-loaded',          'paired-and-verified OR divergent');

-- C4.2.2 section-then-lemma-detector
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4.2.2'), 1, 'directory-registered(path)',     'scan-for-section-module',           'convention-loaded',          'section-module-found OR no-section'),
  ((SELECT id FROM shadows WHERE code='C4.2.2'), 2, 'section-module-found',           'extract-parametric-signature',      'section-is-parametric',      'parameter-set-S'),
  ((SELECT id FROM shadows WHERE code='C4.2.2'), 3, 'parameter-set-S',                'verify-siblings-import-section(S)', 'siblings-enumerable',        'section-bundle-verified OR siblings-disagree');

-- C4.2.3 completion-suggester
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C4.2.3'), 1, 'chirality-detector-output(unpaired)','check-cooldown(file)',           'cooldown-table-readable',    'not-in-cooldown OR in-cooldown'),
  ((SELECT id FROM shadows WHERE code='C4.2.3'), 2, 'not-in-cooldown',                  'generate-mirror-template',         'template-engine-loaded',     'template-text'),
  ((SELECT id FROM shadows WHERE code='C4.2.3'), 3, 'template-text',                    'emit-suggestion(diagnostic)',      'diagnostic-channel-open',    'suggestion-shown OR suppressed');

-- ----------------------------------------------------------------------------
-- Transitions for cross-cutting infrastructure (X1, X3 are R(reach, trans)).
-- ----------------------------------------------------------------------------

-- X1 wire-format
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='X1'), 1, 'in-memory-term (Haskell ADT)','canonical-encode(de-Bruijn-CBOR)',  'no-name-capture; deterministic-byte-order','CBOR-byte-sequence'),
  ((SELECT id FROM shadows WHERE code='X1'), 2, 'CBOR-byte-sequence',           'hash(BLAKE3, 256-bit output)',       'hash-fn-fixed',                   '32-byte content-key'),
  ((SELECT id FROM shadows WHERE code='X1'), 3, '32-byte content-key',          'marshal-to-backend(sqlite-blob or LMDB-key)','byte-sequence-faithful',  'persistent-key');

-- X3 error-ux
INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='X3'), 1, 'C4.1.2-fail from typechecker', 'extract-failing-subterm-pointer(error-context)','error-format-stable','subterm-key + context'),
  ((SELECT id FROM shadows WHERE code='X3'), 2, 'subterm-key + context',        'resolve-key-to-source-span(via C1.3)','source-map-cached',           'source-span(file, line, column-range)'),
  ((SELECT id FROM shadows WHERE code='X3'), 3, 'source-span(file, line, column-range)','format-as-diagnostic(span + reason)','diagnostic-channel-format-known','user-facing-error');

-- ----------------------------------------------------------------------------
-- Role-edges for R(reach, role-labeled-graphs) shadows.
-- ----------------------------------------------------------------------------

-- C1.2 production-ref-index PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='C1.2'), 'index', ':nodes',    'n', 'Gamma-production-keys union subterm-keys'),
  ((SELECT id FROM shadows WHERE code='C1.2'), 'index', ':edges',    'e', 'contains-as-subterm'),
  ((SELECT id FROM shadows WHERE code='C1.2'), 'index', ':supports', 'q', 'query-by-subterm-key');

-- C2.2 constraint-graph PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='C2.2'), 'Delta-graph', ':nodes',  'n', 'meta-id-with-constraint-shape'),
  ((SELECT id FROM shadows WHERE code='C2.2'), 'Delta-graph', ':edges',  'e', 'depends-on-resolution-of'),
  ((SELECT id FROM shadows WHERE code='C2.2'), 'Delta-graph', ':cycles', 'c', 'require-fixed-point-via-C3.3');

-- C3.1 production-index PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='C3.1'), 'prod-index', ':keys',       'k', 'RHS-head-symbol x arity'),
  ((SELECT id FROM shadows WHERE code='C3.1'), 'prod-index', ':values',     'v', 'set-of-production-keys'),
  ((SELECT id FROM shadows WHERE code='C3.1'), 'prod-index', ':rebuild-on', 'r', 'Gamma-extension-event from C4');

-- C4.2 structural-rule-discipline PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='C4.2'), 'structural-discipline', ':exchange-rule',    'er', 'chirality-pair-completeness'),
  ((SELECT id FROM shadows WHERE code='C4.2'), 'structural-discipline', ':contraction-rule', 'cr', 'section-then-lemma'),
  ((SELECT id FROM shadows WHERE code='C4.2'), 'structural-discipline', ':weakening-rule',   'wr', 'file-per-lemma');

-- X2 concurrency-model PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='X2'), 'concurrency', ':writer-lock',    'wl', 'cooperative-mutex-on-Gamma-store'),
  ((SELECT id FROM shadows WHERE code='X2'), 'concurrency', ':reader-handles', 'rh', 'snapshot-id-pinned-readers'),
  ((SELECT id FROM shadows WHERE code='X2'), 'concurrency', ':handoff-event',  'he', 'commit-publishes-new-snapshot-id');

-- X4 parametric-module-handling PENMAN
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='X4'), 'param-module', ':module-params',      'mp',  'abstract-parameter-set'),
  ((SELECT id FROM shadows WHERE code='X4'), 'param-module', ':module-productions', 'mpr', 'productions-with-mp-free-vars'),
  ((SELECT id FROM shadows WHERE code='X4'), 'param-module', ':instantiation-rule', 'ir',  'closed-application-instantiates-all-productions');

-- ----------------------------------------------------------------------------
-- Compositions for every productive and cross-cutting shadow.
-- ----------------------------------------------------------------------------

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C1.2'),
   'ingest-definition invokes update (C1.2.2); search-Gamma (C3.1) invokes query (C1.2.3); both operate over the edge representation (C1.2.1).'),
  ((SELECT id FROM shadows WHERE code='C1.3'),
   'C1.3.3 sequences C1.3.2; C1.3.2 wraps writes to C1.3.1.'),
  ((SELECT id FROM shadows WHERE code='C2.1'),
   'C2.1.2 produces the key; C2.1.1 records the value; the pair becomes the entry in Delta.'),
  ((SELECT id FROM shadows WHERE code='C2.2'),
   'Nodes and edges added incrementally as C2.1 allocates metas and C2.3 poses dependent constraints; C2.2.3 invoked before C3 attempts discharge.'),
  ((SELECT id FROM shadows WHERE code='C2.3'),
   'Pipeline: extract -> query -> filter -> emit. Each step is total (returns either an answer or "defer this meta to later").'),
  ((SELECT id FROM shadows WHERE code='C3.1'),
   'C3.1.3 maintains C3.1.2 as C4.1 mutates Gamma; C2.3 and the search loop in C3 query C3.1.2 via a thin API.'),
  ((SELECT id FROM shadows WHERE code='C3.2'),
   'unify invokes occurs-check first (C3.2.3), then attempts type-equality (C3.2.1), then composes the resulting substitution (C3.2.2).'),
  ((SELECT id FROM shadows WHERE code='C3.3'),
   'Fixed-point loop: detect -> reduce -> re-detect until normal-form holds.'),
  ((SELECT id FROM shadows WHERE code='C4.1'),
   'Pipeline: extract -> typecheck -> commit. Each step is total; failure is communicated, not silent.'),
  ((SELECT id FROM shadows WHERE code='C4.2'),
   'Each new file passes through C4.2.1 then C4.2.2; suggestions emitted by C4.2.3 are advisory and do not block registration.'),
  ((SELECT id FROM shadows WHERE code='C4.3'),
   'Sequential: collect bounds, then traverse RHS, then test subset.'),
  ((SELECT id FROM shadows WHERE code='C1.2.2'),
   'Traversal generates inserts; batching collects them; transaction guarantees atomicity.'),
  ((SELECT id FROM shadows WHERE code='C1.2.3'),
   'Sequential: normalize the query shape, lookup, then optionally push down a type filter; result is a lazy iterator.'),
  ((SELECT id FROM shadows WHERE code='C1.3.2'),
   'begin -> execute-mutations -> commit-or-abort. All mutations within one transaction; abort path resets in-flight changes.'),
  ((SELECT id FROM shadows WHERE code='C1.3.3'),
   'Topological walk of imports identifies dependencies; per-dep snapshot caching avoids redundant rebuild; fresh transaction frames the target module.'),
  ((SELECT id FROM shadows WHERE code='C2.2.3'),
   'Tarjan SCC: DFS with low-link tracking; on low-link == index, pop stack to enumerate one SCC.'),
  ((SELECT id FROM shadows WHERE code='C4.2.1'),
   'Sequential: pattern-match the file name; look for the opposite-side mirror file; verify structural alignment via the mirror map.'),
  ((SELECT id FROM shadows WHERE code='C4.2.2'),
   'Sequential: identify the section module in the directory; extract its parameter set; verify each sibling lemma imports the section with matching parameters.'),
  ((SELECT id FROM shadows WHERE code='C4.2.3'),
   'gap-detector feeds template-generator feeds emitter; noise-suppression sits above the pipeline as a guard.'),
  ((SELECT id FROM shadows WHERE code='X1'),
   'Sequential: canonical encode, then hash, then marshal to backend storage format.'),
  ((SELECT id FROM shadows WHERE code='X2'),
   'Writer-lock serializes mutators; readers pin to a snapshot at session-start; handoff event publishes a new snapshot-id on commit.'),
  ((SELECT id FROM shadows WHERE code='X3'),
   'Sequential: parse the typechecker error, resolve content-key to source-span via sidecar, format as LSP diagnostic.'),
  ((SELECT id FROM shadows WHERE code='X4'),
   'Module parameters are tagged metas; each parametric production has parameter-free-vars in its LHS; instantiation substitutes once across all productions in the module.');

-- ----------------------------------------------------------------------------
-- Entailments for every productive and cross-cutting shadow.
-- ----------------------------------------------------------------------------

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C1.2'),
   'C1.2.2 transactional AND C1.2.3 reads consistent snapshot',
   'queries observe a referentially closed index'),
  ((SELECT id FROM shadows WHERE code='C1.3'),
   'transactions ACID (delegated to backend) AND import-order topological',
   'every C1.3.3 load sees a consistent point-in-time Gamma-snapshot'),
  ((SELECT id FROM shadows WHERE code='C2.1'),
   'counter monotone within a session',
   'meta-ids pairwise distinct; Delta well-defined as finite map'),
  ((SELECT id FROM shadows WHERE code='C2.2'),
   'graph acyclic OR cycles handled by C3.3 fixed-point',
   'topological-order discharge terminates'),
  ((SELECT id FROM shadows WHERE code='C2.3'),
   'index-query soundness (C1.2.3) AND unifier soundness (C3.2)',
   'every emitted cut-request is valid; applying preserves Gamma-Delta-consistency'),
  ((SELECT id FROM shadows WHERE code='C3.1'),
   'every Gamma-mutation triggers a C3.1.3 update',
   'index stays consistent with Gamma; queries return complete candidate set'),
  ((SELECT id FROM shadows WHERE code='C3.2'),
   'C3.2.1 sound + complete for chosen unification fragment AND C3.2.3 rejects occurs-violations',
   'unify returns most-general unifier when one exists, none otherwise'),
  ((SELECT id FROM shadows WHERE code='C3.3'),
   'subformula property (C4.3) holds for every production in Gamma',
   'each reduction strictly decreases a well-founded measure; loop terminates; unique normal form'),
  ((SELECT id FROM shadows WHERE code='C4.1'),
   'Agda existing typechecker is sound (axiom)',
   'OK from C4.1.2 implies extraction is cut-sound; Gamma remains consistent after registration'),
  ((SELECT id FROM shadows WHERE code='C4.2'),
   'chirality pairs complete AND section-then-lemma respected',
   'Gamma admits sequent-calculus structural rules; C3 search invariant under hypothesis-reordering and duplicate-elimination'),
  ((SELECT id FROM shadows WHERE code='C4.3'),
   'predicate holds (free-vars subset bound-vars)',
   'every reduction step strictly decreases a well-founded measure; cut-elimination terminates'),
  ((SELECT id FROM shadows WHERE code='C1.2.2'),
   'atomicity of C1.2.2.3',
   'no partial Gamma-mutation on extraction-soundness failure; Gamma remains consistent grammar'),
  ((SELECT id FROM shadows WHERE code='C1.2.3'),
   'lazy iteration AND filter pushdown',
   'peak memory for a query is O(answer-prefix-the-caller-consumes), not O(total-matches)'),
  ((SELECT id FROM shadows WHERE code='C1.3.2'),
   'serializability',
   'Gamma history is a linear sequence of consistent snapshots; every read returns a valid grammar state'),
  ((SELECT id FROM shadows WHERE code='C1.3.3'),
   'snapshot-caching sound (same source -> same snapshot-id, content-addressed)',
   'incremental load returns the same Gamma as a from-scratch load; elaboration deterministic across cache states'),
  ((SELECT id FROM shadows WHERE code='C2.2.3'),
   'Tarjan correctness theorem (textbook)',
   'emitted partition is exactly the set of SCCs of G; C3.3 invocations target true cycles'),
  ((SELECT id FROM shadows WHERE code='C4.2.1'),
   'completeness predicate holds for a pair',
   'Gamma chirality structural rule (exchange between the pair) is sound at file level; C3 search can permute paired productions'),
  ((SELECT id FROM shadows WHERE code='C4.2.2'),
   'verified section-then-lemma cluster',
   'Gamma admits contraction; C3.1 can share parameter representation across the lemma productions, reducing index size'),
  ((SELECT id FROM shadows WHERE code='C4.2.3'),
   'gap-detection completeness (C4.2.1) AND template-correctness (mirror-map injectivity)',
   'every emitted suggestion is a valid mirror candidate'),
  ((SELECT id FROM shadows WHERE code='X1'),
   'canonical encoder injectivity (up to alpha) AND hash collision-resistance',
   'content-key uniquely identifies the structural term modulo intended equivalence'),
  ((SELECT id FROM shadows WHERE code='X2'),
   'single-writer AND snapshot-pinning',
   'no read-write conflicts; each reader observes a consistent Gamma throughout its session'),
  ((SELECT id FROM shadows WHERE code='X3'),
   'C1.3 source-span sidecar maintained',
   'every error points to user-visible source; error UX no worse than current Agda'),
  ((SELECT id FROM shadows WHERE code='X4'),
   'instantiation substitution-respecting (delegated to C3.2.2)',
   'parametric modules sound across instantiation; section-then-lemma discipline mechanically supported');

-- ============================================================================
-- Γ-INSTANCE DATA — actual productions registered in the substrate library
-- via extraction commits. Each row is a right-rule introduction by the
-- sketch's terms; production_usages records left-rule call sites.
-- ============================================================================

INSERT INTO productions (code, module_path, lhs_signature, rhs_expansion, status, extraction_commit, notes) VALUES
  ('cong-trans', 'Substrate.Foundation.Eq',
   '(f : A → B) {x y : A} {z : B} → x ≡ y → f y ≡ z → f x ≡ z',
   'trans (cong f p) q',
   'extracted', '894cd8a',
   'Naturality-step combinator. Highest-frequency Eq composition (338 sites at extraction time).'),
  ('sym-trans', 'Substrate.Foundation.Eq',
   '{x y z : A} → x ≡ y → x ≡ z → y ≡ z',
   'trans (sym p) q',
   'extracted', '894cd8a',
   'Shared-source triangle. Second-highest frequency (72 sites at extraction time).'),
  ('trans-sym', 'Substrate.Foundation.Eq',
   '{x y z : A} → x ≡ y → z ≡ y → x ≡ z',
   'trans p (sym q)',
   'extracted', '894cd8a',
   'Shared-target triangle. Third-highest frequency (81 sites at extraction time).'),
  ('pred-at-i→kernel-at-i', 'Substrate.Algebra.F2.Linear.KernelPredBridge',
   '(S : Linear n p) (w : Vector n) (i : Fin p) {pi-of-w : F₂} → lookup (apply S w) i ≡ pi-of-w → pi-of-w ≡ 𝟘 → lookup (apply S w) i ≡ lookup (𝟎ⱽ {p}) i',
   'trans-sym (trans sl pi) (lookup-𝟎 i)',
   'extracted', '30eb9b7',
   'Per-index bridge: predicate-i-clause + selector-lookup-i → kernel-at-i. Composes with ≡-from-lookup at call site. Surfaced via typed-holes on ChiralityAxis ↔ V4Plane after the Foundation.Eq trio arc closed.'),
  ('kernel-at-i→pred-at-i', 'Substrate.Algebra.F2.Linear.KernelPredBridge',
   '(S : Linear n p) (w : Vector n) (i : Fin p) {pi-of-w : F₂} → lookup (apply S w) i ≡ pi-of-w → apply S w ≡ 𝟎ⱽ → pi-of-w ≡ 𝟘',
   'sym-trans sl (cong-trans (λ x → lookup x i) ker (lookup-𝟎 i))',
   'extracted', '30eb9b7',
   'Per-index bridge: in-kernel + selector-lookup-i → predicate-i-clause. Companion to pred-at-i→kernel-at-i.'),
  ('cubed-orbit-walk', 'Substrate.Algebra.F2.HodgeDim3.MetricGauge.CoxeterRelations.CubedOrbitWalk',
   '(s₁ s₂ : Linear n n) (a₀ : Vector n) {a₁..a₆ : Vector n} → 6 step-equations → apply ((s₁ ∘L s₂)³) a₀ ≡ a₆',
   '5-call cong-trans chain with 6 swap-lemma slots',
   'extracted', '93e2764',
   'Parametric Coxeter (s₁∘s₂)³ orbit-walk witness. Extracted under fine-grained-over-coarse discipline. 3 sites: S1S2CubedOnE0/E1/E2, each collapses 7-line body to 1-line call.');

-- ----------------------------------------------------------------------------
-- Per-file occurrence counts as observed at commit 6664ea5 (structural-coverage
-- backfill). Counts include the import line; subtract 1 for raw call-site count.
-- ----------------------------------------------------------------------------

-- cong-trans usages
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Cyclic/Lookup0.agda', 3, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Cyclic/Lookup1.agda', 5, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Cyclic/Lookup2.agda', 4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Swap/Lookup0.agda',   5, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Swap/Lookup1.agda',   3, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridgeAlternatives/Swap/Lookup2.agda',   4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/S4-Iso/Embedding.agda',                                        7, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/S4-Iso/ExtractCorrect.agda',                                   2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Stab-S3.agda',                                                 2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/V4-Coxeter.agda',                                              2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/V4-Embedding.agda',                                            4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/V4/Axioms/Lifted.agda',                                        4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/V4/FourProduct.agda',                                          3, '6664ea5');

-- sym-trans usages
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/S4-Iso/Embedding.agda',           3, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/S4-Iso/ExtractCorrect.agda',      2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Stab-S3.agda',                    3, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Subgroup.agda',                   4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/V4-Coxeter.agda',                 4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/V4-Embedding.agda',               2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/V4/Axioms/Lifted.agda',           4, '6664ea5'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/V4/FourProduct.agda',             3, '6664ea5');

-- trans-sym usages
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/Coxeter/Core/NormalizeAppend/Left.agda',  2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/Coxeter/Core/NormalizeAppend/Right.agda', 2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/Coxeter/Core/NormalizeCong/Left.agda',    2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/Coxeter/Core/NormalizeCong/Right.agda',   2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/S4-Iso/ExtractCorrect.agda',              31, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/S4-Iso/ForwardHom.agda',                  2, '6664ea5'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Groups/Stab-S3.agda',                            2, '6664ea5');

-- ----------------------------------------------------------------------------
-- Link the productions table back to C1 (Γ-store): the table IS C1 at the
-- library-discipline level for the substrate's recent extractions.
-- ----------------------------------------------------------------------------

INSERT INTO library_correspondence (shadow_id, library_discipline, notes) VALUES
  ((SELECT id FROM shadows WHERE code='C1'),
   'productions table',
   'The productions table is a literal Γ-store instance for the substrate library; each row is a right-rule introduction.'),
  ((SELECT id FROM shadows WHERE code='C1.2'),
   'production_usages table',
   'production_usages is a forward-direction instance of the production-ref index: production -> set of containing files.'),
  ((SELECT id FROM shadows WHERE code='C4.2.3'),
   'extraction_candidates table',
   'extraction_candidates is a literal gap-detector instance of the completion-suggester shadow: produces left-rule-applicable sites awaiting migration.');

-- ============================================================================
-- EXTRACTION-CANDIDATE DATA — discovered gap sites where the trio could land.
-- Counts taken at commit a9ebf0e via grep -c against the relevant raw pattern.
-- ============================================================================

-- cong-trans candidates: files with 3+ unmigrated `trans (cong` sites.
INSERT INTO extraction_candidates (production_id, file_path, raw_pattern, occurrence_count, status, discovered_at_commit, notes) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Linear/FromImages.agda',                                  'trans (cong', 12, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort). 10 real cong-trans sites; 12 reported count included 1 cong₂ and 1 sym(cong...) false positives.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda',                              'trans (cong', 11, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridge.agda',                           'trans (cong', 11, 'done', 'a9ebf0e', 'Migrated in 63200fe (densest single-file remaining). 11 real sites across 4 round-trip lemmas; no false positives.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/Q/AsModule.agda',                                            'trans (cong', 10, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure). 8 real sites; 2 cong₂ false positives.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/SymBilinForm/Bilinearity.agda',                           'trans (cong', 10, 'done', 'a9ebf0e', 'Migrated in c0c6983 (SymBilinForm cohort). 9 real sites; 1 cong₂ false positive.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/StabiliserClosure.agda',            'trans (cong', 10, 'done', 'a9ebf0e', 'Migrated in b2050d4 (HodgeDim3/MetricGauge cohort). 4 stabiliser-closure lemmas, same 3-line template.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/Orthogonality.agda',                              'trans (cong',  6, 'done', 'a9ebf0e', 'Migrated in bddf677 (Geometry/HodgeDim3 cohort). 7 real sites (off-by-one in gap-detector per-line count).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Foundation/Nat/Properties/Mul.agda',                                 'trans (cong',  6, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Vector.agda',                                             'trans (cong',  6, 'done', 'a9ebf0e', 'Migrated in bddf677 (Algebra/F2 cohort). 5 real sites; 1 cong₂ false positive in +ⱽ-self-inverse chain.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/Stabiliser.agda',                   'trans (cong',  6, 'done', 'a9ebf0e', 'Migrated in b2050d4. 6 sites: 3 per s₁/s₂ generator.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Coxeter/Cyclic/InvCanonical/InvInv.agda',                     'trans (cong',  5, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure). All 5 real cong-trans sites.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/ShiftHom.agda','trans (cong', 5, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/SymBilinForm/CongruenceCompose.agda',                     'trans (cong',  5, 'done', 'a9ebf0e', 'Migrated in c0c6983 (SymBilinForm cohort). 4 real sites; 1 cong₂ false positive.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE2.agda','trans (cong', 5, 'done', 'a9ebf0e', 'Migrated in b2050d4. 3-cycle Coxeter braid relation on e₂.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE1.agda','trans (cong', 5, 'done', 'a9ebf0e', 'Migrated in b2050d4. 3-cycle Coxeter braid relation on e₁.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE0.agda','trans (cong', 5, 'done', 'a9ebf0e', 'Migrated in b2050d4. 3-cycle Coxeter braid relation on e₀.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CongruenceBridge.agda',             'trans (cong',  5, 'rejected', 'a9ebf0e', 'All 5 reported sites are gap-detector false positives: trans (congruence-act-…) / trans (congruence-compose-…) identifier-prefix matches the regex `trans (cong`. File has 0 real cong-trans patterns. Discovered in b2050d4.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Symmetric.agda',                                              'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/S4-Iso/Foundation.agda',                                      'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Coxeter/GroupAdapter.agda',                                   'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/V4Plane.agda',                                    'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in bddf677 (Geometry/HodgeDim3 cohort). Also picked up 1 sym-trans opportunistically.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivector.agda',              'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure). 4 sites across 2 round-trip lemmas.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/LiveS4Bijection/Reverse.agda',         'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure). 4 sites in the live-σ-live-roundtrip proof tree.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Category/Coalgebra/FiniteOrder.agda',                                'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in b0fdf7b (cong-trans arc closure). 4 sites across iterate-at-fixed-point, HasOrder-multiple, iterate-iterate, HasOrder-iterate.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Vector/Universal.agda',                                   'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort); 2 real cong-trans sites, 2 cong₂ false positives.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/Bivector-F2Graded.agda',                        'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in bddf677 (Algebra/F2 cohort).'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/AsModule.agda',                                           'trans (cong',  4, 'done', 'a9ebf0e', 'Migrated in bddf677 (Algebra/F2 cohort). 3 real sites; 1 cong₂ false positive.'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Foundation/Eq.agda',                                                 'trans (cong',  2, 'rejected', 'a9ebf0e', 'These two sites are the cong-trans definition itself.');

-- sym-trans candidates: all unmigrated sites count >= 2, with Hedberg flagged.
INSERT INTO extraction_candidates (production_id, file_path, raw_pattern, occurrence_count, status, discovered_at_commit, notes) VALUES
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Foundation/Hedberg.agda',                                            'trans (sym', 12, 'rejected', 'a9ebf0e', 'Local trans-sym-id definition uses trans (sym ...); not a substrate.Foundation.Eq.sym-trans candidate.'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Symmetric.agda',                                              'trans (sym',  3, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/ShiftHom.agda','trans (sym', 3, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Coxeter/GroupAdapter.agda',                                   'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda',                              'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Foundation/Nat/Properties/Mul.agda',                                 'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Cocycles/F2CubedPuncturing.agda',                                    'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 4b49216 (sym-trans arc closure). Plus 3 opportunistic cong-trans sites also picked up.'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Algebra/F2/Vector/Universal.agda',                                   'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort); 1 real sym-trans site, 1 sym-sum-cong identifier false positive.'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Algebra/F2/Linear/FromImages.agda',                                  'trans (sym',  2, 'done', 'a9ebf0e', 'Migrated in 136c901 (multi-production cohort).');

-- trans-sym candidates: both migrated in commit f429d6f, closing the trans-sym arc.
INSERT INTO extraction_candidates (production_id, file_path, raw_pattern, occurrence_count, status, discovered_at_commit, notes) VALUES
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Cocycles/V4Signature/S4Iso/Cases.agda',     'trans X (sym Y)', 18, 'done', 'a9ebf0e', 'Densest unmigrated trans-sym site at discovery (18 occurrences across 6 case-functions); migrated in f429d6f.'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Cocycles/V4Signature/S4Iso/Roundtrips.agda', 'trans X (sym Y)',  7, 'done', 'a9ebf0e', 'Migrated in f429d6f. 3 cong-trans sites at lines 64/88/94 remain unmigrated (separate arc).');

-- trans-sym usages added by the migration commit f429d6f.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Cocycles/V4Signature/S4Iso/Cases.agda',     19, 'f429d6f'),
  ((SELECT id FROM productions WHERE code='trans-sym'), 'Substrate/Cocycles/V4Signature/S4Iso/Roundtrips.agda', 8, 'f429d6f');

-- Multi-production cohort usages added by commit 136c901 (7 files × 2 productions = 14 rows).
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Foundation/Nat/Properties/Mul.agda',                                  7, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Coxeter/GroupAdapter.agda',                                    5, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Symmetric.agda',                                               5, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Vector/Universal.agda',                                    3, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/ShiftHom.agda', 6, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda',                              12, '136c901'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Linear/FromImages.agda',                                  12, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Foundation/Nat/Properties/Mul.agda',                                  3, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Coxeter/GroupAdapter.agda',                                    3, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Groups/Symmetric.agda',                                               4, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Algebra/F2/Vector/Universal.agda',                                    2, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivectorAffine/ShiftHom.agda', 4, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda',                               3, '136c901'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Algebra/F2/Linear/FromImages.agda',                                   3, '136c901'),
  -- Opportunistic trans-sym site picked up in FromImages.agda during the multi-production migration.
  ((SELECT id FROM productions WHERE code='trans-sym'),  'Substrate/Algebra/F2/Linear/FromImages.agda',                                   2, '136c901');

-- sym-trans arc closure (commit 4b49216) + opportunistic cong-trans for the same file.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Cocycles/F2CubedPuncturing.agda', 3, '4b49216'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/F2CubedPuncturing.agda', 4, '4b49216');

-- HodgeDim3/MetricGauge cohort migration (commit b2050d4) — 5 files.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/StabiliserClosure.agda',                       5, 'b2050d4'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/Stabiliser.agda',                              7, 'b2050d4'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE0.agda',          6, 'b2050d4'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE1.agda',          6, 'b2050d4'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE2.agda',          6, 'b2050d4');

-- SymBilinForm cohort migration (commit c0c6983) — 2 files.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/SymBilinForm/Bilinearity.agda',                          11, 'c0c6983'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/SymBilinForm/CongruenceCompose.agda',                     5, 'c0c6983');

-- ReservedBridge single-file migration (commit 63200fe) — densest remaining single file.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/ReservedBridge.agda',                          12, '63200fe');

-- Algebra/F2 + Geometry/HodgeDim3 cohorts migration (commit bddf677) — 5 files.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/Vector.agda',                                              6, 'bddf677'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/AsModule.agda',                                            4, 'bddf677'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/F2/HodgeDim4/Bivector-F2Graded.agda',                         5, 'bddf677'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/Orthogonality.agda',                               7, 'bddf677'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Geometry/HodgeDim3/V4Plane.agda',                                     5, 'bddf677'),
  ((SELECT id FROM productions WHERE code='sym-trans'),  'Substrate/Geometry/HodgeDim3/V4Plane.agda',                                     2, 'bddf677');

-- cong-trans arc closure (commit b0fdf7b) — 6 final scattered files.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Algebra/Q/AsModule.agda',                                             9, 'b0fdf7b'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/Coxeter/Cyclic/InvCanonical/InvInv.agda',                      6, 'b0fdf7b'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Groups/S4-Iso/Foundation.agda',                                       5, 'b0fdf7b'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/ReservedToBivector.agda',               5, 'b0fdf7b'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Cocycles/V4Signature/Codeword/LiveS4Bijection/Reverse.agda',          5, 'b0fdf7b'),
  ((SELECT id FROM productions WHERE code='cong-trans'), 'Substrate/Category/Coalgebra/FiniteOrder.agda',                                 5, 'b0fdf7b');

-- KernelPredBridge extraction + migration (commit 30eb9b7) — 2 seed sites.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='pred-at-i→kernel-at-i'), 'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda', 2, '30eb9b7'),
  ((SELECT id FROM productions WHERE code='pred-at-i→kernel-at-i'), 'Substrate/Geometry/HodgeDim3/V4Plane.agda',       1, '30eb9b7'),
  ((SELECT id FROM productions WHERE code='kernel-at-i→pred-at-i'), 'Substrate/Geometry/HodgeDim3/ChiralityAxis.agda', 2, '30eb9b7'),
  ((SELECT id FROM productions WHERE code='kernel-at-i→pred-at-i'), 'Substrate/Geometry/HodgeDim3/V4Plane.agda',       1, '30eb9b7');

-- CubedOrbitWalk extraction + migration (commit 93e2764) — 3 seed sites.
INSERT INTO production_usages (production_id, file_path, occurrence_count, observed_at_commit) VALUES
  ((SELECT id FROM productions WHERE code='cubed-orbit-walk'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE0.agda', 1, '93e2764'),
  ((SELECT id FROM productions WHERE code='cubed-orbit-walk'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE1.agda', 1, '93e2764'),
  ((SELECT id FROM productions WHERE code='cubed-orbit-walk'), 'Substrate/Algebra/F2/HodgeDim3/MetricGauge/CoxeterRelations/S1S2CubedOnE2.agda', 1, '93e2764');

-- ============================================================================
-- C5 — GAP-DETECTOR-PRECISION-LAYER (depth-4 sketch extension)
--
-- Introduced after the structural-strictifier finding in commit 136c901:
-- the gap-detector's grep patterns catch substring matches inside cong₂
-- and identifiers like sym-sum-cong as false positives. C5 is the new
-- sub-architecture that intercepts raw regex output before it reaches
-- C4.2.3 (completion-suggester), discriminating real candidates from
-- regex false positives via three precision tiers.
-- ============================================================================

-- LAYER 1 — the new cluster.
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C5', (SELECT id FROM shadows WHERE code='arch'), 'gap-detector-precision-layer', 1, 'C5', 'productive',
   'R(reach, role-labeled-graphs)',
   'Sub-architecture between raw regex gap-detection and C4.2.3 candidate registration; discriminates real candidates from substring false positives via three precision tiers.');

-- Layer-1 PENMAN role-edges
INSERT INTO role_edges (shadow_id, source_node, role_label, target_node, target_role) VALUES
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':sits-between',      'sb', 'raw-grep-output and C4.2.3-completion-suggester'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':decomposes-into',   'p1', 'lexical-discriminator'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':decomposes-into',   'p2', 'ast-discriminator'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':decomposes-into',   'p3', 'semantic-discriminator'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':strengths-ordered', 'so', 'P.1-cheapest-P.3-strongest-only-when-needed'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':discharges',        'd',  'regex-false-positives'),
  ((SELECT id FROM shadows WHERE code='C5'), 'C5', ':preserves',         'pr', 'current-true-positive-recall');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C5'),
   'Short-circuit pipeline: regex matches enter C5.1; verdict spurious -> reject, verdict real -> pass to C4.2.3, verdict indeterminate -> escalate to C5.2; same again for C5.2 -> C5.3.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C5'),
   'C5.1.2 rule-table sound AND C5.2 AST-walk sound AND C5.3 unifier sound',
   'every C5-real candidate is a left-rule-applicable site, not a syntactic false positive');

-- LAYER 2 — three precision tiers.
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, rung, description) VALUES
  ('C5.1', (SELECT id FROM shadows WHERE code='C5'), 'lexical-discriminator', 2, 'C5', 'productive',
   'R(reach, transitions)',
   'Cheapest precision tier; word-boundary tests against rule table.'),
  ('C5.2', (SELECT id FROM shadows WHERE code='C5'), 'ast-discriminator', 2, 'C5', 'productive',
   'R(reach, transitions)',
   'Mid-tier; parses enclosing Agda expression and walks ancestors to check outer-context.'),
  ('C5.3', (SELECT id FROM shadows WHERE code='C5'), 'semantic-discriminator', 2, 'C5', 'productive',
   'R(cov, types)',
   'Strongest tier; type-checks whether candidate is a valid left-rule-application.');

INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1'), 1, 'regex-match-event(file, pos, match-text)', 'extract-token-boundaries-around-match', 'match-position-known',  'token-boundary-quadruple'),
  ((SELECT id FROM shadows WHERE code='C5.1'), 2, 'token-boundary-quadruple',                  'apply-word-boundary-tests',             'token-rules-loaded',    'discriminator-verdict (real | spurious | indeterminate)');

INSERT INTO transitions (shadow_id, ordinal, before_state, morphism, preconditions, after_state) VALUES
  ((SELECT id FROM shadows WHERE code='C5.2'), 1, 'indeterminate-verdict-from-C5.1(file, pos, match-text)', 'parse-enclosing-expression-via-agda-parser', 'agda-parser-available', 'term-AST-with-pinpointed-subterm'),
  ((SELECT id FROM shadows WHERE code='C5.2'), 2, 'term-AST-with-pinpointed-subterm',                       'walk-AST-checking-outer-operator',           'AST-shape-known',       'discriminator-verdict (real | spurious | indeterminate)');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1'), 'Sequential: extract token window, then apply rule-table classification; if any rule fires, emit verdict; else emit indeterminate.'),
  ((SELECT id FROM shadows WHERE code='C5.2'), 'Sequential: parse, ancestor-walk, classify. Defer to C5.3 only if AST classification is ambiguous.'),
  ((SELECT id FROM shadows WHERE code='C5.3'), 'Call into C3.2 unifier with production LHS and candidate site; extract substitution; construct applicability witness.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1'),
   'rule-table covers all known false-positive shapes',
   'C5.1 returns "real" only for tokens that are exact production-name applications'),
  ((SELECT id FROM shadows WHERE code='C5.2'),
   'Agda parser is sound AND ancestor-walk respects its depth limit',
   'C5.2 verdict is sound: real iff outer-context permits a production-as-head reading'),
  ((SELECT id FROM shadows WHERE code='C5.3'),
   'C3.2 unifier is sound (delegated)',
   'C5.3 "real" verdict is a typed proof of left-rule applicability — strongest possible precision');

-- LAYER 3 — sub-sub-shadows.
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C5.1.1', (SELECT id FROM shadows WHERE code='C5.1'), 'token-boundary-extractor', 3, 'C5', 'leaf',
   'Slices N chars before/after match position; tokenises via char-class rules (alpha, digit, subscript, hyphen, paren, whitespace).'),
  ('C5.1.2', (SELECT id FROM shadows WHERE code='C5.1'), 'rule-table', 3, 'C5', 'productive',
   'Per-production word-boundary tables. Positive contexts vs negative-known-false-positive contexts.'),
  ('C5.1.3', (SELECT id FROM shadows WHERE code='C5.1'), 'verdict-emitter', 3, 'C5', 'leaf',
   'Returns real | spurious | indeterminate; indeterminate when window-context is not classifiable.'),
  ('C5.2.1', (SELECT id FROM shadows WHERE code='C5.2'), 'agda-parser-invocation', 3, 'C5', 'leaf',
   'Uses existing Agda front-end or tree-sitter grammar; output is AST with match position marked.'),
  ('C5.2.2', (SELECT id FROM shadows WHERE code='C5.2'), 'ancestor-walk', 3, 'C5', 'productive',
   'Walks N ancestors of marker node checking outer-operator; bounded by depth limit.'),
  ('C5.2.3', (SELECT id FROM shadows WHERE code='C5.2'), 'outer-context-classifier', 3, 'C5', 'leaf',
   'Maps ancestor fingerprint to verdict via a classification table.'),
  ('C5.3.1', (SELECT id FROM shadows WHERE code='C5.3'), 'unifier-invocation', 3, 'C5', 'productive',
   'Calls into C3.2 unifier with production LHS and candidate site; returns Just unifier or Nothing.'),
  ('C5.3.2', (SELECT id FROM shadows WHERE code='C5.3'), 'substitution-extractor', 3, 'C5', 'leaf',
   'From successful unification, extracts substitution mapping production params to candidate args.'),
  ('C5.3.3', (SELECT id FROM shadows WHERE code='C5.3'), 'applicability-witness', 3, 'C5', 'leaf',
   'Typed proof that applying production RHS at candidate site produces a term of the same type.');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1.2'),
   'Lookup-then-decide: try positive contexts first, then negative, then fall back.'),
  ((SELECT id FROM shadows WHERE code='C5.2.2'),
   'Recursive descent with bounded depth (default 3); at each step, check parent operator against wrapping table.'),
  ((SELECT id FROM shadows WHERE code='C5.3.1'),
   'Single-step delegation to C3.2 unifier.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1.2'),
   'positive ∪ negative ∪ unknown partitions the context space',
   'verdict is total'),
  ((SELECT id FROM shadows WHERE code='C5.2.2'),
   'bounded depth (3) AND finite wrapping-table',
   'recursion terminates'),
  ((SELECT id FROM shadows WHERE code='C5.3.1'),
   'C3.2 unifier total + decidable',
   'C5.3.1 returns definite Just unifier or Nothing in finite time');

-- LAYER 4 — sub-sub-sub-shadows (where productive).
INSERT INTO shadows (code, parent_id, name, depth, cluster, status, description) VALUES
  ('C5.1.2.1', (SELECT id FROM shadows WHERE code='C5.1.2'), 'positive-context-generation', 4, 'C5', 'leaf',
   'For each production, canonical application shape is <production-name> followed by ws and ( or identifier; generated from production syntactic name.'),
  ('C5.1.2.2', (SELECT id FROM shadows WHERE code='C5.1.2'), 'negative-context-catalogue', 4, 'C5', 'productive',
   'Per-session-discovered false positives (cong₂, cong-trans, sym-sum-cong, sym-trans-id, ...); grows as new false positives are found.'),
  ('C5.1.2.3', (SELECT id FROM shadows WHERE code='C5.1.2'), 'fallback-policy', 4, 'C5', 'leaf',
   'Any context not in positive ∪ negative sets returns indeterminate, deferring to C5.2.'),
  ('C5.2.2.1', (SELECT id FROM shadows WHERE code='C5.2.2'), 'parent-operator-extractor', 4, 'C5', 'leaf',
   'Given a marker node, returns the operator at its direct AST parent.'),
  ('C5.2.2.2', (SELECT id FROM shadows WHERE code='C5.2.2'), 'wrapping-operator-table', 4, 'C5', 'leaf',
   'Which parent operators change the semantics of the matched substring (sym wrapping cong makes regex match a substring of sym (cong ...) rather than a real trans (cong ...) site).'),
  ('C5.2.2.3', (SELECT id FROM shadows WHERE code='C5.2.2'), 'walk-up-depth-limit', 4, 'C5', 'leaf',
   'Default 3; deeper walks are rare and expensive.'),
  ('C5.3.1.1', (SELECT id FROM shadows WHERE code='C5.3.1'), 'c3.2-call-shim', 4, 'C5', 'leaf',
   'Adapter: converts C5 candidate format to C3.2 unifier input format.');

INSERT INTO compositions (shadow_id, description) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1.2.2'),
   'Mutable append-only list; each migration commit that discovers a new false-positive shape appends a row.');

INSERT INTO entailments (shadow_id, antecedent, consequent) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1.2.2'),
   'append-only discipline + each row records discovering-commit',
   'catalogue is auditable and grows monotonically; never silently corrects past entries');

-- Cross-shadow entailment edges connecting C5 to existing clusters.
INSERT INTO cross_entailments (from_shadow_id, to_shadow_id, claim) VALUES
  ((SELECT id FROM shadows WHERE code='C5'),     (SELECT id FROM shadows WHERE code='C4.2.3'),
   'C5 verdict "real" ⊢ candidate is safe to register via C4.2.3 completion-suggester'),
  ((SELECT id FROM shadows WHERE code='C5.1'),   (SELECT id FROM shadows WHERE code='C5.2'),
   'C5.1 verdict "indeterminate" ⊢ defer to C5.2'),
  ((SELECT id FROM shadows WHERE code='C5.2'),   (SELECT id FROM shadows WHERE code='C5.3'),
   'C5.2 verdict "indeterminate" ⊢ defer to C5.3'),
  ((SELECT id FROM shadows WHERE code='C5.3.1'), (SELECT id FROM shadows WHERE code='C3.2'),
   'C5.3.1 delegates unification soundness to C3.2'),
  ((SELECT id FROM shadows WHERE code='C5.1.2.2'),(SELECT id FROM shadows WHERE code='C4.2.1'),
   'C5.1.2.2 catalogue grows in parallel with chirality-pair-detector findings; both record substrate-discovered structural facts');

-- Library-discipline correspondence: extraction_candidates.notes column IS the
-- depth-2 instance of C5.1.2.2 negative-context catalogue.
INSERT INTO library_correspondence (shadow_id, library_discipline, notes) VALUES
  ((SELECT id FROM shadows WHERE code='C5.1.2.2'),
   'extraction_candidates.notes column (false-positive rationale)',
   'Each "Migrated in <sha>; N real sites, M <kind> false positives" note in extraction_candidates.notes IS one row in C5.1.2.2 negative-context catalogue. The notes column is the live append-only log of discovered false-positive shapes.'),
  ((SELECT id FROM shadows WHERE code='C5'),
   'manual per-file inspection in commit 136c901',
   'Commit 136c901 manually executed C5.1 + C5.2 by hand for 3 files (Vector/Universal, FromImages); the new cluster names that work as automatable architecture.'),
  ((SELECT id FROM shadows WHERE code='C5.1.2.2'),
   'identifier-prefix false-positive shape: trans (congruence-* …)',
   'CongruenceBridge.agda has 5 sites of `trans (congruence-act-…)` / `trans (congruence-compose-…)` where `congruence-` is a single identifier starting with `cong-`. Generalises the cong-trans false-positive class beyond `cong₂` to any identifier prefixed by `cong<separator>`. Discovered in b2050d4 during MetricGauge cohort migration.'),
  ((SELECT id FROM shadows WHERE code='C1'),
   'KernelPredBridge module (pred-at-i↔kernel-at-i pair)',
   'Higher-order Γ-production: discovered by typed-holes on ChiralityAxis ↔ V4Plane AFTER the Foundation.Eq trio arc closed. Bridges (a) component-equality predicate form and (b) kernel-of-linear-map form for F₂-vector subspaces. Composes the trio with lookup-𝟎; each per-site call collapses ~3 lines per index. Demonstrates the iterated-SPPF principle at depth-2: trio extraction surfaces NEW bridges that the trio alone couldn''t express.'),
  ((SELECT id FROM shadows WHERE code='C1'),
   'CubedOrbitWalk module (parametric Coxeter (s₁∘s₂)³ on basis)',
   'Parametric production extracted under the fine-grained-over-coarse discipline. The 3 S1S2CubedOn{E0,E1,E2} files shared a 5-call cong-trans chain template with 6 swap-lemma argument positions varying per starting basis. Was initially declined under DBE''s over-decomposition warning; reinstated when the user clarified that fine-grained primitives are mechanically recomposable while coarse-grained primitives cause context-flood for rearrangement.');

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
