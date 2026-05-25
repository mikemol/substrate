-- ============================================================================
-- Sample queries against the elaborator-sketch database.
-- Run with: sqlite3 sketch.db < queries.sql
-- ============================================================================

.headers on
.mode column

-- ----------------------------------------------------------------------------
-- 1. Tree walk: every shadow with its parent and depth.
-- ----------------------------------------------------------------------------
.print
.print '== Tree walk (depth-ordered) =='
SELECT s.code, s.depth, p.code AS parent, s.status, s.name
FROM shadows s
LEFT JOIN shadows p ON s.parent_id = p.id
ORDER BY s.depth, s.code;

-- ----------------------------------------------------------------------------
-- 2. All productive shadows by cluster, with descendant count.
-- ----------------------------------------------------------------------------
.print
.print '== Productive shadows by cluster + descendant count =='
WITH RECURSIVE descendants(root_id, descendant_id) AS (
  SELECT id, id FROM shadows
  UNION ALL
  SELECT d.root_id, c.id FROM descendants d JOIN shadows c ON c.parent_id = d.descendant_id
)
SELECT s.cluster, s.code, s.name, COUNT(d.descendant_id) - 1 AS descendants
FROM shadows s
LEFT JOIN descendants d ON d.root_id = s.id
WHERE s.status = 'productive'
GROUP BY s.id
ORDER BY s.cluster, s.code;

-- ----------------------------------------------------------------------------
-- 3. Status distribution.
-- ----------------------------------------------------------------------------
.print
.print '== Status distribution =='
SELECT status, COUNT(*) AS n FROM shadows GROUP BY status ORDER BY n DESC;

-- ----------------------------------------------------------------------------
-- 4. All R(cov, types) — the highest-rigour cells.
-- ----------------------------------------------------------------------------
.print
.print '== Typed-term cells =='
SELECT code, name, description FROM shadows WHERE rung LIKE 'R(cov, types)%';

-- ----------------------------------------------------------------------------
-- 5. Transitions for a specific shadow (e.g., C4 soundness-discipline).
-- ----------------------------------------------------------------------------
.print
.print '== Transitions for C4 =='
SELECT ordinal, before_state, morphism, preconditions, after_state
FROM transitions t JOIN shadows s ON t.shadow_id = s.id
WHERE s.code = 'C4'
ORDER BY ordinal;

-- ----------------------------------------------------------------------------
-- 6. Cross-shadow entailment graph.
-- ----------------------------------------------------------------------------
.print
.print '== Cross-shadow entailment edges =='
SELECT f.code AS from_code, t.code AS to_code, ce.claim
FROM cross_entailments ce
JOIN shadows f ON ce.from_shadow_id = f.id
JOIN shadows t ON ce.to_shadow_id   = t.id
ORDER BY f.code;

-- ----------------------------------------------------------------------------
-- 7. Substrate-library-discipline correspondences.
-- ----------------------------------------------------------------------------
.print
.print '== Library-discipline correspondences =='
SELECT s.code, lc.library_discipline, lc.notes
FROM library_correspondence lc
JOIN shadows s ON lc.shadow_id = s.id
ORDER BY s.code;

-- ----------------------------------------------------------------------------
-- 8. Research frontiers (where depth-N+1 is genuinely open).
-- ----------------------------------------------------------------------------
.print
.print '== Research frontiers =='
SELECT code, name, description FROM shadows WHERE status = 'research-frontier';

-- ----------------------------------------------------------------------------
-- 9. Path from any node back to root.
-- ----------------------------------------------------------------------------
.print
.print '== Path from C4.2.2.3 to root =='
WITH RECURSIVE path(id, parent_id, code, name, depth) AS (
  SELECT id, parent_id, code, name, depth FROM shadows WHERE code = 'C4.2.2.3'
  UNION ALL
  SELECT s.id, s.parent_id, s.code, s.name, s.depth
  FROM shadows s JOIN path p ON s.id = p.parent_id
)
SELECT depth, code, name FROM path ORDER BY depth;

-- ----------------------------------------------------------------------------
-- 10. Frontier-of-the-sketch view: nodes with no children (leaves+frontiers+root-if-childless).
-- ----------------------------------------------------------------------------
.print
.print '== Childless nodes (= sketch frontier) by cluster =='
SELECT s.cluster, s.status, COUNT(*) AS n
FROM shadows s
WHERE NOT EXISTS (SELECT 1 FROM shadows c WHERE c.parent_id = s.id)
GROUP BY s.cluster, s.status
ORDER BY s.cluster, s.status;
