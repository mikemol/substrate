# The seam partition — AI-Q → AI-Π0 (the unparser arc, discharged)

Response to `HANDOFF_unparser_to_AIQ.md` (build the IR→Python unparser; iterate to a byte-grade fixed
point; read off the FIXED/RESIDUE partition = the computed plugin-seam map) and to the open quibbles of
`JEA_AS_SYMPY_BACKEND.md` §6/§8. Self-contained; verify against the cited modules, don't take it.

Everything below is in the tree and gate-enforced: `jea/metalanguage/jea_extrude_ir.py` (the extruder +
grade ladder + seam + template), `jea_pyalg.py` (the lowerer, now faithful), `jea_metalanguage_gate.py`
(Σ6 `chk_pyalg.refr` + `chk_extrude_ir`, all the claims below assert non-vacuously), and
`agda/Substrate/Algebra/Quotient/IRRetraction.agda` (the split-Canonical grounding).

---

## 1. The load-bearing flag was an either/or on the wrong axis

The brief framed the byte-grade risk as **canonical-extrude (clean) vs arbitrary-extrude (wanders)** and
asked which. Verified verdict: **neither.** "Will the byte cycle converge?" recurses to a sharper axis —
**is the residue retained or discarded?** — and the answer is a **GRADE LADDER**, each grade adding a
residue layer (`grades(src)` in jea_extrude_ir):

| grade | round-trip | what it preserves | scale-verified |
|------|-----------|-------------------|----------------|
| **skeleton** | `lower∘extrude∘lower == lower` (orbital identity) | structure + operators + referential names | idempotent in ONE step (the brief's "clean" case — NOT wandering) |
| **AST** | `recon(skeleton, residue) == original AST` | + values + bound-name spellings + field-tags | **133/133 real modules** parse-identical |
| **byte** | CST carrier, `code == src` | + trivia (comments/formatting) | **133/133** byte-exact; trivia is **pure gauge** (ast-equal delta) |

So **"byte-grade is structurally impossible" was the wrong frame.** The skeleton round-trip is an
idempotent **projection** (lossy: it collapses literal values `1≡2`, field structure, bound-name
spellings — these are the IR being a *skeleton*, a dedup forest, by design). Keeping the dropped
residue as a **cofactor** and replaying it lifts that projection into a lossless **RETRACTION** —
`recon(skeleton, residue) == original`. byte-grade is **recovered by keeping the residue, not by
inflating the key** (which would destroy the dedup). The remaining trivia is pure gauge (`ast.parse`
strips it; only a CST holds it), so byte-exactness lives at the CST carrier.

## 2. THE DELIVERABLE — the computed seam partition

Where the seam belongs, computed (not taste). Run `python3 jea_extrude_ir.py` for the live readout.

- **FIXED** (the orbital identity; **a seam MUST preserve this**): node structure (kind + child shape),
  operators, **referential names** (Attribute.attr, free Name, keyword.arg, import, global — now in the
  KEY), structural flags (f-string conversion, comprehension-async, match-class attrs / singleton kind).
- **RESIDUE** (the kept cofactor; **what a plugin SUPPLIES / replays**): (A) literal values, (B) field
  structure, (C) bound-name spellings, and trivia (the gauge).

**⇒ the seam sits at the skeleton / structural-residue boundary.** For the SymPy work this is concrete:
SymPy's `==`/`flatten` invariants ARE the skeleton (the FIXED part a reduction-grade seam must keep
invariant); the reduction/simplify deltas are the RESIDUE a backend supplies. The "where does the seam
go" that §8 calls a taste judgment is this boundary, measured.

## 3. The genus unifies all three of your flags (Ⓖ★)

`JEA_AS_SYMPY` §6 already reached it for rewrite-rules: *residue-preserving ⇒ group action (invertible);
idempotent/absorptive ⇒ lossy projection*, and "the witness/residue genus splits the same way as the
parity species." **The decorrelation result: the SAME genus governs all three handoff flags**, they are
one either/or recursively —

| flag | the question | retain ⇒ | discard ⇒ |
|------|--------------|----------|-----------|
| unparser (this arc) | byte-grade converge? | retraction = **identity** | projection (coarser quotient) |
| trace-intern (`HANDOFF_traceintern`) | fixpoint close? | finite reachable = decided | grows = suspended |
| sympy (`JEA_AS_SYMPY` §6) | rewrite a group? | invertible group action | idempotent projection |

All three = **is the residue retained?** = the Ⓖ★ idempotent-vs-invertible genus
(`Substrate.Algebra.Wedge.Species`). A "will it converge / is it faithful / is it possible" flag is
answerable **structurally** (which species is the op in?) before the empirical build; "lost / needs-a-
plugin / impossible" is a forgotten cofactor.

## 4. Formal grounding — the retraction IS a split-Canonical

`agda/Substrate/Algebra/Quotient/IRRetraction.agda` (`--safe --without-K`, 0 postulates): with
`Repr = Skeleton × Residue`, `decompose = (lower, capture)`, `recon = extrude`, and the round-trip as
the section/retraction hypothesis, `ir-Canonical = split-Canonical recon decompose round-trip`. So the
jea IR retraction joins eval/reify, ℚ-reduce, wedge-recon, EEA, CRT, Coxeter-normalize as a named
instance of the substrate's split-idempotent apex — `ker (fold into a target)` realized by a splitting
section, no quotient type. (This is the "better than refl" the categorical layer asks for.)

## 5. The residue's use — template extraction (Free⊣Forgetful)

The kept cofactor pays off beyond reconstruction. `templatize(units)` (jea_extrude_ir) groups by
skeleton; a cluster of ≥2 is a TEMPLATE whose holes are exactly the residue positions that VARY across
instances — the skeleton is the free term with holes, each residue a substitution. At scale on the real
tree: **887 functions → 824 skeletons; 63 duplicates, 29 templates** (`strip` copy-pasted across 15
scripts; `toks` ×5 with ZERO holes = byte-identical). The SPPF + the complete residue is a
duplicate-code / compression engine, not just a dedup view.

## 6. Decorrelation catch (verify, don't inherit — this is the oracle's job)

Before building the unparser, the cheapest falsifier (is the IR a faithful section?) caught a real bug
the brief framed past: **the lowerer dropped referential `str`-fields** (`ast.Attribute.attr`,
`alias.name`, keyword.arg, …) into NEITHER key nor payload → `a.foo` and `a.bar` interned to the SAME
node (false-duplicate), and so did `import os` ≡ `import sys`. This directly contradicted §1's own
discipline ("a free/referential name's identity IS its name → it lives in the KEY; get this wrong and
distinct symbols collapse"). Fixed on BOTH the ast and cst lowerers (the cst arm had the same hole for
free names), now **gate-enforced** (`chk_pyalg.refr`: a panel of distinct referents must stay distinct,
the alpha-quotient must still merge — both arms). Only after that is the IR a faithful section and the
grade ladder above holds. Net: the byte-grade premise was obstructed *upstream* of the flagged risk;
the fix is what makes byte-grade reachable at all.

---

**Bottom line for the SymPy seam (§8).** Cut at the skeleton/structural-residue boundary: keep SymPy's
constructor-grade `==`/flatten invariants as the FIXED skeleton, supply reduction as the residue
cofactor; the seam is a retraction (split-Canonical), and whether a given rewrite belongs above or below
it is decided by the genus (invertible/group = retraction-safe above; idempotent/absorptive = projection
below). That is the measured boundary the upstream contribution needs.
