-- ============================================================================
-- Elaborator-as-sequent-indexed-SPPF sketch — schema
--
-- Persists the depth-2/3/4 structural sketch of routing Agda's Signature and
-- MetaStore through a sequent-indexed SPPF. Each shadow is one node in a tree
-- whose root is the architecture target. Transitions, role-edges,
-- compositions, and entailments hang off shadows.
--
-- Two cell families per structural-strictifier:
--   * R(reach, transitions) shadows populate `transitions`
--   * R(reach, role-labeled-graphs) shadows populate `role_edges`
--   * R(cov, types) shadows are flagged in `shadows.rung` but their typed-term
--     content is held only as descriptive text — depth-4 would emit Agda.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- Shadow tree.
--
-- code is the dotted identifier (arch, C1, C1.2, C1.2.2, X1, ...).
-- depth: 0 = root, 1 = layer-1 cluster, 2 = layer-2 sub-shadow, etc.
-- status: 'root' | 'productive' | 'leaf' | 'research-frontier' | 'cross-cutting'
-- rung: structural-strictifier RUNG header e.g. 'R(reach, transitions)'
CREATE TABLE shadows (
  id           INTEGER PRIMARY KEY,
  parent_id    INTEGER REFERENCES shadows(id),
  code         TEXT NOT NULL UNIQUE,
  name         TEXT NOT NULL,
  depth        INTEGER NOT NULL,
  cluster      TEXT,
  status       TEXT NOT NULL CHECK (status IN ('root','productive','leaf','research-frontier','cross-cutting')),
  rung         TEXT,
  description  TEXT
);

CREATE INDEX idx_shadows_parent ON shadows(parent_id);
CREATE INDEX idx_shadows_cluster ON shadows(cluster);
CREATE INDEX idx_shadows_status ON shadows(status);

-- Named state→morphism→state steps within a single shadow (R(reach, trans) cell).
CREATE TABLE transitions (
  id             INTEGER PRIMARY KEY,
  shadow_id      INTEGER NOT NULL REFERENCES shadows(id),
  ordinal        INTEGER NOT NULL,
  before_state   TEXT NOT NULL,
  morphism       TEXT NOT NULL,
  preconditions  TEXT,
  after_state    TEXT NOT NULL,
  UNIQUE (shadow_id, ordinal)
);

CREATE INDEX idx_transitions_shadow ON transitions(shadow_id);

-- Role-labeled edges within a single shadow (R(reach, graph) cell).
CREATE TABLE role_edges (
  id           INTEGER PRIMARY KEY,
  shadow_id    INTEGER NOT NULL REFERENCES shadows(id),
  source_node  TEXT NOT NULL,
  role_label   TEXT NOT NULL,
  target_node  TEXT NOT NULL,
  target_role  TEXT
);

CREATE INDEX idx_role_edges_shadow ON role_edges(shadow_id);

-- One composition per shadow describing how its sub-shadows assemble.
CREATE TABLE compositions (
  shadow_id    INTEGER PRIMARY KEY REFERENCES shadows(id),
  description  TEXT NOT NULL
);

-- Per-shadow entailment claims (the licensing inference).
CREATE TABLE entailments (
  id           INTEGER PRIMARY KEY,
  shadow_id    INTEGER NOT NULL REFERENCES shadows(id),
  antecedent   TEXT NOT NULL,
  consequent   TEXT NOT NULL
);

CREATE INDEX idx_entailments_shadow ON entailments(shadow_id);

-- Cross-shadow entailment edges (the chain that runs across the whole sketch).
CREATE TABLE cross_entailments (
  id              INTEGER PRIMARY KEY,
  from_shadow_id  INTEGER NOT NULL REFERENCES shadows(id),
  to_shadow_id    INTEGER NOT NULL REFERENCES shadows(id),
  claim           TEXT NOT NULL
);

CREATE INDEX idx_cross_from ON cross_entailments(from_shadow_id);
CREATE INDEX idx_cross_to ON cross_entailments(to_shadow_id);

-- Maps substrate library-discipline artefacts to the implementation shadow
-- they realise. e.g., chirality-pair-completeness → C4.2.1.
CREATE TABLE library_correspondence (
  id                   INTEGER PRIMARY KEY,
  shadow_id            INTEGER NOT NULL REFERENCES shadows(id),
  library_discipline   TEXT NOT NULL,
  notes                TEXT
);

CREATE INDEX idx_lib_corr_shadow ON library_correspondence(shadow_id);
