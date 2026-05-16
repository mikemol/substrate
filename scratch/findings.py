"""
Grothendieck-construction consolidation of all structural-analysis
scripts.

Each existing detector (percentile_gaps, reachability_dual,
simplicial_shape, clause_shapes) is a functor:

    Codebase → Findings_i

at some level (module-pair, module-simplex, definition-group). Taking
∫ over the level-index packages all findings into one category, where
the objects are (level, finding) pairs and a "thick point" is an
entity-tuple witnessed by multiple scripts at multiple levels.

This script:
  1. Re-implements the key analyses inline (so it's self-contained).
  2. Emits all findings as `Finding` records with a normalized
     `objects` key (frozenset of entity names).
  3. Consolidates by `objects` — counts witnesses per entity-tuple.
  4. Outputs:
     a) Ranked table of structural facts by witness count.
     b) Cross-level refinement chains (module-pair → definitions in those modules).
     c) Empty-fiber report (levels with no witnesses).

Per [[project-annealing-methodology]]: the script proposes thick
points. We don't propose specific refactors from outside the script.
"""

import re
from pathlib import Path
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from typing import FrozenSet, Tuple, Any

import numpy as np
import networkx as nx


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")
CATALOG_ROOT = Path("/home/mikemol/github/substrate/catalog")


@dataclass(frozen=True)
class Finding:
    """A single structural-claim object from some source script."""
    level: str           # 'module-pair' | 'module-simplex' | 'def-group' | 'def-pair' | etc.
    kind: str            # script-specific category, e.g., 'jaccard-neighborhood-p90'
    objects: FrozenSet   # the entities the finding is about (set of names)
    metric: float        # primary numerical signal
    source: str          # which logical script emitted this finding
    extra: Tuple = field(default_factory=tuple)  # supplementary data


# ============================================================
# Parsing helpers
# ============================================================

def parse_module_path(path):
    text = path.read_text()
    m = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not m:
        return None, ""
    name = m.group(1)
    return name, re.sub(r"\{-.*?-\}", "", re.sub(r"--.*$", "", text, flags=re.M), flags=re.S)


def module_imports(text):
    return [imp for imp in re.findall(r"^(?:open\s+)?import\s+([A-Za-z0-9_.\-]+)", text, re.M)
            if imp.startswith("Substrate.")]


def short(name):
    return name.split("::")[-1].split(".")[-1]


def jaccard(a, b):
    if not a and not b: return 1.0
    u = a | b
    return (len(a & b) / len(u)) if u else 0.0


# ============================================================
# Source 1: module-pair Jaccards at multiple levels
# ============================================================

def collect_module_findings(graph, nodes):
    findings = []
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)

    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])
    nbr_sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Reachability closures.
    adj = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                adj[idx[src]].add(idx[dep])
    down = [set() for _ in range(n)]
    for i in range(n):
        stack, seen = [i], set()
        while stack:
            v = stack.pop()
            if v in seen: continue
            seen.add(v); stack.extend(adj[v])
        seen.discard(i)
        down[i] = seen

    # Global base.
    reach_count = [0] * n
    for i in range(n):
        for t in down[i]:
            reach_count[t] += 1
    base_modules = set(i for i in range(n) if reach_count[i] >= n // 2)

    # Compute Jaccards at each level.
    sigs = {
        "jaccard-neighborhood":     nbr_sig,
        "jaccard-reach-raw":         down,
        "jaccard-reach-base-quotient": [s - base_modules for s in down],
    }

    for kind, sig in sigs.items():
        vals = []
        for i in range(n):
            for j in range(i + 1, n):
                vals.append(jaccard(sig[i], sig[j]))
        if not vals:
            continue
        p90 = float(np.percentile(vals, 90))
        for i in range(n):
            for j in range(i + 1, n):
                jv = jaccard(sig[i], sig[j])
                if jv >= p90:
                    findings.append(Finding(
                        level="module-pair",
                        kind=f"{kind}-p90",
                        objects=frozenset({nodes[i], nodes[j]}),
                        metric=jv,
                        source="percentile_gaps",
                    ))
    return findings, base_modules


# ============================================================
# Source 2: simplicial cliques at threshold sweeps
# ============================================================

def collect_simplex_findings(graph, nodes):
    findings = []
    idx = {n_: i for i, n_ in enumerate(nodes)}
    n = len(nodes)

    out_nbr = [set() for _ in range(n)]
    in_nbr  = [set() for _ in range(n)]
    for src, deps in graph.items():
        for dep in deps:
            if dep in idx:
                out_nbr[idx[src]].add(idx[dep])
                in_nbr[idx[dep]].add(idx[src])
    sig = [out_nbr[i] | in_nbr[i] for i in range(n)]

    # Build similarity matrix.
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            J[i, j] = J[j, i] = jaccard(sig[i], sig[j])

    for theta in [0.5, 0.7, 0.8]:
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for i in range(n):
            for j in range(i + 1, n):
                if J[i, j] >= theta:
                    G.add_edge(i, j)
        for c in nx.find_cliques(G):
            if len(c) >= 3:
                findings.append(Finding(
                    level="module-simplex",
                    kind=f"max-clique-theta{theta:.1f}",
                    objects=frozenset(nodes[i] for i in c),
                    metric=float(theta),
                    source="simplicial_shape",
                ))
    return findings


# ============================================================
# Source 3: clause-shape recurrence groups (definition-level)
# ============================================================

CLAUSE_RE = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*)"
    r"(\s+[^\n=]+?)?\s*=\s*([^\n]*)$",
    re.M
)


def parse_definitions(text):
    defs = defaultdict(list)
    for line in text.split("\n"):
        if not line or line[0].isspace():
            continue
        m = CLAUSE_RE.match(line)
        if not m:
            continue
        name, _args, rhs = m.group(1), m.group(2), m.group(3).strip()
        if name in {"open", "import", "module", "record", "data", "field",
                    "private", "postulate", "infixl", "infixr", "infix", "where"}:
            continue
        if not rhs:
            continue
        defs[name].append(rhs)
    return defs


def shape_template(rhs):
    t = re.sub(r"[a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*", "_", rhs)
    return re.sub(r"\s+", " ", t).strip()


def parse_definitions_with_sig(text):
    """
    Like parse_definitions but ALSO captures the type signature line for
    each definition. Returns {name: (sig_line_or_None, [rhss])}.
    """
    out = defaultdict(lambda: [None, []])
    # First pass: collect signatures (lines like `name : Type...`).
    sig_pattern = re.compile(
        r"^([a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*)\s*:\s*(.+)$",
        re.M
    )
    for m in sig_pattern.finditer(text):
        name = m.group(1)
        if name in {"open", "import", "module", "record", "data", "field",
                    "private", "postulate", "infixl", "infixr", "infix",
                    "where", "let", "in", "with"}:
            continue
        sig = m.group(2).strip()
        # Heuristic: keep first signature seen.
        if out[name][0] is None:
            out[name][0] = sig
    # Second pass: collect clauses.
    for line in text.split("\n"):
        if not line or line[0].isspace():
            continue
        m = CLAUSE_RE.match(line)
        if not m:
            continue
        name, _args, rhs = m.group(1), m.group(2), m.group(3).strip()
        if name in {"open", "import", "module", "record", "data", "field",
                    "private", "postulate", "infixl", "infixr", "infix", "where"}:
            continue
        if not rhs:
            continue
        # Skip signature lines (RHS starts with type-like content typically
        # not = sign — but CLAUSE_RE matches `=`, so signature lines without
        # `=` won't match here. We're good).
        out[name][1].append(rhs)
    # Convert to plain dict, filter empties.
    return {name: (val[0], val[1]) for name, val in out.items() if val[1]}


def collect_clause_findings():
    findings = []
    all_defs = {}            # qname (full-module::def) -> rhss
    qname_to_module = {}     # qname -> full module name (Substrate.X.Y)
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, rhss in parse_definitions(text).items():
            qname = f"{mod}::{name}"
            all_defs[qname] = rhss
            qname_to_module[qname] = mod
    # Stash all_defs as an attribute for downstream detectors.
    collect_clause_findings.all_defs = all_defs

    # Group by (clause_count, template_set).
    shape_to_defs = defaultdict(list)
    for qname, rhss in all_defs.items():
        if len(rhss) < 4:
            continue
        templates = frozenset(shape_template(r) for r in rhss)
        sig = (len(rhss), templates)
        shape_to_defs[sig].append(qname)

    for (count, templates), members in shape_to_defs.items():
        if len(members) >= 2:
            findings.append(Finding(
                level="def-group",
                kind=f"shape-group-{count}c",
                objects=frozenset(members),
                metric=float(len(members)),
                source="clause_shapes",
                extra=(count,),
            ))

    # All-refl-clause definitions as individual findings.
    for qname, rhss in all_defs.items():
        if len(rhss) >= 4 and all(r == "refl" for r in rhss):
            findings.append(Finding(
                level="def-single",
                kind=f"all-refl-{len(rhss)}c",
                objects=frozenset({qname}),
                metric=float(len(rhss)),
                source="clause_shapes",
                extra=(len(rhss),),
            ))
    return findings, qname_to_module


# ============================================================
# Source 4a: module-triple detector (extract 3-faces of simplices).
# Filling the empty `module-triple` fiber.
# ============================================================

def collect_module_triple_findings(simplex_findings):
    """Emit explicit 3-face findings from each (≥3)-simplex."""
    findings = []
    for s in simplex_findings:
        nodes_list = sorted(s.objects)
        if len(nodes_list) < 3:
            continue
        # Every 3-subset is a face.
        for i in range(len(nodes_list)):
            for j in range(i + 1, len(nodes_list)):
                for k in range(j + 1, len(nodes_list)):
                    findings.append(Finding(
                        level="module-triple",
                        kind=f"simplex-3face-θ{s.metric:.1f}",
                        objects=frozenset({nodes_list[i], nodes_list[j], nodes_list[k]}),
                        metric=s.metric,
                        source="simplicial_shape",
                    ))
    return findings


# ============================================================
# Source 4b: def-pair detector (pairs within def-groups).
# Filling the empty `def-pair` fiber.
# ============================================================

def collect_def_pair_findings(def_group_findings):
    """Emit every pair within each def-group."""
    findings = []
    for dg in def_group_findings:
        members = sorted(dg.objects)
        for i in range(len(members)):
            for j in range(i + 1, len(members)):
                findings.append(Finding(
                    level="def-pair",
                    kind=f"def-group-pair-{int(dg.metric)}m",
                    objects=frozenset({members[i], members[j]}),
                    metric=dg.metric,
                    source="clause_shapes",
                    extra=(dg.kind,),
                ))
    return findings


# ============================================================
# Source 4c: clause-shape-pair detector (pairs of definitions sharing
# clause-template structure, cross-module).
# Filling the empty `clause-shape-pair` fiber.
# ============================================================

def collect_clause_shape_pair_findings(all_defs_with_modules):
    """
    For each pair of definitions (in possibly-different modules) whose
    clause RHSs share the same template-set, emit a finding. Distinct
    from def-group (which clusters; this enumerates pairs).
    """
    findings = []
    # Build sig -> [qname] map.
    sig_to_qnames = defaultdict(list)
    for qname, rhss in all_defs_with_modules.items():
        if len(rhss) < 2:
            continue
        templates = frozenset(shape_template(r) for r in rhss)
        sig = (len(rhss), templates)
        sig_to_qnames[sig].append(qname)
    # Emit pairs for each sig with ≥2 qnames.
    for (count, templates), qnames in sig_to_qnames.items():
        if len(qnames) < 2:
            continue
        for i in range(len(qnames)):
            for j in range(i + 1, len(qnames)):
                findings.append(Finding(
                    level="clause-shape-pair",
                    kind=f"shape-match-{count}c",
                    objects=frozenset({qnames[i], qnames[j]}),
                    metric=float(count),
                    source="clause_shapes",
                ))
    return findings


# ============================================================
# Source 4d: term-shape detector (recurrent subterm shapes within
# RHSs). Filling the empty `term-shape` fiber.
#
# Tokenize each RHS, abstract identifiers/literals to `_`, keep
# operators/punctuation. Group RHSs by their token-shape signature.
# Recurrent signatures with ≥3 occurrences are findings.
# ============================================================

TOKEN_RE = re.compile(
    r"[a-zA-Z_][a-zA-Z0-9_\-'≢≈₁₂₃₄₅₆₇₈₉₀ⁿᵐ⁻ᵖᵃˢⁱ]*"  # identifiers
    r"|[(){};,]"                                          # punctuation
    r"|[+\-*/=<>≡≢≈→←↔⇒∘·⁻⁺λ∧∨¬]+"                    # operators
)


def term_shape(rhs):
    """Tokenize RHS and abstract identifiers to `_`, keeping structure."""
    tokens = TOKEN_RE.findall(rhs)
    out = []
    for t in tokens:
        if re.match(r"^[a-zA-Z_]", t):
            out.append("_")
        else:
            out.append(t)
    return " ".join(out)


def collect_term_shape_findings(all_defs_with_modules):
    """For each RHS, compute term-shape and find recurrent shapes."""
    shape_to_owners = defaultdict(list)  # shape -> [(qname, clause_idx)]
    for qname, rhss in all_defs_with_modules.items():
        for idx, rhs in enumerate(rhss):
            shape = term_shape(rhs)
            if len(shape) < 5:  # filter trivial 1-2-token shapes (most refl etc.)
                continue
            shape_to_owners[shape].append((qname, idx))

    findings = []
    for shape, owners in shape_to_owners.items():
        if len(owners) < 3:
            continue
        # Use the qnames as objects (collapse multiple-clauses-per-def).
        qnames = frozenset(q for q, _ in owners)
        if len(qnames) < 2:
            continue
        findings.append(Finding(
            level="term-shape",
            kind=f"recurrent-term-{len(owners)}occ",
            objects=qnames,
            metric=float(len(owners)),
            source="term_shapes",
            extra=(shape,),
        ))
    return findings


# ============================================================
# Source 4e: def-level Jaccard — lift module-level analysis to
# (module, def) granularity. Same operations: each def is a node;
# edges are "def A uses def B's name in its body".
# ============================================================

def build_def_usage_graph(all_defs):
    """
    Build {qname → set of qnames it references}.
    A qname is `Substrate.X.Y::name`. We match short names against bodies.
    """
    short_to_qnames = defaultdict(list)
    for qname in all_defs:
        short = qname.split("::", 1)[1]
        short_to_qnames[short].append(qname)
    # Compile patterns for performance.
    patterns = {
        short: re.compile(r"(?<![A-Za-z0-9_\-'])" + re.escape(short) + r"(?![A-Za-z0-9_\-'])")
        for short in short_to_qnames
    }
    out_nbr = defaultdict(set)
    for src_qname, rhss in all_defs.items():
        body = " ".join(rhss)
        src_short = src_qname.split("::", 1)[1]
        for short, pat in patterns.items():
            if short == src_short:
                continue
            if pat.search(body):
                for tgt_qname in short_to_qnames[short]:
                    if tgt_qname != src_qname:
                        out_nbr[src_qname].add(tgt_qname)
    return out_nbr


def collect_orbit_findings():
    """
    For each pair of definitions across modules:
      1. Capture signature + RHS clauses.
      2. Tokenize each into a token sequence.
      3. Two definitions are 'orbit-equivalent under substitution σ' if:
         their token sequences differ only by replacing each occurrence
         of some identifier `a` in one with `a'` in the other, consistently.
      4. Emit a finding for each orbit (group of mutually-orbit-equivalent defs).

    This is the QUOTIENT detector: defs that are the same shape modulo
    a consistent renaming. The renaming = "which module-or-helper
    distinguishes them" the user asked about.
    """
    # Re-parse with signatures.
    all_defs_full = {}  # qname -> (sig, [rhss])
    qname_to_module = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, (sig, rhss) in parse_definitions_with_sig(text).items():
            qname = f"{mod}::{name}"
            all_defs_full[qname] = (sig or "", rhss)
            qname_to_module[qname] = mod

    # Build token sequence for each def: sig + " || " + concatenated RHSs.
    def def_tokens(qname):
        sig, rhss = all_defs_full[qname]
        body = " || ".join(rhss)
        whole = f"{sig} || {body}"
        return TOKEN_RE.findall(whole)

    # Two token sequences are orbit-equivalent if they have the same
    # length and the same "shape skeleton" (operators + punctuation +
    # position-of-identifier-occurrences) AND there's a consistent
    # identifier-to-identifier bijection between them.
    def skeleton(tokens):
        """Replace each identifier with a position-stable placeholder."""
        seen = {}
        out = []
        for t in tokens:
            if re.match(r"^[a-zA-Z_]", t):
                if t not in seen:
                    seen[t] = f"#{len(seen)}"
                out.append(seen[t])
            else:
                out.append(t)
        return tuple(out)

    # Group qnames by skeleton.
    sk_groups = defaultdict(list)
    for qname in all_defs_full:
        toks = def_tokens(qname)
        if len(toks) < 8:  # filter tiny defs
            continue
        sk_groups[skeleton(toks)].append(qname)

    findings = []
    for sk, qnames in sk_groups.items():
        if len(qnames) < 2:
            continue
        findings.append(Finding(
            level="orbit",
            kind=f"shape-quotient-{len(qnames)}m",
            objects=frozenset(qnames),
            metric=float(len(qnames)),
            source="orbit_detector",
            extra=(len(sk),),  # skeleton length as side info
        ))
    return findings


def collect_partial_coset_findings():
    """
    Galois-of-orbit-almost-filled detector with parametric-counterpart
    annotation. Surfaces definitions whose names contain a specific
    constructor of a known finite type AND reports whether a parametric
    counterpart exists elsewhere (a definition with the same stem but
    no constructor suffix, OR with the finite type as an explicit
    parameter in its signature).

    Per user: a partial coset is a partial coset regardless of counterpart
    existence — the asymmetry will crop up as a refl annoyance
    somewhere. But the parametric counterpart, when it exists, gives
    structural guidance for how to annealing-step-close the partial
    coset (since the parametric shape is already there to instantiate).
    """
    finite_types = {
        "Axis":      ["D", "C", "S", "W"],
        "V₄":        ["e", "α", "β", "γ"],
        "Pairing":   ["α-pair", "β-pair", "γ-pair"],
        "Chirality": ["even", "odd"],
        "Bool":      ["true", "false"],
    }

    # Collect all definition names + signatures.
    all_defs_full = {}  # (mod, name) → signature (or '')
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, (sig, rhss) in parse_definitions_with_sig(text).items():
            all_defs_full[(mod, name)] = sig or ""

    all_def_names_by_short = defaultdict(list)
    for (mod, name) in all_defs_full:
        all_def_names_by_short[name].append((mod, name))

    def find_parametric_counterpart(stem, ty):
        """
        Look for a definition that could be the parametric counterpart:
          1. A definition named exactly `stem` (no constructor suffix).
          2. A definition named `stem` with a signature containing
             `(_ : <ty>)` or `(<name> : <ty>)`.
        Returns list of qnames (one per match) or [].
        """
        candidates = []
        if stem in all_def_names_by_short:
            for mod, name in all_def_names_by_short[stem]:
                sig = all_defs_full.get((mod, name), "")
                # Check if signature mentions the type — heuristic.
                if ty in sig or f"Axis" in sig:  # 'Axis' as the most common
                    candidates.append(f"{mod}::{name}")
                else:
                    # Even without explicit Axis parameter, the stem-match
                    # is suggestive (might use the type implicitly).
                    candidates.append(f"{mod}::{name}")
        return candidates

    findings = []
    for ty, ctors in finite_types.items():
        ctor_set = set(ctors)
        stem_to_ctor_qnames = defaultdict(dict)
        for (mod, name) in all_defs_full:
            for c in ctors:
                if name.endswith("-" + c) or name.endswith("_" + c):
                    stem = name[: -(len(c) + 1)]
                    stem_to_ctor_qnames[stem].setdefault(c, []).append((mod, name))
                    continue
                marker = "-" + c + "-"
                if marker in name:
                    stem = name.replace(marker, "-", 1).rstrip("-")
                    stem_to_ctor_qnames[stem].setdefault(c, []).append((mod, name))
        for stem, ctor_map in stem_to_ctor_qnames.items():
            present = set(ctor_map.keys())
            missing = ctor_set - present
            if missing and present and len(present) < len(ctors):
                # Look for parametric counterpart.
                counterpart = find_parametric_counterpart(stem, ty)
                findings.append(Finding(
                    level="partial-coset",
                    kind=f"missing-{ty}-ctors",
                    objects=frozenset(
                        f"{mod}::{n}" for c, qnames in ctor_map.items() for mod, n in qnames
                    ),
                    metric=float(len(present)),
                    source="partial_coset_detector",
                    extra=(ty, tuple(sorted(present)), tuple(sorted(missing)),
                           stem, tuple(counterpart)),
                ))
    return findings


def collect_orbit_suborbit_connections(orbit_findings):
    """
    For each pair of orbits (parent, child), detect when the parent's
    members reference the child's members through a 1-1 correspondence
    at varying token positions.

    These are the points where parametric HELPERS belong: a helper
    indexed by the child orbit's parameter would collapse the parent.
    """
    # Re-parse definitions with sigs (needed to capture varying tokens).
    all_defs_full = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, (sig, rhss) in parse_definitions_with_sig(text).items():
            qname = f"{mod}::{name}"
            all_defs_full[qname] = (sig or "", rhss)

    def def_tokens(qname):
        sig, rhss = all_defs_full.get(qname, ("", []))
        body = " || ".join(rhss)
        whole = f"{sig} || {body}"
        return TOKEN_RE.findall(whole)

    def def_shorts(qnames):
        return {q.split("::")[1] for q in qnames}

    # Index: short-name → orbit (membership lookup).
    short_to_orbit = {}
    for orb in orbit_findings:
        for q in orb.objects:
            short_to_orbit.setdefault(q.split("::")[1], []).append(orb)

    # Also: track per-orbit varying-token sets for the "no suborbit, but
    # here are the varying tokens" output.
    orbit_varying = []  # (orbit, [(position, sorted_distinct_tokens)])

    connections = []
    for parent in orbit_findings:
        members = sorted(parent.objects)
        token_seqs = [def_tokens(m) for m in members]
        if not all(token_seqs) or len({len(ts) for ts in token_seqs}) > 1:
            continue
        varying = []
        for p in range(len(token_seqs[0])):
            tokens_p = [ts[p] for ts in token_seqs]
            distinct = sorted(set(tokens_p))
            if len(distinct) > 1:
                varying.append((p, distinct))
        orbit_varying.append((parent, varying))
        # Strict match (token-set == child orbit's members).
        for child in orbit_findings:
            if child.objects == parent.objects:
                continue
            child_shorts = def_shorts(child.objects)
            for p, distinct in varying:
                tokens_set = set(distinct)
                if tokens_set == child_shorts:
                    connections.append((parent, child, p, distinct, "exact"))
                    break
        # Subset match (token-set covers child orbit's members partially).
        for child in orbit_findings:
            if child.objects == parent.objects:
                continue
            child_shorts = def_shorts(child.objects)
            for p, distinct in varying:
                tokens_set = set(distinct)
                if tokens_set < child_shorts or child_shorts < tokens_set:
                    overlap = tokens_set & child_shorts
                    if len(overlap) >= 2:
                        connections.append((parent, child, p, sorted(overlap), "partial"))
                        break
    return connections, orbit_varying


def collect_def_level_jaccard_findings(all_defs):
    """Emit def-level pair findings above P90 Jaccard."""
    out_nbr = build_def_usage_graph(all_defs)
    in_nbr = defaultdict(set)
    for src, tgts in out_nbr.items():
        for t in tgts:
            in_nbr[t].add(src)
    qnames = sorted(all_defs.keys())
    sig = {q: out_nbr[q] | in_nbr[q] for q in qnames}
    # Compute Jaccards; filter by nontrivial neighborhood.
    pairs = []
    for i, q1 in enumerate(qnames):
        if not sig[q1]:
            continue
        for q2 in qnames[i + 1:]:
            if not sig[q2]:
                continue
            jv = jaccard(sig[q1], sig[q2])
            if jv > 0:
                pairs.append((jv, q1, q2))
    if not pairs:
        return []
    p90 = float(np.percentile([p[0] for p in pairs], 90))
    findings = []
    for jv, q1, q2 in pairs:
        if jv >= p90:
            findings.append(Finding(
                level="def-pair",
                kind="def-jaccard-p90",
                objects=frozenset({q1, q2}),
                metric=jv,
                source="def_level_jaccard",
            ))
    return findings


# ============================================================
# Source 4: catalog-claim detector (filling a previously-empty fiber)
#
# Catalog claims are referenced from Agda modules via comment lines like:
#   -- See: catalog/cocycles.md § CY-N — <human description>
# The claim itself lives in the catalog/*.md file. The set of modules
# that reference a given claim is the claim's MATERIALIZATION FOOTPRINT —
# the cohomology section over the catalog at the module level.
# ============================================================

CATALOG_REF_RE = re.compile(
    r"catalog/(\w+\.md)\s*§\s*([^—\n]+?)(?:\s*—|\s*$|\s*;|\s*\.)",
    re.M | re.IGNORECASE
)


def collect_catalog_findings():
    """
    Build a map: catalog-claim (file, §-key) → set of Agda modules referencing it.
    Emit one finding per claim, with the referencing modules as the objects.
    """
    claim_to_modules = defaultdict(set)
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        # Re-read raw (we want comments).
        raw = path.read_text()
        for m in CATALOG_REF_RE.finditer(raw):
            catalog_file, key = m.group(1).strip(), m.group(2).strip().rstrip("—.;").strip()
            claim_to_modules[(catalog_file, key)].add(mod)

    findings = []
    for (cat_file, key), mods in claim_to_modules.items():
        # The claim itself is one of the "objects" — represent as a synthetic
        # entity name so it consolidates with other findings about the same claim.
        claim_name = f"catalog::{cat_file}§{key}"
        # Emit as a finding with the modules as objects, the claim name in extra.
        findings.append(Finding(
            level="catalog-claim",
            kind="materialization-footprint",
            objects=frozenset(mods),
            metric=float(len(mods)),
            source="catalog_claims",
            extra=(claim_name,),
        ))
        # Also emit pair-refinements: each (claim, module) pair gets a
        # 2-object finding so consolidation at the module level picks
        # up the claim as another witness.
        for mod in mods:
            findings.append(Finding(
                level="module-pair",
                kind=f"catalog-claim-refinement",
                objects=frozenset({mod, claim_name}),
                metric=float(len(mods)),
                source="catalog_claims",
                extra=(key,),
            ))
    return findings, claim_to_modules


# ============================================================
# Consolidation: the Grothendieck total category
# ============================================================

def main():
    # Build module graph.
    graph = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, text = parse_module_path(path)
        if name and name.startswith("Substrate"):
            graph[name] = module_imports(text)
    nodes = sorted(graph.keys())

    print(f"Modules: {len(nodes)}\n")

    # Collect findings from all three sources.
    findings = []
    mod_findings, base = collect_module_findings(graph, nodes)
    findings.extend(mod_findings)
    findings.extend(collect_simplex_findings(graph, nodes))
    clause_f, qname_to_module = collect_clause_findings()
    findings.extend(clause_f)
    all_defs = collect_clause_findings.all_defs

    # Build derived findings.
    simplex_findings = [f for f in findings if f.level == "module-simplex"]
    def_group_findings = [f for f in findings if f.level == "def-group"]
    findings.extend(collect_module_triple_findings(simplex_findings))
    findings.extend(collect_def_pair_findings(def_group_findings))
    findings.extend(collect_clause_shape_pair_findings(all_defs))
    findings.extend(collect_term_shape_findings(all_defs))
    findings.extend(collect_def_level_jaccard_findings(all_defs))
    findings.extend(collect_orbit_findings())
    findings.extend(collect_partial_coset_findings())

    catalog_f, claim_to_modules = collect_catalog_findings()
    findings.extend(catalog_f)

    print(f"Total findings emitted: {len(findings)}")
    for lvl in ["module-pair", "module-triple", "module-simplex",
                "def-pair", "def-group", "def-single",
                "clause-shape-pair", "term-shape", "orbit",
                "partial-coset", "catalog-claim"]:
        n = sum(1 for f in findings if f.level == lvl)
        if n > 0:
            print(f"  {lvl:18s} : {n}")
    print()

    # === Dependency analysis between findings ===
    # For each pair of partial-coset findings (F1, F2), F1 depends on F2 if
    # any F2 member's short name appears in any F1 member's body or signature.
    # Leaves (no outgoing deps among finding-set) are smallest annealing steps.
    pc_findings_list = [f for f in findings if f.level == "partial-coset"]

    # Rebuild all_defs_full to access bodies + sigs by qname.
    _defs_text = {}
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, (sig, rhss) in parse_definitions_with_sig(text).items():
            qname = f"{mod}::{name}"
            _defs_text[qname] = (sig or "") + " || " + " ".join(rhss)

    def member_tokens(qname):
        return set(TOKEN_RE.findall(_defs_text.get(qname, "")))

    finding_deps = {i: set() for i in range(len(pc_findings_list))}
    for i, f1 in enumerate(pc_findings_list):
        f1_token_union = set()
        for m1 in f1.objects:
            f1_token_union |= member_tokens(m1)
        for j, f2 in enumerate(pc_findings_list):
            if i == j: continue
            for m2 in f2.objects:
                m2_short = m2.split("::")[-1]
                if m2_short in f1_token_union:
                    finding_deps[i].add(j)
                    break

    leaves = [i for i in range(len(pc_findings_list)) if not finding_deps[i]]

    # 2-deep: cousins. Two partial-coset findings (P1, P2) are cousins
    # if some third finding P3 has both as dependencies, OR if they share
    # a common name-stem prefix/template indicating they're parametric
    # instances of a higher-order pattern.
    # Reverse-deps: for each finding, who depends on it?
    rev_deps = {i: set() for i in range(len(pc_findings_list))}
    for i, deps in finding_deps.items():
        for j in deps:
            rev_deps[j].add(i)

    # Build cousin graph: undirected edges between findings sharing an
    # upstream dependent.
    cousin_edges = defaultdict(set)
    for i in range(len(pc_findings_list)):
        upstream = rev_deps[i]  # findings that depend on i
        if not upstream:
            continue
        # Find other findings j that share an upstream dependent with i.
        for j in range(len(pc_findings_list)):
            if j == i: continue
            shared = upstream & rev_deps[j]
            if shared:
                cousin_edges[i].add((j, frozenset(shared)))

    # Group into cousin clusters (connected components).
    cousin_clusters = []
    visited = set()
    for i in range(len(pc_findings_list)):
        if i in visited: continue
        cluster = set()
        stack = [i]
        while stack:
            v = stack.pop()
            if v in visited: continue
            visited.add(v)
            cluster.add(v)
            for (j, _) in cousin_edges[v]:
                if j not in visited:
                    stack.append(j)
        if len(cluster) >= 2:
            cousin_clusters.append(cluster)

    # Partial-coset detector (Galois-of-orbit-almost-filled).
    partial_findings = sorted(
        ((f.metric, f.extra, f.objects, i) for i, f in enumerate(pc_findings_list)),
        key=lambda x: (0 if x[3] in leaves else 1, -x[0], x[1])
    )
    if partial_findings:
        print("=== Partial coset interactions (Galois of orbit-almost-filled) ===")
        print("  Definition-name stems where some constructors of a finite type are")
        print("  represented but others are missing. Each partial coset IS the finding;")
        print("  the parametric counterpart, when listed, is bonus structural guidance.")
        print()
        print(f"  Leaves (no outgoing dependencies on other partial-coset findings) listed first.")
        print(f"  Total: {len(pc_findings_list)} findings, {len(leaves)} leaves, "
              f"{len(pc_findings_list) - len(leaves)} non-leaves.")
        print()
        for metric, extra, members, idx in partial_findings:
            ty, present, missing, stem, counterparts = extra
            members_short = sorted(short(o) for o in members)
            leaf_marker = "  [LEAF]" if idx in leaves else "       "
            print(f"{leaf_marker} [{ty}]  stem '{stem}': "
                  f"present={list(present)}, MISSING={list(missing)}")
            if counterparts:
                cp_names = ", ".join(c.split("::")[-1] for c in counterparts)
                print(f"           parametric counterpart: {cp_names}")
            for m in members_short:
                print(f"    · {m}")
            # Show dependencies on other findings.
            if finding_deps[idx]:
                dep_stems = sorted({
                    pc_findings_list[d].extra[3] for d in finding_deps[idx]
                })
                print(f"           depends on stems: {dep_stems}")
            print()

        # 2-deep: cousin clusters.
        absorbed_members = set()         # finding indices in COMPLETE-VIA-UPSTREAM clusters
        promoted_leaves_via_cluster = set()  # upstream findings that are next-to-tackle
        if cousin_clusters:
            print("  --- Cousin clusters (2-deep: findings sharing an upstream dependent) ---")
            for cluster in cousin_clusters:
                cluster_stems = sorted(pc_findings_list[i].extra[3] for i in cluster)
                # Find shared upstream dependent(s) — intersection of rev_deps.
                shared = None
                for i in cluster:
                    shared = rev_deps[i] if shared is None else (shared & rev_deps[i])
                shared_stems = (sorted({pc_findings_list[s].extra[3] for s in shared})
                                if shared else [])
                # Check if upstream's deps EXACTLY cover the cluster.
                structurally_complete = False
                completing_upstream = None
                if shared:
                    for upstream_idx in shared:
                        upstream_deps = finding_deps[upstream_idx]
                        if cluster <= upstream_deps:
                            structurally_complete = True
                            completing_upstream = upstream_idx
                            break
                marker = "[COMPLETE-VIA-UPSTREAM]" if structurally_complete else "[partial]"
                print(f"    cluster {marker}: {cluster_stems}")
                if shared_stems:
                    print(f"      common upstream finding(s): {shared_stems}")
                if structurally_complete:
                    absorbed_members |= cluster
                    promoted_leaves_via_cluster.add(completing_upstream)
                    upstream_stem = pc_findings_list[completing_upstream].extra[3]
                    print(f"      The upstream depends on the full cluster; positional")
                    print(f"      coverage is handled there. Individual cousins'")
                    print(f"      'missing' siblings would be false propositions.")
                    print(f"      → Next-leaf-to-tackle: '{upstream_stem}' (was non-leaf,")
                    print(f"        now effectively a leaf since its deps are absorbed).")
                print()

        # === Effective leaves after cluster absorption ===
        # A finding becomes an "effective leaf" when its dependencies are all
        # in absorbed-members. Strict leaves PLUS findings whose remaining
        # dependencies are entirely in COMPLETE-VIA-UPSTREAM clusters.
        effective_leaves = []
        for i in range(len(pc_findings_list)):
            if i in absorbed_members:
                continue  # cluster member, not an independent leaf
            if not finding_deps[i] or finding_deps[i] <= absorbed_members:
                effective_leaves.append(i)
        # Sort: explicitly promoted ones first, then strict leaves.
        promoted = [i for i in effective_leaves if i in promoted_leaves_via_cluster]
        strict = [i for i in effective_leaves if i not in promoted_leaves_via_cluster]

        print("  --- Effective leaves (NEXT-TO-TACKLE this iteration) ---")
        print(f"    Strict leaves (no deps): {len(strict)}")
        print(f"    Promoted from cousin clusters (upstream of absorbed cluster): {len(promoted)}")
        for i in promoted:
            stem = pc_findings_list[i].extra[3]
            present = pc_findings_list[i].extra[1]
            missing = pc_findings_list[i].extra[2]
            print(f"      PROMOTED: stem='{stem}', present={list(present)}, MISSING={list(missing)}")
        if not promoted:
            print(f"      (no promotions this iteration)")
        print()

    # Orbit-suborbit connections (helper-belongs-here detector).
    orbit_findings = [f for f in findings if f.level == "orbit"]
    connections, orbit_varying = collect_orbit_suborbit_connections(orbit_findings)
    print("=== Orbit ⇄ suborbit connections (helper-placement candidates) ===")
    if connections:
        print("  When parent orbit's varying-token-set at some position matches")
        print("  (or overlaps) a child orbit's members, a helper parameterized")
        print("  by the child IS the natural way to collapse the parent.")
        print()
        for parent, child, pos, tokens, kind in connections:
            parent_short = sorted(short(o) for o in parent.objects)
            child_short = sorted(short(o) for o in child.objects)
            print(f"  [{kind}] parent: {{{', '.join(parent_short)}}}")
            print(f"          child:  {{{', '.join(child_short)}}}")
            print(f"          varying tokens at pos {pos}: {{{', '.join(tokens)}}}")
            print()
    else:
        print("  No orbit-suborbit matches found (exact or subset).")
    print()

    # Always show the varying tokens for each orbit (even with no
    # suborbit match) — these are the "parameters a helper would take".
    print("=== Per-orbit varying tokens (helper-parameter signatures) ===")
    for parent, varying in orbit_varying:
        members = sorted(short(o) for o in parent.objects)
        if not varying:
            continue
        print(f"  orbit {{{', '.join(members)}}}")
        for p, distinct in varying[:5]:
            print(f"    pos {p}: {distinct}")
        if len(varying) > 5:
            print(f"    ... and {len(varying) - 5} more positions")
        print()

    # Orbit findings (shape-quotient detections).
    print("=== Orbits (shape-quotient candidates) ===")
    print("  Definitions whose (signature, body) tokenize to the same shape-")
    print("  skeleton modulo a consistent identifier-bijection. These are")
    print("  parameterization candidates: one parametric definition could")
    print("  replace each orbit.")
    print()
    orbit_findings = sorted(
        ((f.metric, f.objects) for f in findings if f.level == "orbit"),
        key=lambda x: -x[0]
    )
    for n, members in orbit_findings:
        m_short = sorted(short(q) for q in members)
        print(f"  [{int(n)}-element orbit] {{{', '.join(m_short)}}}")
    print()

    # Catalog-claim materialization footprints.
    print("=== Catalog-claim materialization footprints ===")
    print("  (Each catalog claim referenced by N Agda modules → that's its cohomology")
    print("   section's support at the module level.)")
    print()
    cc_findings = sorted(
        ((f.metric, f.extra[0], f.objects) for f in findings if f.level == "catalog-claim"),
        key=lambda x: -x[0]
    )
    for n, claim, mods in cc_findings[:15]:
        claim_short = claim.replace("catalog::", "").replace(".md", "")
        print(f"  [{int(n)} materializing modules] {claim_short}")
        for m in sorted(mods):
            print(f"    · {m.split('.')[-1]}")
    print()

    # === Refinement morphisms (Grothendieck construction): each
    # higher-level finding REFINES to the implied lower-level findings.
    # A simplex {A,B,C} witnesses pairs {A,B}, {A,C}, {B,C}. A def-group
    # spanning modules {A,B} witnesses the pair {A,B}.
    refined = list(findings)
    # Simplex → pairs.
    for f in findings:
        if f.level == "module-simplex":
            nodes_list = sorted(f.objects)
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    refined.append(Finding(
                        level="module-pair",
                        kind=f"simplex-refinement-θ{f.metric:.1f}",
                        objects=frozenset({nodes_list[i], nodes_list[j]}),
                        metric=f.metric,
                        source="simplicial_shape",
                    ))
    # Def-group → module-pairs (every pair of distinct modules covered).
    for f in findings:
        if f.level == "def-group":
            mods = sorted({qname_to_module.get(q, q.split("::")[0]) for q in f.objects})
            for i in range(len(mods)):
                for j in range(i + 1, len(mods)):
                    refined.append(Finding(
                        level="module-pair",
                        kind=f"def-group-refinement-{int(f.metric)}m",
                        objects=frozenset({mods[i], mods[j]}),
                        metric=f.metric,
                        source="clause_shapes",
                        extra=(f.kind,),
                    ))
    findings = refined
    print(f"After refinements: {len(findings)} findings\n")

    # === Consolidate by objects (the Grothendieck thick-point computation) ===
    by_objects = defaultdict(list)
    for f in findings:
        by_objects[f.objects].append(f)

    # Witness-count distribution.
    wc_dist = Counter(len(fs) for fs in by_objects.values())
    print("=== Witness-count distribution ===")
    for wc in sorted(wc_dist.keys(), reverse=True):
        print(f"  {wc} witnesses : {wc_dist[wc]} entity-tuples")
    print()

    # === Thick points: entities witnessed ≥3 times ===
    thick = [(len(fs), objs, fs) for objs, fs in by_objects.items() if len(fs) >= 3]
    thick.sort(key=lambda x: -x[0])
    print("=== Thick points (≥3 witnesses) ===")
    for wc, objs, fs in thick[:25]:
        ent = ", ".join(short(o) for o in sorted(objs))
        srcs = ", ".join(sorted({f.source for f in fs}))
        kinds = ", ".join(sorted({f.kind for f in fs}))
        print(f"  [{wc} witnesses, {len(set(f.source for f in fs))} sources]: {{{ent}}}")
        print(f"    sources: {srcs}")
        print(f"    kinds: {kinds}")
    print()

    # === Cross-level refinement chains ===
    # For each module-pair finding, look for definition-pair / def-group
    # findings whose modules match.
    print("=== Cross-level refinements (module-pair witnessed AND has def-group inside) ===")
    module_pairs = [f for f in findings if f.level == "module-pair"]
    def_groups = [f for f in findings if f.level == "def-group"]

    def def_module(qname):
        return qname.split("::")[0]

    cross_count = 0
    for mp in module_pairs[:50]:
        if mp.metric < 0.8:  # only look at strong pairs
            continue
        mod_set = {n.split(".")[-1] for n in mp.objects}
        for dg in def_groups:
            dg_mods = {def_module(q) for q in dg.objects}
            if mod_set.issubset(dg_mods) and len(dg_mods) <= len(mod_set) + 1:
                ent = ", ".join(short(o) for o in sorted(mp.objects))
                dgent = ", ".join(short(o) for o in sorted(dg.objects))
                print(f"  module-pair {{{ent}}} (J={mp.metric:.2f})")
                print(f"    refines into def-group ({dg.kind}, {int(dg.metric)} members)")
                print(f"    {{{dgent}}}")
                cross_count += 1
                if cross_count >= 8:
                    break
        if cross_count >= 8:
            break
    print()

    # === Inverse refinements: for each thick pair, find ambient containers
    # (simplices it's a face of; def-groups whose modules span it). This is
    # the contravariant direction of the refinement morphism — given a
    # finding at level L, list all findings at level L+1 that refine TO it.
    print("=== Inverse refinements: ambient context per thick point ===")
    print("    (A thick pair → which simplices/def-groups contain it as a face?)")
    print()
    # Index simplices and def-groups by their objects sets.
    simplices = [f for f in findings if f.level == "module-simplex"]
    def_groups = [f for f in findings if f.level == "def-group"]
    pair_findings = sorted(
        ((len(fs), objs) for objs, fs in by_objects.items() if len(objs) == 2),
        key=lambda x: -x[0]
    )
    pair_findings = [(wc, objs) for wc, objs in pair_findings if wc >= 4]
    for wc, pair in pair_findings[:12]:
        ent = ", ".join(short(o) for o in sorted(pair))
        containing_simplices = [s for s in simplices if pair.issubset(s.objects)]
        spanning_defgroups = []
        for dg in def_groups:
            dg_mods = {qname_to_module.get(q, q.split("::")[0]) for q in dg.objects}
            if pair.issubset(dg_mods):
                spanning_defgroups.append(dg)
        print(f"  [{wc}-witness pair] {{{ent}}}")
        if containing_simplices:
            for s in containing_simplices[:2]:
                s_ent = ", ".join(short(o) for o in sorted(s.objects))
                print(f"    ⊂ simplex (θ={s.metric:.1f}, n={len(s.objects)}): {{{s_ent}}}")
        if spanning_defgroups:
            for dg in spanning_defgroups[:2]:
                print(f"    ⊂ def-group ({dg.kind}, {int(dg.metric)} defs)")
        if not containing_simplices and not spanning_defgroups:
            print(f"    (no ambient simplex or def-group contains this pair)")
    print()

    # === Empty fibers ===
    print("=== Empty fibers (levels with no findings or under-populated) ===")
    levels = {f.level for f in findings}
    expected_levels = {"module-pair", "module-simplex", "module-triple",
                       "def-group", "def-single", "def-pair",
                       "clause-shape-pair", "term-shape", "catalog-claim"}
    missing = expected_levels - levels
    print(f"  Currently populated levels: {sorted(levels)}")
    print(f"  Missing levels: {sorted(missing)}")
    print(f"  → Each missing level is a next-detector candidate.")


if __name__ == "__main__":
    main()
