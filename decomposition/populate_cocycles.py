#!/usr/bin/env python3
"""Populate the cocycles table in cotype_decomposition.sqlite.

Mirror of catalog/cocycles.md. Each row corresponds to one cocycle
record in the markdown source; the markdown remains authoritative,
this script makes the data queryable.
"""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


COCYCLES = [
    {
        "slug": "cy-1-representation",
        "name": "Representation cocycle",
        "layer": "Level 2 — rule references",
        "base": "rule representations {integer-as-path, function-as-path, "
                "trace-as-path, polynomial-as-path}",
        "gauge_group": "transform morphisms (S7)",
        "cohomology_classes": "one class per abstract rule",
        "gauge_invariant": "abstract rule identity",
        "introducing_move": "M2",
        "witness_evidence": "../scratch/chart.py:214-226 (operationally empty bridge)",
        "status": "empty-bridge rigidification",
        "notes": "Only integer-as-path operationally realised. M2 named "
                 "four representations as first-class via S7; transform "
                 "raises NotImplementedError for non-identity. Type-D "
                 "empty-bridge sub-variant. Recovery: implement at least "
                 "trace-as-path.",
    },
    {
        "slug": "cy-2-k-rule-variables",
        "name": "K-rule variable cocycle",
        "layer": "Level 4 — K-rule variable assignments",
        "base": "assignment space V × V (2-variable K-rules)",
        "gauge_group": "S_n by variable renaming",
        "cohomology_classes": "{off-diagonal (vx≠vy), diagonal (v,v)}",
        "gauge_invariant": "partition refinement on slot indices",
        "introducing_move": "M17",
        "witness_evidence": "../scratch/search_k_variants.py; "
                            "cotype-free-self-extending-grammar.md:1339-1410",
        "status": "shown",
        "notes": "M17 explicitly: 'M8's cocycle structure becomes directly "
                 "observable: Orbits are the cohomology classes; entries "
                 "within an orbit are connected by gauge transformations.'",
    },
    {
        "slug": "cy-3-wht-quotient",
        "name": "WHT quotient cocycle",
        "layer": "Level 5 — Walsh-Hadamard codewords",
        "base": "WHT codeword space (length 2^m at level m)",
        "gauge_group": "parity-basin equivalence",
        "cohomology_classes": "parity-basin equivalence classes",
        "gauge_invariant": "Walsh-row index (axis-signature ↔ Walsh row)",
        "introducing_move": "M22 (first triplet)",
        "witness_evidence": "../scratch/walsh_hadamard_readings.py; "
                            "../scratch/walsh_hadamard_core.py; "
                            "cotype-free-self-extending-grammar.md:1752-1873",
        "status": "shown",
        "notes": "WH projection is the cocycle projection in WH-character "
                 "vocabulary. Also realises M2's associahedron polytope "
                 "of representations.",
    },
    {
        "slug": "cy-4-f23-puncturing",
        "name": "F_2³ puncturing gauge cocycle",
        "layer": "Level 6 — 8 puncturings of RM(1,3)",
        "base": "8 coordinate puncturings as an F_2³ torsor",
        "gauge_group": "F_2³ translation (3-bit XOR)",
        "cohomology_classes": "single orbit (the WHT core)",
        "gauge_invariant": "the WHT core itself",
        "introducing_move": "M22 (second triplet, M22-bis)",
        "witness_evidence": "../scratch/walsh_hadamard_core.py; "
                            "cotype-free-self-extending-grammar.md:2221-2331",
        "status": "shown",
        "notes": "S (state axis) is the gauge-invariant pivot of the "
                 "8-frame rotation (M23-bis); the other three (D, C, W) "
                 "rotate under F_2³.",
    },
    {
        "slug": "cy-5-v4-signature",
        "name": "V_4 signature cocycle",
        "layer": "Level 9 — directed witnessed-pair signatures",
        "base": "24 valid signatures = elements of S_4 (per s4_structure.py: "
                "σ ∈ S_4 ↔ (σ(D), σ(C), σ(S))); the 24 emerge combinatorially "
                "from C(4,3) × 3! axis-selections × orderings, co-defined "
                "by the 8-element parity space (4 axes × 2 chiralities) that "
                "encodes the 3-of-4 quotienting",
        "gauge_group": "V_4 axis swaps {e, (DC)(SW), (DS)(CW), (DW)(CS)}",
        "cohomology_classes": "6 orbits indexed by (pairing, chirality) ∈ "
                              "{α,β,γ} × {even, odd}, 4 elements each",
        "gauge_invariant": "orbit_key = (pairing, chirality)",
        "introducing_move": "M41 v16 (formalised v19)",
        "witness_evidence": "../applied_grammar.py:861-956 "
                            "(decompose_signature/recompose_signature); "
                            "verify_signature_decomposition_bijection",
        "status": "shown; rigidified-by-lex-min (Type-D verifier-contract)",
        "notes": "The 24 base elements ARE S_4 itself (operationally the "
                 "architectural symmetry group A_4 × Z_2 per M40). The 8 "
                 "complement codewords are NOT noise — they're the parity "
                 "space anchoring the 3-of-4 selection that defines what "
                 "'directed triple' means. Hodge ★ in dim 4 is the "
                 "categorical reading of the same structure (24 = Λ^3 "
                 "ordered triples ↔ 8 = Λ^1 signed singletons). Type-D "
                 "rigidification at lex-min is in v4_delta content-"
                 "addressing — receipts encode the canonical choice. "
                 "Recovery: content-address by orbit_key only.",
    },
    {
        "slug": "cy-6-parse-derivation",
        "name": "Parse-derivation cocycle (grammar / SPPF / parsing)",
        "layer": "NB-B content syntax — pre-M1 / M1 S6",
        "base": "derivations of input strings under a grammar",
        "gauge_group": "parse-tree equivalence (multiple derivations of "
                       "same span are gauge-equivalent)",
        "cohomology_classes": "packed nodes in the SPPF (each is a span "
                              "with its alternative derivations)",
        "gauge_invariant": "the language-reading of the input "
                           "(meaning modulo derivation choice)",
        "introducing_move": "pre-M1 (founding SPPF design); M1 S6 parse",
        "witness_evidence": "MHTML title 'Numpy-backed SPPF datastructure "
                            "design'; S6 parse operation as gauge-"
                            "invariant return",
        "status": "correct orbit-collapse with virtual recovery "
                  "(NOT a Type-D rigidification)",
        "notes": "Revised 2026-05-15 per user clarification: storing "
                 "only the canonical Rule is correct gauge-collapse, "
                 "not lossy compression. Alternatives are virtually "
                 "recoverable from (grammar, input, "
                 "alternative-selection-rule) by re-running the parser. "
                 "Reconstruction upgrade: name and parametrise the "
                 "canonicalization function, do NOT expose alternatives "
                 "in storage (would break metacircular collapse).",
    },
    {
        "slug": "cy-7-combinator-reduction",
        "name": "Combinator-reduction cocycle (SKI / λ)",
        "layer": "NB-C content semantics — Level 1/4",
        "base": "λ-terms (or combinator-encoded equivalents)",
        "gauge_group": "β-η equivalence (with α-renaming); "
                       "combinator-basis transformations as meta-gauge",
        "cohomology_classes": "β-η equivalence classes (denotations)",
        "gauge_invariant": "the semantic function (meaning of the term)",
        "introducing_move": "M1 S5 apply; M3 S/K/I commitment; M11 "
                            "meta-circular interpreter",
        "witness_evidence": "M1 S5 apply; ../scratch/chart.py:40-46 "
                            "(self.S/K/I); ../scratch/verify_shadows.py",
        "status": "shown; doubly rigidified (per-instance integer "
                  "indices + unsubstituted basis-choice SKI)",
        "notes": "β-equivalence operationalised via CBNeed apply "
                 "(Church-Rosser). Basis choice SKI is one of several "
                 "valid (SK, BCKW, raw λ). Recovery: parametrise basis.",
    },
    {
        "slug": "cy-8-substrate-impl",
        "name": "Substrate-implementation cocycle (micro-architecture)",
        "layer": "NB-D operational substrate — multi-level",
        "base": "substrate implementations satisfying the realizability "
                "charter (Morton heap, sequential, content-addressed, "
                "SIMD-packed fat nodes)",
        "gauge_group": "substrate-equivalence (any two realising same "
                       "abstract chart semantics)",
        "cohomology_classes": "charter-satisfying implementation classes",
        "gauge_invariant": "abstract chart semantics + the (Compute, "
                           "Data, State, Workspace) categorical "
                           "decomposition every substrate must provide",
        "introducing_move": "M2 + M5 + M23 (distributed)",
        "witness_evidence": "cotype-free-self-extending-grammar.md:1874-2026; "
                            "../scratch/hamming_scaling_hardware.py; "
                            "pre-M1 SIMD-packed fat-node discussion",
        "status": "partially rigidified (only Morton-coded heap "
                  "realised; alternatives unimplemented)",
        "notes": "Origin of CDSW axes — Compute/Data/State/Workspace "
                 "are substrate-architectural categories. The V_4/S_4 "
                 "structure on them (CY-5) is DOWNSTREAM of this "
                 "substrate-level origin. Per user 2026-05-15.",
    },
]


SPECIAL_STRUCTURES = [
    {
        "slug": "sp-1-metacircular-fixpoint",
        "name": "Metacircular fixed point",
        "layer": "NB-E meta-recursion — M11",
        "base": "metacircular interpreter implementations",
        "gauge_group": "(not a gauge — terminal coalgebra / fixed point)",
        "cohomology_classes": "(not classes — a unique LFP)",
        "gauge_invariant": "the LFP itself (smallest grammar containing "
                           "its own parser)",
        "introducing_move": "M11 (meta-circular fixpoint)",
        "witness_evidence": "cotype:655-713; ../scratch/chart.py "
                            "(meta-circular interpreter); "
                            "K-self-extension-closes-L5",
        "status": "shown; not a cocycle (listed for completeness)",
        "notes": "Metacircularity is the canonical term. NOT a cocycle "
                 "— has no gauge group. The LFP is the gauge-invariant "
                 "content surviving CY-1 + CY-6 + CY-7 + CY-8 "
                 "equivalences; all gauge fixings converge to SP-1. "
                 "This is what gives the storage ≡ grammar ≡ ISA "
                 "triple identification (see cocycles.md).",
    },
]


GROUP_QUOTIENTS = [
    {
        "slug": "q-z2-chirality",
        "name": "Z_2 chirality (S_4/A_4)",
        "layer": "Level 7 — directed witnessed pairs",
        "base": "24 valid signatures",
        "gauge_group": "Z_2 = S_4/A_4 via inverse-swap (source↔sink)",
        "cohomology_classes": "12 inverse-pair classes",
        "gauge_invariant": "(pair, witness) with chirality as fiber coordinate",
        "introducing_move": "M34",
        "witness_evidence": "../scratch/chirality_as_parity.py; "
                            "../scratch/directed_witnessed_pairs.py",
        "status": "shown; label-only rigidification (sign=0→even is one of "
                  "two valid conventions)",
        "notes": "Strictly a Z_2 quotient action, not a cocycle in the "
                 "M8 sense. Sign homomorphism S_4→Z_2 is canonical; only "
                 "the integer encoding and even/odd labels are "
                 "conventional.",
    },
    {
        "slug": "q-z3-3cycle",
        "name": "Z_3 = A_4/V_4 (3-cycle quotient)",
        "layer": "Level 7 — 4-axis chained operations",
        "base": "operations within a V_4 orbit (after V_4 quotient)",
        "gauge_group": "Z_3 generator",
        "cohomology_classes": "3-element orbits under Z_3",
        "gauge_invariant": "V_4 orbit class (already quotiented)",
        "introducing_move": "M37",
        "witness_evidence": "../scratch/chart_chained.py; "
                            "../scratch/verify_chained.py",
        "status": "shown",
        "notes": "Z_3 is the 4-axis chaining generator. Combined with V_4 "
                 "this yields A_4 = V_4 ⋊ Z_3.",
    },
    {
        "slug": "q-a4z2-architectural",
        "name": "A_4 × Z_2 architectural symmetry",
        "layer": "Level 8 — full architectural automorphism group",
        "base": "the 24 architectural operations",
        "gauge_group": "A_4 × Z_2 (closure of admissible generators)",
        "cohomology_classes": "single orbit (transitive action on 24 ops)",
        "gauge_invariant": "the 24-op operation set itself",
        "introducing_move": "M40 (v3-v6)",
        "witness_evidence": "../jea/metalanguage/spectral_view.py "
                            "(verify_m40_group_is_a4z2_not_s4); "
                            "../scratch/verify_spectral.py (98/98 tests)",
        "status": "shown",
        "notes": "Order 24, distinct from S_4 by center order "
                 "(|Z(A_4×Z_2)|=2 vs |Z(S_4)|=1) and order distribution. "
                 "Adding any S_3 transposition extends to S_4 × Z_2 of "
                 "order 48.",
    },
]


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cocycles (
            cocycle_id          INTEGER PRIMARY KEY,
            slug                TEXT NOT NULL UNIQUE,
            name                TEXT NOT NULL,
            kind                TEXT NOT NULL,        -- 'cocycle' | 'quotient'
            layer               TEXT NOT NULL,
            base                TEXT NOT NULL,
            gauge_group         TEXT NOT NULL,
            cohomology_classes  TEXT NOT NULL,
            gauge_invariant     TEXT NOT NULL,
            introducing_move    TEXT NOT NULL,
            witness_evidence    TEXT NOT NULL,
            status              TEXT NOT NULL,
            notes               TEXT,
            generated_at_utc    TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_cocycles_kind ON cocycles(kind);
        CREATE INDEX IF NOT EXISTS idx_cocycles_move ON cocycles(introducing_move);
    """)


def populate(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM cocycles")
    def insert(records, kind):
        for r in records:
            conn.execute("""
                INSERT INTO cocycles (slug, name, kind, layer, base, gauge_group,
                                      cohomology_classes, gauge_invariant,
                                      introducing_move, witness_evidence, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (r["slug"], r["name"], kind, r["layer"], r["base"], r["gauge_group"],
                  r["cohomology_classes"], r["gauge_invariant"],
                  r["introducing_move"], r["witness_evidence"], r["status"], r["notes"]))
    insert(COCYCLES, "cocycle")
    insert(GROUP_QUOTIENTS, "quotient")
    insert(SPECIAL_STRUCTURES, "fixed-point")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="decomposition/cotype_decomposition.sqlite")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db).resolve()
    with sqlite3.connect(db_path) as conn:
        ensure_schema(conn)
        populate(conn)
        conn.commit()
        counts = conn.execute("""
            SELECT kind, COUNT(*) FROM cocycles GROUP BY kind ORDER BY kind
        """).fetchall()
    print(f"db: {db_path}")
    for kind, n in counts:
        print(f"  {kind}: {n}")


if __name__ == "__main__":
    main()
