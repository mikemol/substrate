"""
Agda definition-shape detector.

Scans Substrate/**/*.agda for top-level definitions, extracts a "shape
signature" per definition (clause count, RHS template family), and
reports recurrence groups.

The output surfaces parameterization candidates: definitions with
"structured" clause counts (4, 6, 8, 12, 16, 24...) corresponding to
small group orders or simple products, especially when grouped by
shared RHS templates.

Per [[project-annealing-methodology]]: this script proposes; we don't.
It surfaces patterns; whether to act on them is a separate question.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")

# Suspicious clause counts — products / factorials of small numbers,
# matching common case-split structures (axis × axis, anchor × Fin 3,
# orbit-key, S_n orders, etc.).
SUSPICIOUS_COUNTS = {2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64}


def parse_module(path):
    text = path.read_text()
    m = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not m:
        return None, ""
    name = m.group(1)
    # Strip line comments and block comments.
    text = re.sub(r"--.*$", "", text, flags=re.M)
    text = re.sub(r"\{-.*?-\}", "", text, flags=re.S)
    return name, text


# A "definition" is a sequence of clauses, where each clause begins
# with an identifier at column 0 and has = on the RHS.
# Pattern: identifier followed by zero or more space-separated args
# (with possible ()), then =, then RHS until EOL or next def.
CLAUSE_RE = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*)"
    r"(\s+[^\n=]+?)?\s*=\s*([^\n]*)$",
    re.M
)


def parse_definitions(text):
    """
    Extract top-level definitions as {name: [rhs_per_clause]}.
    Crude heuristic: definitions live at column 0, clauses begin with
    the function name at col 0, RHS starts after `=`.
    """
    defs = defaultdict(list)
    for line in text.split("\n"):
        # Strip indented lines (these are continuations, not new clauses).
        if not line or line[0].isspace():
            continue
        m = CLAUSE_RE.match(line)
        if not m:
            continue
        name, _args, rhs = m.group(1), m.group(2), m.group(3)
        rhs = rhs.strip()
        # Filter out type signatures (RHS would have `:` and `→` in typical
        # patterns), record fields (with `;`), and import lines.
        if name in {"open", "import", "module", "record", "data",
                    "field", "private", "postulate", "infixl", "infixr",
                    "infix", "where"}:
            continue
        if not rhs:
            continue
        defs[name].append(rhs)
    return defs


def shape_template(rhs):
    """
    Compute a coarse RHS template by abstracting identifiers and
    literals to placeholders.
    """
    # Replace identifiers with _ (lowercase + uppercase sequences).
    t = re.sub(r"[a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*", "_", rhs)
    # Collapse runs of whitespace.
    t = re.sub(r"\s+", " ", t).strip()
    return t


def main():
    # Collect all definitions.
    all_defs = {}  # (module, name) -> [rhs per clause]
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, rhss in parse_definitions(text).items():
            all_defs[(mod, name)] = rhss

    print(f"Parsed {len(all_defs)} top-level definitions.\n")

    # === Clause-count distribution ===
    counts = Counter(len(rhss) for rhss in all_defs.values())
    print("=== Clause-count distribution ===")
    for c in sorted(counts):
        marker = "  ← suspicious" if c in SUSPICIOUS_COUNTS else ""
        print(f"  {c:3d} clauses : {counts[c]:3d} definitions{marker}")
    print()

    # === All-refl-clause definitions ===
    print("=== Definitions where every clause RHS is `refl` (parameterization candidates) ===")
    all_refl = [
        (mod, name, len(rhss)) for (mod, name), rhss in all_defs.items()
        if len(rhss) >= 4 and all(r.strip() == "refl" for r in rhss)
    ]
    all_refl.sort(key=lambda x: -x[2])
    for mod, name, n in all_refl:
        marker = "  ← STRUCTURED" if n in SUSPICIOUS_COUNTS else ""
        print(f"  {n:3d} refl-clauses: {mod.split('.')[-1]}::{name}{marker}")
    print()

    # === Shape-signature recurrence groups ===
    # Group definitions by (clause_count, sorted_template_set).
    print("=== Recurrent shape groups (definitions sharing clause-count AND template-set) ===")
    shape_to_defs = defaultdict(list)
    for (mod, name), rhss in all_defs.items():
        if len(rhss) < 4:
            continue
        templates = frozenset(shape_template(r) for r in rhss)
        sig = (len(rhss), templates)
        shape_to_defs[sig].append((mod, name))

    groups = [(sig, defs) for sig, defs in shape_to_defs.items() if len(defs) >= 2]
    groups.sort(key=lambda x: (-x[0][0], -len(x[1])))
    for (n_clauses, templates), defs in groups[:20]:
        marker = " ← STRUCTURED" if n_clauses in SUSPICIOUS_COUNTS else ""
        print(f"\n  Shape: {n_clauses} clauses, {len(templates)} distinct templates{marker}")
        if len(templates) <= 5:
            for t in sorted(templates)[:5]:
                t_short = t if len(t) < 80 else t[:77] + "..."
                print(f"    template: {t_short}")
        print(f"  Members ({len(defs)}):")
        for mod, name in defs:
            print(f"    {mod.split('.')[-1]}::{name}")


if __name__ == "__main__":
    main()
