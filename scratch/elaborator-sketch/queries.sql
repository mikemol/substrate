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

-- ----------------------------------------------------------------------------
-- 11. COVERAGE INVARIANTS — must return zero rows on a structurally complete db.
-- ----------------------------------------------------------------------------
.print
.print '== Coverage invariant 1: productive/cross-cutting shadows missing composition =='
SELECT s.code, s.name FROM shadows s
WHERE s.status IN ('productive','cross-cutting')
  AND NOT EXISTS (SELECT 1 FROM compositions c WHERE c.shadow_id = s.id);

.print
.print '== Coverage invariant 2: productive/cross-cutting shadows missing entailment =='
SELECT s.code, s.name FROM shadows s
WHERE s.status IN ('productive','cross-cutting')
  AND NOT EXISTS (SELECT 1 FROM entailments e WHERE e.shadow_id = s.id);

.print
.print '== Coverage invariant 3: R(reach, transitions) shadows missing transitions =='
SELECT s.code, s.name FROM shadows s
WHERE s.rung LIKE 'R(reach, transitions)%'
  AND s.status IN ('productive','cross-cutting','root','leaf')
  AND NOT EXISTS (SELECT 1 FROM transitions t WHERE t.shadow_id = s.id)
  AND s.code IN ('C1.1');  -- explicit leaf-with-prose-transitions allowlist; expand as more prose lands

.print
.print '== Coverage invariant 4: R(reach, role-labeled-graphs) shadows missing role-edges =='
SELECT s.code, s.name FROM shadows s
WHERE s.rung LIKE 'R(reach, role-labeled-graphs)%'
  AND s.status IN ('root','productive','cross-cutting')
  AND NOT EXISTS (SELECT 1 FROM role_edges r WHERE r.shadow_id = s.id);

.print
.print 'If any of the four invariant queries above returns rows, the db is structurally incomplete with respect to the prose sketch.'

-- ----------------------------------------------------------------------------
-- 12. Γ-INSTANCE QUERIES — exercise the productions / production_usages tables.
-- ----------------------------------------------------------------------------

.print
.print '== Productions registered in Gamma (the substrate library) =='
SELECT code, module_path, status, extraction_commit FROM productions ORDER BY code;

.print
.print '== Usage count totals per production =='
SELECT p.code, COUNT(u.id) AS usage_files, SUM(u.occurrence_count) AS total_occurrences
FROM productions p LEFT JOIN production_usages u ON u.production_id = p.id
GROUP BY p.id ORDER BY p.code;

.print
.print '== Top adopter files (= files adopting most distinct productions) =='
SELECT u.file_path, COUNT(DISTINCT u.production_id) AS distinct_productions, SUM(u.occurrence_count) AS total_occurrences
FROM production_usages u
GROUP BY u.file_path
ORDER BY distinct_productions DESC, total_occurrences DESC
LIMIT 10;

.print
.print '== Productions and their containing-file count (forward production-ref index view) =='
SELECT p.code, p.lhs_signature, COUNT(u.id) AS files
FROM productions p LEFT JOIN production_usages u ON u.production_id = p.id
GROUP BY p.id ORDER BY files DESC;

-- ----------------------------------------------------------------------------
-- 13. CROSS-VIEW — productions linked to architecture shadows via correspondence.
-- ----------------------------------------------------------------------------

.print
.print '== Architecture shadows that have library-level Gamma-instances =='
SELECT s.code, s.name, lc.library_discipline, lc.notes
FROM shadows s
JOIN library_correspondence lc ON lc.shadow_id = s.id
WHERE lc.library_discipline LIKE '%table%' OR lc.library_discipline LIKE '%production%'
ORDER BY s.code;

-- ----------------------------------------------------------------------------
-- 14. GAP-DETECTOR QUERIES — exercise the extraction_candidates table.
-- ----------------------------------------------------------------------------

.print
.print '== Top 10 highest-density extraction candidates (proposed only) =='
SELECT p.code AS production, ec.file_path, ec.occurrence_count
FROM extraction_candidates ec
JOIN productions p ON p.id = ec.production_id
WHERE ec.status = 'proposed'
ORDER BY ec.occurrence_count DESC
LIMIT 10;

.print
.print '== Candidate summary by production =='
SELECT p.code AS production,
       SUM(CASE WHEN ec.status='proposed' THEN 1 ELSE 0 END) AS proposed_files,
       SUM(CASE WHEN ec.status='proposed' THEN ec.occurrence_count ELSE 0 END) AS proposed_total_sites,
       SUM(CASE WHEN ec.status='rejected' THEN 1 ELSE 0 END) AS rejected_files
FROM productions p
LEFT JOIN extraction_candidates ec ON ec.production_id = p.id
GROUP BY p.code ORDER BY p.code;

.print
.print '== Total adoption picture: production X (migrated + proposed + rejected) =='
SELECT p.code AS production,
       (SELECT COUNT(*) FROM production_usages u WHERE u.production_id = p.id)   AS migrated_files,
       (SELECT COALESCE(SUM(u.occurrence_count),0) FROM production_usages u WHERE u.production_id = p.id) AS migrated_sites,
       (SELECT COUNT(*) FROM extraction_candidates ec WHERE ec.production_id = p.id AND ec.status='proposed') AS proposed_files,
       (SELECT COALESCE(SUM(ec.occurrence_count),0) FROM extraction_candidates ec WHERE ec.production_id = p.id AND ec.status='proposed') AS proposed_sites
FROM productions p ORDER BY p.code;

.print
.print '== Rejected candidates with rationale (false positives) =='
SELECT p.code AS production, ec.file_path, ec.occurrence_count, ec.notes
FROM extraction_candidates ec
JOIN productions p ON p.id = ec.production_id
WHERE ec.status = 'rejected';

.print
.print '== Files that are candidates for MULTIPLE productions (high-payoff migration targets) =='
SELECT ec.file_path, GROUP_CONCAT(p.code, ', ') AS productions, SUM(ec.occurrence_count) AS total_sites
FROM extraction_candidates ec
JOIN productions p ON p.id = ec.production_id
WHERE ec.status = 'proposed'
GROUP BY ec.file_path
HAVING COUNT(DISTINCT p.id) > 1
ORDER BY total_sites DESC;
