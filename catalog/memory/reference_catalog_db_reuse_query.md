---
name: reference_catalog_db_reuse_query
description: catalog/catalog.db is a queryable SQLite structural index (structs/members/shape_parallel) of every data+record in the tree — query it BEFORE hand-building graded/monoidal/law machinery; it catches reinventions grep misses.
metadata: 
  node_type: memory
  type: reference
  originSessionId: d35bc15a-16b8-42c5-aad1-20966c9a9f8e
---

`catalog/catalog.db` is a SQLite reuse index the reuse-search discipline should hit FIRST for
"does a structure of this shape exist" — it is the queryable form of `catalog/reuse-index.md`,
stronger than grep because it indexes canonical typechecked cores and fingerprints their shape.

Schema (tables): `structs(qname,name,kind,module,fp,desc)` — every `data` (306) + `record`
(517) in the tree, `fp` = shape fingerprint; `members(struct_qname,name,ord)` — a struct's
fields/constructors; `refs`, `edges`, `module_edges`, `modules(module,purpose)`. Views:
`shape_parallel(fp,names,structs)` = **same-shape-different-name** (the reinvention detector),
`multiply_homed`, `in_degree`/`out_degree`. NOTE: indexes STRUCTURES only, not functions/lemmas
— a lemma like `combine-assoc` won't appear; search its HOME record's `members` or grep for it.

Useful queries (run from repo root):
- `sqlite3 -header catalog/catalog.db "SELECT name,module FROM structs WHERE name LIKE '%onoidal%' OR name LIKE '%Rig%' OR name LIKE '%ssociat%';"`
- members of a record: `SELECT m.name FROM members m JOIN structs s ON m.struct_qname=s.qname WHERE s.name='GradedMonoidalAdjunction' ORDER BY m.ord;`
- everything in a namespace: `SELECT name,kind,module FROM structs WHERE module LIKE 'Substrate.Algebra.Wedge.Graded%';`

**Caught 2026-07-10 (the ⟡rig / graded-Lehmer-rig arc):** I was hand-building bespoke ⊕-assoc/
⊕-unit lemmas and a "decode is a monoidal functor" framing from scratch. The db surfaced
`GradedProduct C` (`u : C 0`, `_∧_ : C i → C j → C(i+j)`), `Product.LawTypes` (`GradedAssoc/
GradedUnitˡ/GradedUnitʳ` — VERBATIM my lemma types), `GradedMonoidalAdjunction` (the five-face
uniting record), and `SymmetricMonoidal` (`σ`/`σ-involution` — exactly my blockSwap/factorSwap
+ their involutions). My ⊕ WAS a GradedProduct; the laws WERE its fields. The user had to point
me at the db. See CLAUDE.md "Reuse-search BEFORE building" + [[feedback_reuse_search_before_feasibility_conclusions]];
this names the specific always-there tool. Rule: before a new `record`/law-type in the
graded/monoidal/algebra layers, run the shape query — the Wedge.Graded framework likely frames it.
