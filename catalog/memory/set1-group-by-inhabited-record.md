---
name: set1-group-by-inhabited-record
description: "To find Set₁ consolidation orbits, group defs by the RECORD their TYPE inhabits (decode_core type-head), NOT by shared-subtree — shared-subtree is a proxy that surfaces the AST floor and fragments each record's orbit."
metadata:
  node_type: memory
  type: project
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

Building `scratch/set1_consolidate.py` (⟡set1-consolidate-report, 2026-07-16), the plan spec (from a saturation
agent) assumed `reuse_tui.db_rows` + `resolve_orbit`'s SHARED-SUBTREE grouping would recover the canonical records
whose carrier-reparameterize drains a Set₁ orbit. **It does NOT** — shared-subtree is a PROXY for "same record
instantiated," and the two diverge: the max-impact covering subtree for a Set₁ instance is a UNIVERSAL Foundation
node (`Fin.suc` fanin 266, `Vec`, `Product._,_`), so the report surfaced the AST floor at the top and FRAGMENTED
each record's instance-orbit across the shared primitives.

**The correct, semantic signal is the TYPE-HEAD** — the record a def's TYPE inhabits, read from the elaborated core:
a Set₁ record-instance `F2-CommMonoid : CommutativeMonoid F₂ …` decodes to `Defn [type, clause]`; the TYPE node's
HEAD symbol (peel `Pi`→codomain / `App`→function to the head `Def`/`Con`) IS `CommutativeMonoid`. Grouping by that
reproduced the research EXACTLY (355 = the ratchet baseline; the 5 records drain 42 originals) and surfaced MORE
(Brick 14, RosettaEntry 12). Extraction: `jea_agdai.decode_core(agdai)` → `{defmarks, nodes}`; per Set₁ defmark
(`level≥1`), `type_head(nodes, defmark["root"])`; the defmark `copy` field marks re-export copies (drain
derivatively — count originals). Self-contained (no reuse_tui/Textual; home-file = the record qname's module file).

**Why (the general lesson):** this is [[read-structure-dont-rebuild]] / reuse-search-the-real-signal — the substrate
NAMES its centers (a def's inhabited record is IN its elaborated type), so read the ground truth (`decode_core` type),
don't proxy via a surrogate (shared-subtree) that happens to be available. The proxy's failure mode is generic:
universal low-level nodes dominate by impact, coherent semantic orbits fragment. When grouping "instances of X",
group by the X in the TYPE, not by what the values happen to SHARE.

Relates to [[read-structure-dont-rebuild]], [[set1-carrier-always-parameterize]], [[set1-is-grade-collapse]],
[[reuse-search-structural-questions]], [[collapse-keeps-the-orientation-residue]].
