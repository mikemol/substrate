"""Parse catalog/idea_lattice.md into levels + tagged concepts.

Shared by the 2D idea_lattice figure and its 3D tower sibling.
"""

import re

import pathlib
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]  # figures→scratch→repo

SRC = REPO_ROOT / "catalog" / "idea_lattice.md"
_LEVEL_RE = re.compile(r"^## Level (\d+)\s+—\s+(.*)$")
_CONCEPT_RE = re.compile(r"^- \*\*([^*]+)\*\*\s*\[([^\]]+)\]")


def classify(tag):
    t = tag.lower()
    if "gauge" in t:
        return "gauge"
    if "invariant" in t:
        return "invariant"
    return "other"


def short_name(name):
    return name.split(":")[0].replace("C-", "").replace("K-", "")


def parse_levels():
    """Return [(level_num, title, [(concept_name, class), …]), …]."""
    levels = []
    cur = None
    for raw in SRC.read_text(encoding="utf-8").splitlines():
        lm = _LEVEL_RE.match(raw)
        if lm:
            cur = (int(lm.group(1)), lm.group(2).strip(), [])
            levels.append(cur)
            continue
        cm = _CONCEPT_RE.match(raw)
        if cm and cur is not None:
            cur[2].append((cm.group(1).strip(), classify(cm.group(2))))
    return levels
