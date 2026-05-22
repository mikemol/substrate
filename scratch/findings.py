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
    # Convert to plain dict, filter empties. Include defs that have
    # EITHER a signature OR clauses — covers absurd-pattern defs like
    # `e-pair : ⊥ → Pairing  ;  e-pair ()` (no = clause, but real def).
    return {name: (val[0], val[1]) for name, val in out.items() if val[0] or val[1]}


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


def _feed_data_declaration_ctors(all_defs_full=None):
    """Feeder #1: Agda data-declaration constructors.

    Returns {type_name: [ctor_names]}, extracted from `data X : Set
    where` blocks in source. Plus Bool as a builtin fallback.
    """
    finite_types = {}
    data_decl_re = re.compile(
        r"^\s*data\s+([A-Za-z_][A-Za-z0-9_\-'₀-₉]*).*?:\s*Set.*?where\s*$",
        re.M,
    )
    ctor_line_re = re.compile(r"^\s+([^:]+?)\s*:\s*([^\s].*?)$")
    ident_re = re.compile(r"[A-Za-z_α-ωΑ-Ω₀-₉][A-Za-z0-9_\-'₀-₉α-ωΑ-Ω]*")
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        lines = text.split("\n")
        i = 0
        while i < len(lines):
            m = data_decl_re.match(lines[i])
            if m:
                ty_name = m.group(1)
                ctors = []
                j = i + 1
                while j < len(lines):
                    line = lines[j]
                    if not line.strip():
                        break
                    if not line.startswith(" ") and not line.startswith("\t"):
                        break
                    cm = ctor_line_re.match(line)
                    if cm:
                        names_part, type_part = cm.group(1), cm.group(2)
                        if type_part == ty_name or type_part.startswith(ty_name + " "):
                            ctors.extend(ident_re.findall(names_part))
                    j += 1
                if ctors:
                    finite_types.setdefault(ty_name, ctors)
                i = j
            else:
                i += 1
    finite_types.setdefault("Bool", ["true", "false"])
    return finite_types


def _longest_common_suffix(strings):
    """Longest string that's a suffix of every input string."""
    if not strings:
        return ""
    s0 = strings[0]
    for i in range(len(s0), 0, -1):
        suffix = s0[-i:]
        if all(s.endswith(suffix) for s in strings):
            return suffix
    return ""


def _feed_sig_return_defs(pool, all_defs_full):
    """Feeder #2: defs whose name matches the common-suffix pattern
    of existing ctors AND whose signature returns the type.

    For each type T in the pool:
      1. Compute the longest common suffix of T's existing ctors.
      2. If the suffix is meaningful (≥2 chars OR starts with '-'/'_'),
         scan all defs for names ending in that suffix.
      3. Admit those defs to pool[T] if their signature's tail
         identifier matches T.

    Example: Pairing's ctors {α-pair, β-pair, γ-pair} share suffix
    '-pair'. A def `e-pair : ⊥ → Pairing` ends with '-pair' AND
    returns Pairing → admitted to pool[Pairing], closing the
    V₄→Pairing cross-type fanout.

    The common-suffix filter prevents over-admission: Axis's ctors
    {C, D, S, W} share no common suffix, so arbitrary defs returning
    Axis (like `act-axis`, `axis-of-v`) are NOT auto-admitted.
    """
    tail_ident_re = re.compile(r"[A-Za-z_α-ωΑ-Ω₀-₉][\w\-'α-ωΑ-Ω₀-₉]*\s*$")
    for ty_name, ctors in list(pool.items()):
        if len(ctors) < 2:
            continue
        suffix = _longest_common_suffix(ctors)
        if not suffix or (len(suffix) < 2 and not suffix.startswith(("-", "_"))):
            continue
        for (mod, name), sig in all_defs_full.items():
            if not sig:
                continue
            if name in pool[ty_name]:
                continue
            if name == ty_name:
                continue  # skip the type itself
            if not name.endswith(suffix):
                continue
            m = tail_ident_re.search(sig.rstrip())
            if not m:
                continue
            tail = m.group(0).strip()
            tail_leaf = tail.split(".")[-1]
            if tail_leaf == ty_name:
                pool[ty_name].append(name)
    return pool


def _build_ctor_pool(all_defs_full):
    """Compose feeders into a unified ctor pool.

    The pool is a single source of truth that detectors read from.
    Adding a new way of recognizing "ctor-like names" means adding a
    feeder, not changing every detector. Data-declaration ctors are
    one feeder among many; other feeders (sig-return, naming-pattern,
    etc.) extend the pool compositionally.
    """
    pool = _feed_data_declaration_ctors(all_defs_full)
    pool = _feed_sig_return_defs(pool, all_defs_full)
    return pool


def collect_partial_coset_findings():
    """
    Galois-of-orbit-almost-filled detector with parametric-counterpart
    annotation. Surfaces definitions whose names contain a constructor
    of a known finite type — where "constructor" is whatever the ctor
    pool admits (data-declaration ctors plus other feeders' admissions).

    Per user: a partial coset is a partial coset regardless of counterpart
    existence — the asymmetry will crop up as a refl annoyance
    somewhere. But the parametric counterpart, when it exists, gives
    structural guidance for how to annealing-step-close the partial
    coset (since the parametric shape is already there to instantiate).
    """
    # Collect all definition names + signatures.
    all_defs_full = {}  # (mod, name) → signature (or '')
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        mod, text = parse_module_path(path)
        if not mod or not mod.startswith("Substrate"):
            continue
        for name, (sig, rhss) in parse_definitions_with_sig(text).items():
            all_defs_full[(mod, name)] = sig or ""

    # Build the unified ctor pool. Detectors below consume from this
    # pool, not the raw data-declaration ctors. Feeders compose into
    # the pool; adding a new way of recognizing ctor-like names means
    # adding a feeder, not changing the detectors.
    finite_types = _build_ctor_pool(all_defs_full)

    all_def_names_by_short = defaultdict(list)
    for (mod, name) in all_defs_full:
        all_def_names_by_short[name].append((mod, name))

    def find_parametric_counterpart(stem, ty):
        candidates = []
        if stem in all_def_names_by_short:
            for mod, name in all_def_names_by_short[stem]:
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

    # Cross-type ctor-stem-extension detector. For each pair of types
    # (T1, T2), check whether T2's ctors look like "T1.ctor + suffix"
    # for some common suffix. If most-but-not-all T1 ctors have such
    # an extension, the missing ctors form a CROSS-TYPE partial coset
    # — a signal that one type's "ctor space" is partially indexed by
    # another's, with some ctors of T1 lacking a T2 counterpart.
    #
    # Example: V₄ = {e, α, β, γ}, Pairing = {α-pair, β-pair, γ-pair}.
    # Pairing ctors are V₄.{α,β,γ} + "-pair"; V₄.e has no counterpart.
    # Whether the missing 'e-pair' is structurally required or an
    # intentional quotient is a downstream interpretation question;
    # the detector just surfaces the asymmetry.
    type_list = sorted(finite_types.keys())
    for t1 in type_list:
        for t2 in type_list:
            if t1 == t2:
                continue
            # Group: suffix → list of (t1_ctor matched, t2_ctor)
            suffix_groups = defaultdict(list)
            for c1 in finite_types[t1]:
                for c2 in finite_types[t2]:
                    if c2 == c1:
                        continue
                    # T2 ctor = T1 ctor + delimited suffix.
                    for delim in ("-", "_", ""):
                        prefix = c1 + delim
                        if c2.startswith(prefix) and len(c2) > len(prefix):
                            suffix_groups[delim + c2[len(prefix):]].append((c1, c2))
                            break
            for suffix, matches in suffix_groups.items():
                covered = sorted({c1 for c1, _ in matches})
                missing_t1 = sorted(set(finite_types[t1]) - set(covered))
                if len(covered) >= 2 and missing_t1:
                    # Genuine cross-type stem-extension pattern with
                    # some ctors uncovered.
                    findings.append(Finding(
                        level="partial-coset",
                        kind=f"cross-type-{t1}-to-{t2}-via-suffix",
                        objects=frozenset(
                            f"<cross-type::{t1}.{c1}→{t2}.{c2}>"
                            for c1, c2 in matches
                        ),
                        metric=float(len(covered)),
                        source="cross_type_ctor_detector",
                        extra=(f"{t1}→{t2}", tuple(covered), tuple(missing_t1),
                               f"{t1}{suffix}", tuple()),
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

        # === Speculative shape-match: for each partial-coset finding's
        # missing constructors, search the codebase for existing
        # definitions whose name/signature shape suggests they ARE the
        # missing sibling (just under a different naming convention,
        # e.g., case difference, lower/upper swap, hyphen variant).
        # Speculative — surface candidates the strict detector can't
        # match directly. Useful for finding "this is what we have, the
        # naming just differs."
        print("  --- Speculative shape-matches for missing siblings ---")
        # Build a name → signature map across the whole codebase.
        _name_to_qnames = defaultdict(list)
        for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
            mod, text = parse_module_path(path)
            if not mod or not mod.startswith("Substrate"):
                continue
            for nm, (sig, rhss) in parse_definitions_with_sig(text).items():
                _name_to_qnames[nm].append((mod, sig or "", rhss))

        spec_count = 0
        for f in pc_findings_list:
            ty, present, missing, stem, _ = f.extra
            # Per-finding ctor universe; no hardcoded type→ctors map.
            ctors = sorted(set(present) | set(missing))
            # Get one of the present-ctor's qnames for shape baseline.
            if not f.objects:
                continue
            baseline_qname = next(iter(f.objects))
            baseline_short = baseline_qname.split("::")[-1]
            baseline_sig = ""
            for mod, sig, rhss in _name_to_qnames.get(baseline_short, []):
                baseline_sig = sig
                break
            for missing_c in missing:
                hypotheticals = []
                # Build candidate names for the missing constructor.
                hypotheticals.append(stem + "-" + missing_c)
                hypotheticals.append(stem + "-" + missing_c.lower())
                hypotheticals.append(stem.replace("-" + missing_c.lower() + "-",
                                                   "-" + missing_c.lower() + "-")
                                     + "-" + missing_c)
                # If stem itself has a lowercase ctor token, try the swap.
                for c2 in ctors:
                    c2_lower = c2.lower()
                    if "-" + c2_lower + "-" in stem and c2 != missing_c:
                        # The stem already names another ctor in lowercase;
                        # try swapping.
                        swap_stem = stem.replace("-" + c2_lower + "-",
                                                  "-" + missing_c.lower() + "-")
                        hypotheticals.append(swap_stem + "-" + missing_c)
                        hypotheticals.append(swap_stem)
                # Look for hypotheticals in the name map.
                seen = set()
                for hyp in hypotheticals:
                    if hyp in seen: continue
                    seen.add(hyp)
                    if hyp in _name_to_qnames:
                        for mod, sig, rhss in _name_to_qnames[hyp]:
                            spec_count += 1
                            if spec_count <= 10:
                                print(f"    stem '{stem}' missing '{missing_c}':")
                                print(f"      candidate: {mod}::{hyp}")
                                print(f"      (existing definition; naming convention differs)")
        if spec_count == 0:
            print("    (no speculative matches found)")
        elif spec_count > 10:
            print(f"    ... and {spec_count - 10} more speculative matches.")
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

    # === PROPOSED ACTIONS — synthesizing the structure into concrete steps ===
    print("=== PROPOSED ACTIONS (synthesized next-iteration steps) ===")
    print("  Each proposal names a concrete code change AND its expected detector")
    print("  effect. Listed in priority order: structural collapses first, then")
    print("  speculative renames, then additive siblings, then accepts.")
    print()

    proposals_count = 0

    # 1. EXACT orbit-suborbit collapses (clearest structural fix).
    exact_connections = [
        (p, c, pos, toks, k) for (p, c, pos, toks, k) in connections if k == "exact"
    ]
    if exact_connections:
        # Build (once) the data needed to surface existing-parametric-helper
        # candidates: def-level usage graph + ELABORATED type signatures
        # from scratch/.agda_types.json (built by scratch/agda_types.py).
        #
        # Score every candidate def by Jaccard across THREE orthogonal
        # similarity dimensions:
        #   - dep-J: Jaccard of def-level dependencies vs the UNION of
        #     orbit members' deps.
        #   - sig-J-asis: Jaccard of AsIs-elaborated signature tokens.
        #     Captures structural identity (Stab-C ≠ Stab-D distinct).
        #   - sig-J-norm: Jaccard of Normalised-elaborated signature
        #     tokens. Captures definitional equality (orbit members
        #     normalise to the same shape modulo one axis token).
        # Rank by the PRODUCT of all three: a candidate must look like
        # the orbit in EVERY dimension to score high. A zero in any
        # dimension zeros out the candidate.
        def_usage_for_collapse = build_def_usage_graph(all_defs)

        # Load the elaborated-types cache. If absent or stale-and-
        # unbuildable, fall back to regex-parsed signatures with a
        # warning. The cache key format matches our qname format:
        # "Substrate.<Mod>.<Path>::<def-name>".
        try:
            from agda_types import load_cache as _agda_load_cache, cache_is_stale as _agda_cache_stale, discover_modules as _agda_discover
            _elab_cache = _agda_load_cache()
            if _elab_cache and _agda_cache_stale(_agda_discover()):
                print(f"      (note: .agda_types.json is STALE relative to source"
                      f" — rerun `python scratch/agda_types.py --force` to refresh)")
        except ImportError:
            _elab_cache = {}
        if not _elab_cache:
            print(f"      (note: no .agda_types.json cache found — sig-J dimensions"
                  f" will be empty. Run `python scratch/agda_types.py` once to build it.)")

        # Token extraction from elaborated types. Agda emits fully-
        # qualified identifiers like `Substrate.Groups.Stab-S3.Stab`.
        # We split on whitespace and parens, then for each qualified
        # token take both the leaf name AND the full path; this lets
        # us match either at the level of "same operator name" or
        # "same module-path origin".
        _split_re = re.compile(r"[\s\(\)\{\}\[\],→]+")
        def _elab_tokens(s):
            out = set()
            for raw in _split_re.split(s or ""):
                raw = raw.strip().rstrip(".")
                if not raw:
                    continue
                if raw in {":", "→", "=", "λ", ".", "...", "_"}:
                    continue
                out.add(raw)
                if "." in raw:
                    out.add(raw.split(".")[-1])
            return out

        def _elab_sig(qname, mode):
            entry = _elab_cache.get(qname)
            if not entry:
                return ""
            return entry.get(mode, "")

        print("  [1] EXACT orbit-suborbit collapses (highest priority):")
        for parent, child, pos, tokens, _ in exact_connections:
            parent_qnames = set(parent.objects)
            child_qnames = set(child.objects)
            parent_short = sorted(short(o) for o in parent.objects)
            child_short = sorted(short(o) for o in child.objects)
            proposals_count += 1
            print(f"    PROPOSAL #{proposals_count}: collapse parent orbit")
            print(f"      Parent members: {{{', '.join(parent_short)}}}")
            print(f"      Child members:  {{{', '.join(child_short)}}}")
            print(f"      Action: replace the {len(parent.objects)} parent definitions with")
            print(f"              ONE parametric helper indexed by the child set.")
            print(f"      Expected effect: parent orbit closes; helper may compose with")
            print(f"              other parametric structures (transposition, extend, etc.).")

            # Surface existing definitions that LOOK structurally like the
            # parametric helper we'd want. Three orthogonal Jaccard
            # dimensions per candidate:
            #   - dep-J:      Jaccard against UNION of member deps.
            #   - sig-J-asis: Jaccard against UNION of AsIs-elaborated sig
            #                 tokens. (Structural identity preserved.)
            #   - sig-J-norm: Jaccard against UNION of Normalised-elaborated
            #                 sig tokens. (Definitional equality unfolded.)
            # Rank by PRODUCT (dep-J × sig-J-asis × sig-J-norm). Any zero
            # dimension zeros out the candidate.
            #
            # core-coverage (fraction of orbit's shared primitive deps
            # the candidate uses) shown for context — sharp variant of
            # dep dimension that's useful even when dep-J is low.
            member_deps = [def_usage_for_collapse.get(q, set()) for q in parent_qnames]
            union_deps = (set().union(*member_deps) if member_deps else set())
            intersection_deps = (set.intersection(*member_deps)
                                 if member_deps and all(member_deps) else set())
            axis_short_names = {"C", "S", "W", "D"}
            def _is_axis_dep(q):
                return q.split("::")[-1] in axis_short_names
            union_deps = {q for q in union_deps - parent_qnames - child_qnames
                          if not _is_axis_dep(q)}
            intersection_deps = {q for q in intersection_deps - parent_qnames - child_qnames
                                 if not _is_axis_dep(q)}
            # Elaborated signature tokens per orbit member, at both
            # AsIs and Normalised levels.
            member_short_names = {q.split("::")[-1] for q in parent_qnames}
            # Axis-token suffixes to strip from token sets (these are
            # what VARIES across the orbit). Strip both bare axis
            # constructor names and their per-axis specializations
            # like "Stab-C" / "orbit-key-to-stab-C".
            member_asis = [_elab_tokens(_elab_sig(q, "asis")) for q in parent_qnames]
            member_norm = [_elab_tokens(_elab_sig(q, "normalised")) for q in parent_qnames]
            union_asis = set().union(*member_asis) if member_asis else set()
            union_norm = set().union(*member_norm) if member_norm else set()
            # Symmetric difference is what varies across the orbit; the
            # INTERSECTION is the parametric-shape skeleton.
            inter_asis = (set.intersection(*member_asis)
                          if member_asis and all(member_asis) else set())
            inter_norm = (set.intersection(*member_norm)
                          if member_norm and all(member_norm) else set())
            # Strip orbit member self-references and bare axis names
            # from all token sets (they're trivially "shared" or
            # trivially "varying").
            _strip = member_short_names | axis_short_names
            for s in (union_asis, union_norm, inter_asis, inter_norm):
                s -= _strip

            if intersection_deps or inter_asis or inter_norm:
                # The parametric helpers the orbit ALREADY uses are
                # exactly the intersection of member-deps (minus axis
                # constructors). Surface these prominently: they ARE
                # the answer to "what existing helpers already have
                # the right shape — the orbit composes them."
                primitives = sorted({q.split("::")[-1] for q in intersection_deps})
                if primitives:
                    print(f"      Existing parametric helpers USED by every orbit member:")
                    print(f"        {{{', '.join(primitives)}}}")
                    print(f"        (these are the parametric primitives the orbit composes;")
                    print(f"         a unified form wraps them with ONE Axis-like parameter,")
                    print(f"         replacing the {len(parent.objects)} specialised member defs.)")
                # Display intersections with leaf-name only (de-dup the
                # qualified+leaf double-counting we keep in the matching
                # token sets).
                def _display_leaf(tokens):
                    return sorted({t.split(".")[-1] if "." in t else t for t in tokens})
                if inter_asis:
                    sample = _display_leaf(inter_asis)[:8]
                    n = len({t.split(".")[-1] if "." in t else t for t in inter_asis})
                    suffix = f", … (+{n - 8})" if n > 8 else ""
                    print(f"      Shared AsIs sig-tokens (orbit identity): {{{', '.join(sample)}{suffix}}}")
                if inter_norm:
                    sample = _display_leaf(inter_norm)[:8]
                    n = len({t.split(".")[-1] if "." in t else t for t in inter_norm})
                    suffix = f", … (+{n - 8})" if n > 8 else ""
                    print(f"      Shared Normalised sig-tokens (definitional skeleton): {{{', '.join(sample)}{suffix}}}")

            candidates = []
            for qname in all_defs:
                if qname in parent_qnames or qname in child_qnames:
                    continue
                cand_deps_raw = def_usage_for_collapse.get(qname, set())
                cand_deps = {q for q in cand_deps_raw - parent_qnames - child_qnames
                             if not _is_axis_dep(q)}
                cand_asis = _elab_tokens(_elab_sig(qname, "asis")) - _strip
                cand_norm = _elab_tokens(_elab_sig(qname, "normalised")) - _strip
                core = (len(cand_deps & intersection_deps) / len(intersection_deps)
                        if intersection_deps else 0.0)
                dep_j = jaccard(cand_deps, union_deps) if union_deps else 0.0
                asis_j = jaccard(cand_asis, union_asis) if union_asis else 0.0
                norm_j = jaccard(cand_norm, union_norm) if union_norm else 0.0
                product = dep_j * asis_j * norm_j
                if product <= 0.0:
                    continue
                candidates.append((product, core, dep_j, asis_j, norm_j, qname))
            candidates.sort(reverse=True)
            top = candidates[:5]
            if top:
                print(f"      Candidate existing parametric helpers (dot-product rank):")
                print(f"        (rank = dep-J × sig-J-asis × sig-J-norm — all three")
                print(f"         dimensions must be nonzero. AsIs preserves structural")
                print(f"         identity, Normalised exposes definitional equality.)")
                for product, core, dep_j, asis_j, norm_j, qname in top:
                    mod = qname.split("::")[0]
                    nm = qname.split("::")[-1]
                    mod_short = mod.split(".")[-1] if "." in mod else mod
                    flag = "  ← FULL primitive coverage" if core >= 0.999 else ""
                    print(f"        - {mod_short}.{nm}{flag}")
                    print(f"            product={product:.3f}  (dep={dep_j:.2f}, asis={asis_j:.2f}, norm={norm_j:.2f}, core={core:.2f})")
            else:
                # Fall back to two-dimensional product if 3-D was too
                # strict (likely when one elaborated dimension is empty
                # because the cache is missing or sparse for this orbit).
                fallback = []
                for qname in all_defs:
                    if qname in parent_qnames or qname in child_qnames:
                        continue
                    cand_deps_raw = def_usage_for_collapse.get(qname, set())
                    cand_deps = {q for q in cand_deps_raw - parent_qnames - child_qnames
                                 if not _is_axis_dep(q)}
                    cand_asis = _elab_tokens(_elab_sig(qname, "asis")) - _strip
                    cand_norm = _elab_tokens(_elab_sig(qname, "normalised")) - _strip
                    dep_j = jaccard(cand_deps, union_deps) if union_deps else 0.0
                    asis_j = jaccard(cand_asis, union_asis) if union_asis else 0.0
                    norm_j = jaccard(cand_norm, union_norm) if union_norm else 0.0
                    # 2-D fallback: dep × max(asis, norm). Catches the
                    # "candidate matches in dep + at LEAST one sig
                    # dimension" case.
                    best_sig = max(asis_j, norm_j)
                    product2 = dep_j * best_sig
                    if product2 <= 0.0:
                        continue
                    fallback.append((product2, dep_j, asis_j, norm_j, qname))
                fallback.sort(reverse=True)
                top2 = fallback[:5]
                if top2:
                    print(f"      No candidates match all 3 dimensions; falling back")
                    print(f"      to 2-D dot-product: dep-J × max(asis-J, norm-J):")
                    for product2, dep_j, asis_j, norm_j, qname in top2:
                        mod = qname.split("::")[0]
                        nm = qname.split("::")[-1]
                        mod_short = mod.split(".")[-1] if "." in mod else mod
                        print(f"        - {mod_short}.{nm}")
                        print(f"            product2={product2:.3f}  (dep={dep_j:.2f}, asis={asis_j:.2f}, norm={norm_j:.2f})")
                else:
                    print(f"      No existing parametric-helper candidates found.")
                    print(f"      (No def has nonzero similarity in BOTH the dep AND any")
                    print(f"       sig dimension.) → The helper must be NEWLY constructed;")
                    print(f"       the inferred signature above gives the shape.")
            print()

    # ====================================================================
    # Reasoning-trace infrastructure.
    #
    # Each PROPOSAL emitted below carries a TRACE block that shows the
    # chain of OBSERVATIONS that produced it: what the detectors saw, what
    # cross-references fired, what alternative readings were considered
    # and rejected. The trace is what justifies the proposal — without
    # it, a reader can only take the conclusion on faith.
    # ====================================================================

    # Orbit-membership: for each qname, list the orbit findings it's in.
    # NOTE: `orbit_findings` got rebound to (metric, objects) tuples
    # earlier in main(); re-fetch the Finding objects fresh here.
    _orbit_findings_fresh = [f for f in findings if f.level == "orbit"]
    orbits_by_qname = defaultdict(list)
    for of in _orbit_findings_fresh:
        for q in of.objects:
            orbits_by_qname[q].append(of)

    # Per-partial-coset speculative-match map: finding-idx → list of
    # (missing_axis, candidate-qname). Re-computed here so the trace can
    # cite alternatives. This duplicates the logic that builds
    # spec_proposals but indexes per-finding instead of per-(stem,name).
    pc_spec_matches = defaultdict(list)
    for i, f in enumerate(pc_findings_list):
        ty, present, missing, stem, _ = f.extra
        # Use this finding's own ctor universe (present∪missing); no
        # hardcoded per-type list. Case-collapse search only applies
        # when the ctors have distinct upper/lower forms.
        ctors = sorted(set(present) | set(missing))
        member_short = {q.split("::")[-1] for q in f.objects}
        for missing_c in missing:
            ml = missing_c.lower()
            if ml == missing_c:
                # No case distinction — try exact stem+ctor only.
                candidates = [stem + "-" + missing_c]
            else:
                candidates = [stem + "-" + ml] + [
                    stem.replace("-" + c2.lower() + "-",
                                 "-" + ml + "-")
                    for c2 in ctors if c2 != missing_c
                    and c2.lower() != c2
                    and "-" + c2.lower() + "-" in stem
                ]
            for name in candidates:
                if name in _name_to_qnames and name not in member_short:
                    for mod, sig, rhss in _name_to_qnames[name]:
                        pc_spec_matches[i].append((missing_c, f"{mod}::{name}"))
                    break

    # Cousin-cluster lookup: for each finding, the cluster (if any) that
    # absorbs it, plus the cousin-membership map for trace lines.
    finding_cluster = {}
    for cluster_idx, members in enumerate(cousin_clusters):
        for m in members:
            finding_cluster[m] = (cluster_idx, members)

    # Motif classifier: recognises recurring structural patterns in
    # the (present, missing) shape. Important distinction the classifier
    # CAN'T make from (present, missing) alone:
    #
    #   * ANCHOR-FANOUT: 3 elements form an unordered symmetric fiber,
    #     1 distinguished "anchor". No ordering on the 3 at this level.
    #   * HODGE-DUAL: like anchor-fanout BUT the 3 carry ordering info
    #     (cyclic, sequential, …) — making the 4th their dual rather
    #     than just an anchor.
    #
    # Detecting Hodge-dual requires looking at the 3 elements' usage at
    # a higher level (e.g., whether they're cycled by s3-cycles, or
    # form a sequence). The motif name surfaces the SHAPE; whether
    # to call it Hodge-dual is a higher-level call the trace flags
    # but doesn't decide.
    def _classify_motif(present, missing):
        total = len(present) + len(missing)
        p, m = len(present), len(missing)
        if total == 4 and p == 3 and m == 1:
            return ("3-of-4 / ANCHOR-FANOUT",
                    f"3 elements {sorted(present)} form a fiber; missing "
                    f"'{list(missing)[0]}' is structurally distinguished (anchor). "
                    f"WHETHER this is a Hodge dual depends on the 3 carrying "
                    f"ordering info (cyclic, sequential) at a downstream level — "
                    f"at the type-ctor level alone there's no ordering, so this "
                    f"is anchor-fanout by default")
        if total == 4 and p == 1 and m == 3:
            return ("1-of-4 / ANCHOR-ONLY",
                    f"present element '{list(present)[0]}' is the distinguished "
                    f"anchor; the 3-element fiber {sorted(missing)} is absent at "
                    f"this stem. Dual view of the same anchor-fanout shape")
        if total == 3 and p == 2 and m == 1:
            return ("2-of-3 / Z₂-WEDGE",
                    f"two of three positions in a 3-element fiber; "
                    f"missing '{list(missing)[0]}' breaks a potential cyclic "
                    f"symmetry — if the 3 are cyclically ordered at a downstream "
                    f"level this is a wedge; if unordered it's just 2-of-3")
        if total == 2 and p == 1 and m == 1:
            return ("1-of-2 / PARITY-BREAK",
                    f"half of a 2-element parity pair; the other parity "
                    f"'{list(missing)[0]}' is missing")
        if p == total:
            return ("COMPLETE", "all ctors present")
        if p > 1 and m > 1:
            return (f"{p}-of-{total} / SUB-COSET",
                    f"partial coverage with multiple present and multiple missing; "
                    f"may indicate a sub-structure rather than a clean motif")
        return (None, None)

    def _emit_trace_for_pc(idx, kind_label):
        """Print a reasoning trace for partial-coset finding at idx.

        kind_label is one of PROMOTED / STRICT / SPECULATIVE — informs
        the closing implication line."""
        f = pc_findings_list[idx]
        ty, present, missing, stem, cps = f.extra
        members_short = sorted({q.split("::")[-1] for q in f.objects})
        member_qnames = sorted(f.objects)
        # [a] Observed defs.
        print(f"      TRACE:")
        if len(member_qnames) <= 3:
            for q in member_qnames:
                mod = q.split("::")[0]
                nm = q.split("::")[-1]
                print(f"        [a] observed def: {mod.split('.')[-1]}.{nm}")
        else:
            print(f"        [a] observed defs ({len(member_qnames)}): "
                  f"{', '.join(members_short[:5])}"
                  f"{', …' if len(member_qnames) > 5 else ''}")
        # [b] Stem extraction — also surface any LOWERCASE axis markers
        # embedded in the stem itself. The partial-coset detector strips
        # the uppercase suffix; if a lowercase axis token (-d-, -c-, etc.)
        # is in the middle of the stem, that's a separate, MEANINGFUL
        # signal (e.g., '-d-' marks the cocycle's chirality anchor under
        # the use-vs-commit convention). The speculative-match detector
        # case-collapses to find candidates, but the marker itself is
        # semantically distinct from the matching uppercase axis.
        print(f"        [b] stem extraction: '{stem}' (after stripping a {ty} suffix)")
        # Lowercase axis markers — derived from this finding's own ctor
        # set (present∪missing). If a lowercased version of any ctor
        # appears inside the stem, that's a SEPARATE signal carried in
        # the name itself (typically a use-vs-commit chirality marker).
        type_ctors = sorted(set(present) | set(missing))
        embedded_lower_axes = []
        for c in type_ctors:
            cl = c.lower()
            if cl == c:
                continue  # ctor isn't case-distinct (e.g. lowercase ctors like α-pair)
            marker = "-" + cl + "-"
            if marker in stem:
                pos = stem.index(marker) + 1
                embedded_lower_axes.append((cl, pos))
            end_marker = "-" + cl
            if stem.endswith(end_marker):
                pos = len(stem) - 1
                embedded_lower_axes.append((cl, pos))
        if embedded_lower_axes:
                marks = ", ".join(f"'{a}' at pos {p}" for a, p in embedded_lower_axes)
                print(f"            stem contains lowercase axis marker(s): {marks}")
                print(f"            these are NOT counted in present/missing (uppercase-only");
                print(f"            detector), but they encode a separate signal — typically")
                print(f"            a chirality anchor under the use-vs-commit convention")
                print(f"            (the cocycle USES this axis without COMMITTING to it).")
        # [c] Axis analysis. Derive the type's ctor set from THIS
        # finding's data — present + missing IS the full type's ctor
        # set (the detector built present/missing to partition it).
        # No hardcoded type→ctors map needed: the partition is the
        # data, and "missing" only has meaning relative to it.
        all_axes = sorted(set(present) | set(missing))
        print(f"        [c] {ty} ctors {all_axes}; present={list(present)}, "
              f"missing={list(missing)}")
        # [d] Orbit-membership of members. Cross-link the orbit's
        # per-axis coverage with this finding's missing set. The orbit-
        # siblings have DIFFERENT stems (each axis carries its own
        # stem like orbit-key-to-stab-X-fixes for varying X); the per-
        # sibling axis is extracted from the trailing axis token.
        #
        # Coverage universe: derived from BOTH cosets being compared —
        # the finding's expected axes (present∪missing) AND the orbit-
        # siblings' suffix-axes (extracted from their qnames). The
        # cross-product of these two cosets defines what we're
        # checking coverage of. No hardcoded ctor list.
        all_ctors = sorted(set(present) | set(missing))
        orbits_seen = set()
        for q in f.objects:
            for of in orbits_by_qname.get(q, []):
                orbits_seen.add(of)
        if orbits_seen:
            for of in sorted(orbits_seen, key=lambda x: -len(x.objects)):
                others = sorted({q.split("::")[-1] for q in of.objects} - set(members_short))
                # Extract each sibling's axis from its trailing token,
                # checking against the finding's known ctor universe
                # (all_ctors = present∪missing). Siblings whose
                # trailing token isn't in that universe are skipped —
                # they're not part of the coset we're checking against.
                sibling_axes = set()
                for o in of.objects:
                    on = o.split("::")[-1]
                    for c in all_ctors:
                        if on.endswith("-" + c):
                            sibling_axes.add(c)
                            break
                covered = sibling_axes & set(missing)
                # The orbit also has its OWN axis (the present one for
                # this finding's def). All axes covered by the orbit =
                # sibling_axes ∪ {present}.
                orbit_axes_total = sibling_axes | set(present)
                print(f"        [d] orbit-membership: this def is in a "
                      f"{len(of.objects)}-element orbit")
                if others:
                    print(f"            orbit-siblings: {', '.join(others[:5])}"
                          f"{', …' if len(others) > 5 else ''}")
                print(f"            orbit covers axes: {sorted(orbit_axes_total)}")
                if covered:
                    if covered == set(missing):
                        print(f"            ALL missing axes {sorted(missing)} ARE")
                        print(f"            covered by orbit-siblings → the parametric")
                        print(f"            family is COMPLETE; the per-stem partial-coset")
                        print(f"            view fragments it into {len(of.objects)} apparent")
                        print(f"            'incomplete' findings (stem-extraction artifact).")
                    else:
                        uncov = sorted(set(missing) - covered)
                        print(f"            orbit-siblings cover missing axes: "
                              f"{sorted(covered)}; uncovered: {uncov} → orbit-fanout-PARTIAL")
                else:
                    print(f"            orbit's axes don't intersect this finding's "
                          f"missing set → orbit is structurally independent")
        else:
            print(f"        [d] orbit-membership: none (this def is not in any "
                  f"shape-quotient orbit)")
        # [e] Speculative cross-name matches per missing axis.
        spec = pc_spec_matches.get(idx, [])
        if spec:
            print(f"        [e] speculative matches under naming-convention-relaxation:")
            for axis, cand in spec:
                cand_mod = cand.split("::")[0].split(".")[-1]
                cand_nm = cand.split("::")[-1]
                print(f"            missing '{axis}' ← existing {cand_mod}.{cand_nm}")
        else:
            print(f"        [e] no speculative cross-name matches for the missing axes")
        # [f] Cluster status.
        if idx in finding_cluster:
            ci, members = finding_cluster[idx]
            cl_size = len(members)
            print(f"        [f] cousin-cluster status: member of cluster "
                  f"#{ci} ({cl_size} sibling findings)")
        elif idx in promoted_leaves_via_cluster:
            print(f"        [f] cousin-cluster status: PROMOTED — upstream "
                  f"cluster absorbs this finding's dependencies")
        else:
            print(f"        [f] cousin-cluster status: STRICT leaf "
                  f"(no upstream cluster, no dependencies on other findings)")
        # [g] Parametric counterpart.
        if cps:
            cp_names = ", ".join(c.split("::")[-1] for c in cps)
            print(f"        [g] parametric counterpart in scope: {cp_names}")
        else:
            print(f"        [g] no parametric counterpart found by short-name lookup")
        # [h] Implication — joins the separate signals above into a
        # combined reading, with JUSTIFIED rationale for the join.
        # Use the SAME sibling-axis-extraction as [d] so the coverage
        # numbers in [h] match [d]'s.
        spec_covers = {axis for axis, _ in spec}
        orbit_covers = set()
        for of in orbits_seen:
            for o in of.objects:
                on = o.split("::")[-1]
                for c in all_ctors:
                    if on.endswith("-" + c):
                        if c in missing:
                            orbit_covers.add(c)
                        break
        fully_covered = (spec_covers | orbit_covers) >= set(missing)
        is_promoted = idx in promoted_leaves_via_cluster
        # Promoted findings: cousin-cluster ABSORPTION is the dominant
        # signal even when spec/orbit don't cover. Don't claim "no
        # upstream signal" when [f] says PROMOTED.
        if is_promoted:
            print(f"        [h] IMPLICATION: PROMOTED — cousin cluster covers this "
                  f"finding's dependencies; closure is at the cluster level, not "
                  f"the per-sibling level. No new code unless you want explicit "
                  f"per-axis names.")
        elif fully_covered:
            via = []
            if orbit_covers >= set(missing): via.append("orbit-fanout")
            elif orbit_covers: via.append(f"orbit-fanout-partial({sorted(orbit_covers)})")
            if spec_covers >= set(missing): via.append("speculative-match")
            elif spec_covers: via.append(f"speculative-match-partial({sorted(spec_covers)})")
            print(f"        [h] IMPLICATION: missing axes are FULLY COVERED via "
                  f"{' + '.join(via)}; the partial coset is structurally CLOSED at "
                  f"a higher level. The asymmetry is a stem-extraction artifact, "
                  f"not a missing-code TODO.")
        elif spec_covers or orbit_covers:
            uncovered = sorted(set(missing) - spec_covers - orbit_covers)
            covered_via = []
            if orbit_covers: covered_via.append(f"orbit-fanout({sorted(orbit_covers)})")
            if spec_covers: covered_via.append(f"speculative-match({sorted(spec_covers)})")
            print(f"        [h] IMPLICATION: PARTIAL coverage of missing axes via "
                  f"{' + '.join(covered_via)}; uncovered={uncovered}. Closing the "
                  f"uncovered portion requires either adding siblings (verify "
                  f"provability first) or accepting the residual asymmetry.")
        else:
            print(f"        [h] IMPLICATION: no upstream signal closes the missing "
                  f"axes; either the siblings are unprovable (structural truth) "
                  f"or the type really IS expected to have all {len(all_axes)} ctors "
                  f"but only {len(present)} are realised at this stem.")
        # [i] Motif classification — surfaces project-wide recurring
        # patterns. The 3-vs-4 / Hodge-dual motif is the dominant one:
        # one element of a 4-ctor type plays an identity/dual role to
        # the other 3. Naming it explicitly lets the reader connect
        # this finding to others sharing the same structural shape.
        motif_name, motif_desc = _classify_motif(present, missing)
        if motif_name:
            print(f"        [i] motif: {motif_name}")
            print(f"            {motif_desc}")

    # 2. SPECULATIVE name-matches (rename or alias). Per-finding ctor
    # universe = present∪missing (data-derived, no hardcoded list).
    spec_proposals = []
    for f in pc_findings_list:
        ty, present, missing, stem, _ = f.extra
        ctors = sorted(set(present) | set(missing))
        for missing_c in missing:
            ml = missing_c.lower()
            if ml == missing_c:
                candidates = [stem + "-" + missing_c]
            else:
                candidates = [stem + "-" + ml] + [
                    stem.replace("-" + c2.lower() + "-",
                                 "-" + ml + "-")
                    for c2 in ctors if c2 != missing_c
                    and c2.lower() != c2
                    and "-" + c2.lower() + "-" in stem
                ]
            for name in candidates:
                if name in _name_to_qnames and name not in {f.split("::")[-1] for f in f.objects}:
                    spec_proposals.append((stem, missing_c, name))
                    break

    # ====================================================================
    # Codomain enumeration: for each proposal, list ALL possible actions
    # (the codomain), rate each with justification, then recommend.
    # Per user methodology: separate signals → joined signal (with
    # justification) → codomain of possible solutions → rating →
    # end-to-end justified rationale for each option.
    # ====================================================================
    def _emit_codomain_for_pc(idx):
        f = pc_findings_list[idx]
        ty, present, missing, stem, cps = f.extra
        spec = pc_spec_matches.get(idx, [])
        is_promoted = idx in promoted_leaves_via_cluster
        # Coverage universe derived from this finding's own coset (no
        # hardcoded ctor list); orbit-siblings whose suffix isn't in
        # this universe are out-of-scope for the cross-coset check.
        all_ctors = sorted(set(present) | set(missing))
        # Orbit-coverage: extract each sibling's own axis (from its
        # trailing axis token) and intersect with this finding's
        # missing set. Same logic as [d] in the trace.
        orbits_seen = set()
        for q in f.objects:
            for of in orbits_by_qname.get(q, []):
                orbits_seen.add(of)
        orbit_covers = set()
        for of in orbits_seen:
            for o in of.objects:
                on = o.split("::")[-1]
                for c in all_ctors:
                    if on.endswith("-" + c):
                        if c in missing:
                            orbit_covers.add(c)
                        break
        spec_covers = {axis for axis, _ in spec}
        print(f"      CODOMAIN OF POSSIBLE ACTIONS:")
        opt_n = 0
        # (i) ALIAS via speculative match — usually highest-rated.
        if spec:
            opt_n += 1
            print(f"        ({opt_n}) ALIAS to existing speculative-match def(s):")
            for axis, cand in spec:
                cand_short = cand.split("::")[-1]
                print(f"              {stem}-{axis} = {cand_short}    (axis '{axis}')")
            print(f"            JUSTIFIED BY: a def under naming-convention relaxation")
            print(f"                          already realises each missing position; aliasing")
            print(f"                          makes it findable under both names.")
            print(f"            PRESERVES: original naming marker (e.g., lowercase '-d'")
            print(f"                       for cocycle-anchor, uppercase '-X' for axes).")
            print(f"            COST: {len(spec)} one-line aliases. RATING: ★★★")
        # (ii) RENAME existing match — usually low-rated (rigidification).
        if spec:
            opt_n += 1
            print(f"        ({opt_n}) RENAME existing speculative-match def(s):")
            for axis, cand in spec:
                cand_short = cand.split("::")[-1]
                print(f"              {cand_short} → {stem}-{axis}")
            print(f"            JUSTIFIED BY: same observation as ALIAS, but resolved")
            print(f"                          by erasing the original name rather than")
            print(f"                          coexistence.")
            print(f"            ERASES: original naming marker. If the marker encodes a")
            print(f"                    chirality choice (cocycle anchor, use-vs-commit),")
            print(f"                    this is a RIGIDIFICATION.")
            print(f"            COST: high (rename + update all callers, typically tens).")
            print(f"            RATING: ✗ (avoid unless asymmetry is genuinely unintentional)")
        # (iii) ADD missing siblings as new defs.
        opt_n += 1
        if cps:
            print(f"        ({opt_n}) ADD missing siblings via parametric counterpart:")
            print(f"              counterpart found: {', '.join(c.split('::')[-1] for c in cps)}")
            print(f"              add {len(missing)} aliases (one per missing axis)")
            print(f"            JUSTIFIED BY: parametric counterpart exists in scope; aliasing")
            print(f"                          to it is a mechanical instantiation per axis.")
            print(f"            COST: low ({len(missing)} one-line aliases).")
            print(f"            RATING: ★★ (mechanical, but adds new identifiers that may")
            print(f"                       themselves form an orbit triggering further")
            print(f"                       proposals — verify the codomain shrinks, not grows).")
        else:
            print(f"        ({opt_n}) ADD missing siblings as ad-hoc proofs:")
            print(f"              {len(missing)} new defs with types Stab-X (...) for X in")
            print(f"              {list(missing)}")
            print(f"            JUSTIFIED BY: the type schema implies these siblings could")
            print(f"                          exist by symmetry; we have no parametric")
            print(f"                          counterpart to derive them from.")
            print(f"            RISK: may FAIL TO TYPECHECK if the propositions are not")
            print(f"                  true (e.g., D-anchored dispatcher's outputs don't")
            print(f"                  uniformly fix C/S/W).")
            print(f"            RATING: ★ (investigate provability first; structural truth")
            print(f"                       may forbid closure)")
        # (iv) PROMOTE-TO-PARAMETRIC — refactor to absorb into upstream.
        if cps or orbits_seen:
            opt_n += 1
            print(f"        ({opt_n}) PROMOTE to parametric upstream:")
            print(f"              refactor {sorted({q.split('::')[-1] for q in f.objects})}")
            print(f"              to delegate to a parametric helper indexed by the axis.")
            print(f"            JUSTIFIED BY: orbit-membership ({len(orbits_seen)} orbit(s))")
            print(f"                          or parametric counterpart in scope; the def")
            print(f"                          can be re-expressed as `helper X` for varying X.")
            print(f"            RISK: downstream proofs may rely on pattern-match exposure;")
            print(f"                  delegate-form may not reduce definitionally.")
            print(f"            RATING: ★★ (highest leverage when it works; costliest when")
            print(f"                       downstream relies on case-analysis structure).")
        # (v) ACCEPT — always available.
        opt_n += 1
        if is_promoted:
            print(f"        ({opt_n}) ACCEPT: cousin cluster ALREADY absorbs this finding.")
            print(f"            JUSTIFIED BY: upstream cluster (PROMOTED marker) covers the")
            print(f"                          parametric structure; this finding is downstream")
            print(f"                          reportage, not a TODO.")
            print(f"            RATING: ★★★ (closure already exists at higher level)")
        elif fully_covered := ((spec_covers | orbit_covers) >= set(missing)):
            print(f"        ({opt_n}) ACCEPT: missing axes are FULLY COVERED at higher levels")
            print(f"            JUSTIFIED BY: every missing axis is realised by either an")
            print(f"                          orbit-sibling ({sorted(orbit_covers)}) or a")
            print(f"                          speculative-match candidate ({sorted(spec_covers)}).")
            print(f"            RATING: ★★★ (the partial coset is a stem-extraction artifact)")
        else:
            uncov = sorted(set(missing) - spec_covers - orbit_covers)
            print(f"        ({opt_n}) ACCEPT: structural truth; uncovered={uncov}.")
            print(f"            JUSTIFIED BY: no upstream signal closes the uncovered axes;")
            print(f"                          either siblings are unprovable, or the type's")
            print(f"                          ctors aren't all expected to manifest here.")
            print(f"            RATING: ★★ (informational; no action — but consider whether")
            print(f"                       the stem extraction is dropping meaningful tokens)")
        # Recommendation derived from the joined signal:
        total_cover = spec_covers | orbit_covers
        if is_promoted:
            rec = "ACCEPT (cousin-cluster absorption — closure at higher level)"
        elif total_cover >= set(missing):
            if spec:
                rec = "ALIAS (preserves naming markers; closes coset mechanically)"
            else:
                rec = "ACCEPT (orbit-fanout already complete; stem-extraction artifact)"
        elif orbit_covers and not spec:
            # Partial orbit coverage but no spec-match for the rest.
            uncov = sorted(set(missing) - total_cover)
            rec = (f"ACCEPT for orbit-covered axes {sorted(orbit_covers)} "
                   f"(parametric family); investigate {uncov} separately "
                   f"(likely structurally distinct, e.g., cocycle anchor)")
        elif spec:
            rec = "ALIAS (closes coset; if asymmetry is intentional, ACCEPT instead)"
        elif cps:
            rec = "ADD via parametric counterpart"
        else:
            rec = "ACCEPT (no upstream signal; verify provability if you disagree)"
        print(f"      RECOMMENDED: {rec}")

    if spec_proposals:
        print("  [2] SPECULATIVE rename/alias proposals (naming-convention asymmetries):")
        # Build stem → finding-idx map to pull the trace.
        stem_to_idx = {pc_findings_list[i].extra[3]: i
                       for i in range(len(pc_findings_list))}
        seen_pairs = set()
        for stem, missing_c, existing_name in spec_proposals:
            key = (stem, existing_name)
            if key in seen_pairs:
                continue
            seen_pairs.add(key)
            proposals_count += 1
            print(f"    PROPOSAL #{proposals_count}: stem '{stem}' missing '{missing_c}', "
                  f"existing match: {existing_name}")
            idx = stem_to_idx.get(stem)
            if idx is not None:
                _emit_trace_for_pc(idx, "SPECULATIVE")
                _emit_codomain_for_pc(idx)
            print()

    # 3. EFFECTIVE LEAVES — additive sibling proposals.
    if promoted or strict:
        print("  [3] Effective leaves (cousin-cluster-absorbed or strict):")
        for idx in promoted:
            finding = pc_findings_list[idx]
            ty, present, missing, stem, cps = finding.extra
            proposals_count += 1
            print(f"    PROPOSAL #{proposals_count}: stem '{stem}' "
                  f"(PROMOTED via cousin absorption)")
            _emit_trace_for_pc(idx, "PROMOTED")
            _emit_codomain_for_pc(idx)
            print()
        for idx in strict:
            finding = pc_findings_list[idx]
            ty, present, missing, stem, cps = finding.extra
            # Skip leaves already addressed via speculation.
            already_proposed = any(stem == s for s, _, _ in spec_proposals)
            if already_proposed:
                continue
            proposals_count += 1
            print(f"    PROPOSAL #{proposals_count}: stem '{stem}' (strict leaf)")
            _emit_trace_for_pc(idx, "STRICT")
            _emit_codomain_for_pc(idx)
            print()

    # 4. DEPENDENT findings — partial-coset findings that depend on
    #    other partial-coset findings (NOT leaves). Surfaced explicitly
    #    so the user can see the FULL fanout picture, not just the
    #    leaf-filtered slice. Each gets the same trace + codomain
    #    treatment as leaves; the "depends-on" stem chain is shown
    #    in [f] cluster status.
    spec_stems = {s for s, _, _ in spec_proposals}
    promoted_set = set(promoted)
    strict_set = set(strict)
    dependent_idxs = [
        i for i in range(len(pc_findings_list))
        if i not in promoted_set and i not in strict_set
        and i not in absorbed_members
        and pc_findings_list[i].extra[3] not in spec_stems
    ]
    if dependent_idxs:
        print(f"  [4] Dependent findings (depend on other unresolved findings — shown")
        print(f"       for full-fanout visibility per the multi-signal discipline):")
        for idx in dependent_idxs:
            finding = pc_findings_list[idx]
            ty, present, missing, stem, cps = finding.extra
            proposals_count += 1
            dep_stems = sorted({
                pc_findings_list[d].extra[3]
                for d in finding_deps[idx]
            })
            print(f"    PROPOSAL #{proposals_count}: stem '{stem}' "
                  f"(depends on: {dep_stems})")
            _emit_trace_for_pc(idx, "DEPENDENT")
            _emit_codomain_for_pc(idx)
            print()

    if proposals_count == 0:
        print("  (No actionable proposals — the codebase's partial cosets are at a")
        print("   structural floor that requires manual interpretation.)")
        print()
    else:
        print(f"  Total proposals: {proposals_count}. Apply one, re-run, iterate.")
        print()

    # === Meta-motifs: group findings by recurring structural pattern.
    # Surfaces project-wide motifs like 3-vs-4 / Hodge-dual that the
    # per-finding traces hint at individually — here they're aggregated
    # so the reader can see the motif as a coherent feature.
    motif_groups = defaultdict(list)
    for i in range(len(pc_findings_list)):
        f = pc_findings_list[i]
        ty, present, missing, stem, cps = f.extra
        motif_name, _ = _classify_motif(present, missing)
        if motif_name and motif_name != "COMPLETE":
            motif_groups[motif_name].append((i, ty, present, missing, stem))
    if motif_groups:
        print("=== Meta-motifs (project-wide structural patterns) ===")
        print("  Findings grouped by the structural shape of their (present, missing)")
        print("  partition. Same motif appearing across multiple type-domains is a")
        print("  signal that the motif is a project-level feature, not a local quirk.")
        print()
        for motif, items in sorted(motif_groups.items(), key=lambda x: -len(x[1])):
            print(f"  [{motif}] — {len(items)} finding(s):")
            for i, ty, present, missing, stem in items:
                miss_str = ", ".join(missing) if missing else "—"
                print(f"    · {ty}: stem='{stem}', "
                      f"present={sorted(present)}, missing=[{miss_str}]")
            # For 3-of-4 / ANCHOR-FANOUT findings, surface the
            # missing-element frequency so the cross-type "shared anchor"
            # signal is visible. Whether the anchor is a TRUE Hodge dual
            # vs. a structurally-privileged element with no ordering on
            # the 3 is a separate question; this just reports the shape.
            if "ANCHOR-FANOUT" in motif:
                miss_counter = Counter()
                for i, ty, present, missing, stem in items:
                    for m_elt in missing:
                        miss_counter[m_elt] += 1
                if miss_counter:
                    print(f"    Distinguished-element frequency across this motif:")
                    for elt, n in miss_counter.most_common():
                        print(f"      '{elt}' is the distinguished one in {n} finding(s)")
                    print(f"    → elements that recur in the distinguished position")
                    print(f"      across multiple findings are the project's chirality")
                    print(f"      anchors. To know whether they're also Hodge duals,")
                    print(f"      check whether the 3 carry ordering at a downstream level")
                    print(f"      (e.g., are they cycled by an s3-cycle? sequenced?).")
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
