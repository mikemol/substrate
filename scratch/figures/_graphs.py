"""Graph builders for the meta-structure figures (2D and 3D share these).

- similarity_graph: runs scripts/agda_similarity.py --csv and thresholds it.
- package_import_graph: parses Substrate imports, aggregated to packages.
"""

import re
import subprocess
import sys
from collections import Counter

import networkx as nx

import pathlib
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]  # figures→scratch→repo


def similarity_graph(glob, threshold):
    """Run the similarity tool over `glob`, keep edges scoring ≥ threshold."""
    cmd = [sys.executable, "scripts/agda_similarity.py", "--glob", glob,
           "--csv", "--threshold", str(threshold)]
    out = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=True)
    G = nx.Graph()
    for line in out.stdout.splitlines():
        if not line or line.startswith("score"):
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        score = float(parts[0])
        a = parts[1].split("/")[-1].replace(".agda", "")
        b = parts[2].split("/")[-1].replace(".agda", "")
        G.add_edge(a, b, weight=score)
    return G


_IMPORT_RE = re.compile(r"^\s*(?:open\s+)?import\s+(Substrate\.[\w.]+)")


def _package(mod):
    parts = mod.split(".")
    return parts[1] if len(parts) > 1 else parts[0]


def package_import_graph():
    """Aggregate Substrate module imports to a package-level DiGraph.

    Returns (G, pkg_modules: Counter, edges: Counter, n_files).
    """
    substrate = REPO_ROOT / "agda" / "Substrate"
    files = list(substrate.rglob("*.agda"))
    pkg_modules = Counter()
    edges = Counter()

    def modname(path):
        rel = path.relative_to(REPO_ROOT / "agda").with_suffix("")
        return ".".join(rel.parts)

    for path in files:
        pkg_modules[_package(modname(path))] += 1
    for path in files:
        src = _package(modname(path))
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            m = _IMPORT_RE.match(line)
            if m:
                dst = _package(m.group(1))
                if dst != src:
                    edges[(src, dst)] += 1

    G = nx.DiGraph()
    for pkg, n in pkg_modules.items():
        G.add_node(pkg, modules=n)
    for (a, b), w in edges.items():
        G.add_edge(a, b, weight=w)
    return G, pkg_modules, edges, len(files)
