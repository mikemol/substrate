"""
Definition-level naturality-square detector. Focuses on the hot spot
revealed by the module-level analysis: the Stab-S3-* family (parametric)
vs S4Iso (D-specific) and the S4Iso-Bridges connections.

Parses top-level definitions from each .agda file:
  name : Type
  name = ...
or
  name :
  name = ...

Builds a "uses" graph where definition A uses B if A's body mentions B.
Applies the same CM + missing-corner-square analysis at the definition
level.
"""

import re
from pathlib import Path
from collections import defaultdict

import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.csgraph import reverse_cuthill_mckee


SUBSTRATE_ROOT = Path("/home/mikemol/github/substrate/agda")

# Focus on these modules
FOCUS_MODULES = {
    "Substrate.Cocycles.V4Signature.S4Iso",
    "Substrate.Cocycles.V4Signature.S4Iso-Bridges",
    "Substrate.Cocycles.V4Signature.OrbitKey-S3",
    "Substrate.Groups.Stab-S3",
    "Substrate.Groups.Stab-S3-Restrict",
    "Substrate.Groups.Stab-S3-Extend",
    "Substrate.Groups.Stab-S3-Iso",
    "Substrate.Groups.Stab-S3-Hom",
    "Substrate.Groups.SemidirectProduct",
    "Substrate.Groups.V4-Embedding",
}


def parse_module(path):
    text = path.read_text()
    m = re.search(r"^module\s+([A-Za-z0-9_.\-]+)\s+where", text, re.M)
    if not m:
        return None, []
    name = m.group(1)
    # Strip comments
    text_nc = re.sub(r"--.*$", "", text, flags=re.M)
    text_nc = re.sub(r"\{-.*?-\}", "", text_nc, flags=re.S)
    return name, text_nc


def extract_defs(text):
    """
    Find top-level definitions: identifier at column 0 followed by ':'.
    Returns dict {name: body}.
    """
    defs = {}
    lines = text.split("\n")
    current_name = None
    current_body = []
    sig_pattern = re.compile(r"^([a-zA-Z_][a-zA-Z0-9_'\-≢≈₁₂₃₄₅₆₇₈₉₀ₐₛⁿᵐ]*)\s*:")

    def flush():
        nonlocal current_name, current_body
        if current_name:
            defs.setdefault(current_name, "")
            defs[current_name] += "\n" + "\n".join(current_body)
        current_body = []

    for line in lines:
        if line.startswith(" ") or line == "":
            current_body.append(line)
            continue
        if line.startswith("module ") or line.startswith("open ") or \
           line.startswith("import ") or line.startswith("record ") or \
           line.startswith("data ") or line.startswith("private") or \
           line.startswith("postulate") or line.startswith("{-#"):
            flush()
            current_name = None
            continue
        m = sig_pattern.match(line)
        if m:
            flush()
            current_name = m.group(1)
            current_body = [line]
        else:
            current_body.append(line)
    flush()
    return defs


def main():
    # Parse focus modules.
    all_defs = {}  # qualified-name → body
    short_to_qual = {}  # short_name → set of qualified names (for ambiguity)
    for path in sorted(SUBSTRATE_ROOT.rglob("*.agda")):
        name, text = parse_module(path)
        if name not in FOCUS_MODULES:
            continue
        defs = extract_defs(text)
        for d, body in defs.items():
            qname = f"{name.split('.')[-1]}::{d}"
            all_defs[qname] = body
            short_to_qual.setdefault(d, set()).add(qname)

    print(f"Found {len(all_defs)} definitions across {len(FOCUS_MODULES)} focus modules.")

    # Build uses graph: A uses B if A's body mentions B (as identifier).
    edges = defaultdict(set)
    name_re_cache = {}
    for qname, body in all_defs.items():
        own_short = qname.split("::", 1)[1]
        for tgt_qname, _ in all_defs.items():
            if tgt_qname == qname:
                continue
            tgt_short = tgt_qname.split("::", 1)[1]
            if tgt_short == own_short:
                continue
            if tgt_short not in name_re_cache:
                # Word-boundary match for identifiers. Agda allows weird chars,
                # but we'll match on simple boundaries.
                name_re_cache[tgt_short] = re.compile(
                    r"(?<![A-Za-z0-9_\-'])" + re.escape(tgt_short) + r"(?![A-Za-z0-9_\-'])"
                )
            if name_re_cache[tgt_short].search(body):
                edges[qname].add(tgt_qname)

    nodes = sorted(all_defs.keys())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    A = lil_matrix((n, n), dtype=np.int8)
    for src, tgts in edges.items():
        for t in tgts:
            A[idx[src], idx[t]] = 1
    A = A.tocsr()
    print(f"  Adjacency: {n}x{n}, nnz = {A.nnz}")

    # Symmetrize and CM.
    A_sym = ((A + A.T) > 0).astype(np.int8)
    perm = list(reverse_cuthill_mckee(A_sym))

    # Find parallel-path pairs: (X, Y) such that X and Y are in the same
    # "row" of a naturality square — both downstream of some A, both
    # upstream of some D. We want to find cases where X and Y are
    # "siblings" with similar names (suggesting parametric vs specific).
    print("\n=== Parallel-path pairs (sibling-like) ===")
    print("  X and Y are both used by some A, both use some D, where")
    print("  X is in S4Iso (D-specific) and Y is in Stab-S3 (parametric).")
    print()
    s4iso_defs = [q for q in nodes if q.startswith("S4Iso::")]
    stab_s3_defs = [q for q in nodes if q.startswith("Stab-S3")]

    Adense = A.toarray()
    parallels = []
    for x_q in s4iso_defs:
        x = idx[x_q]
        for y_q in stab_s3_defs:
            y = idx[y_q]
            if x == y:
                continue
            # Predecessors and successors
            preds_x = set(np.where(Adense[:, x] == 1)[0])
            preds_y = set(np.where(Adense[:, y] == 1)[0])
            succs_x = set(np.where(Adense[x] == 1)[0])
            succs_y = set(np.where(Adense[y] == 1)[0])
            common_preds = preds_x & preds_y
            common_succs = succs_x & succs_y
            if common_preds or common_succs:
                # Heuristic: name similarity boosts interest
                x_short = x_q.split("::")[1]
                y_short = y_q.split("::")[1]
                # Strip common prefixes/suffixes for similarity check
                similarity = 0
                for sub in ["-id", "-sw", "-cs", "-cw", "-csw", "-cws",
                            "round-trip", "restrict", "extend",
                            "orbit-key", "stab", "fixes-D"]:
                    if sub in x_short and sub in y_short:
                        similarity += 1
                parallels.append((x_q, y_q, len(common_preds),
                                  len(common_succs), similarity))

    parallels.sort(key=lambda p: (-p[4], -(p[2]+p[3])))
    for x_q, y_q, np_pred, np_succ, sim in parallels[:25]:
        if np_pred + np_succ < 2 and sim < 1:
            continue
        print(f"  similarity={sim} preds={np_pred} succs={np_succ}")
        print(f"    {x_q:55s} ~~  {y_q}")


if __name__ == "__main__":
    main()
