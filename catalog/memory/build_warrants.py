#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""build_warrants.py — project the memory/ corpus into a paperkit claim-DAG.

Each memory file is one claim (@misc): the frontmatter `description` is the claim,
`metadata.type` the rubric section, the body's [[links]] the `from` causality edges
(normalized: hyphen→underscore, basename), the topic file the `check = file:` evidence.

The bibtex stows causality (from) + links to evidence (check) — the formal backbone.
MEMORY.candidate.md is a COMPACT index projected from it (the per-line-scannable form
the harness loads; distinct from paperkit's prose projector).

    python3 build_warrants.py
"""

import os, re, glob

HERE = os.path.dirname(os.path.realpath(__file__))
SKIP = {"MEMORY.md", "ARCHIVE.md", "MEMORY.candidate.md"}


def norm(tok):  # canonical claim key: basename, hyphens→underscores
    return os.path.basename(tok).replace("-", "_")


def parse(path):
    src = open(path).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", src, re.S)
    if not m:
        return None
    fm, body = m.group(1), m.group(2)
    key = norm(os.path.basename(path)[:-3])  # key = filename stem (matches [[links]])
    d = re.search(r"^description:\s*(.+?)\s*$", fm, re.M)
    desc = d.group(1).strip().strip('"').strip() if d else ""
    t = re.search(r"^\s*type:\s*([a-z]+)", fm, re.M)
    typ = t.group(1) if t else "misc"
    links = sorted({norm(x) for x in re.findall(r"\[\[([a-z0-9_/-]+)\]\]", body)} - {key})
    rel = os.path.relpath(path, HERE)
    return {"key": key, "file": rel, "desc": desc, "type": typ, "from": links}


def main():
    files = sorted(
        f
        for f in glob.glob(os.path.join(HERE, "**", "*.md"), recursive=True)
        if os.path.basename(f) not in SKIP
    )
    claims = [c for f in files if (c := parse(f))]
    by_key = {c["key"]: c for c in claims}

    # the claim-DAG
    out = []
    for c in claims:
        claim = c["desc"].replace("{", "(").replace("}", ")")
        out.append(
            "@misc{%s,\n  section = {%s},\n  from    = {%s},\n  claim   = {%s},\n  check   = {file:%s}\n}\n"
            % (c["key"], c["type"], ", ".join(c["from"]), claim, c["file"])
        )
    open(os.path.join(HERE, "warrants.bib"), "w").write("\n".join(out))

    # resolve from-edges TOWARD the core: a link names a core imprecisely (missing
    # prefix) → match a key that endswith it. The common structure under the dangling.
    keys = set(by_key)

    def resolve(l):
        if l in keys:
            return l
        cand = [k for k in keys if k.endswith("_" + l) or k.endswith("/" + l)]
        return cand[0] if len(cand) == 1 else None

    indeg = {}
    junk = []
    for c in claims:
        c["res"] = []
        for l in c["from"]:
            r = resolve(l)
            if r:
                c["res"].append(r)
                indeg[r] = indeg.get(r, 0) + 1
            else:
                junk.append((c["key"], l))
    edges = sum(len(c["from"]) for c in claims)
    print(
        f"claims: {len(claims)}  from-edges: {edges}  resolved-to-a-core: {edges - len(junk)}  genuinely-missing: {len(junk)}"
    )
    print("genuinely-missing (junk / to-write), sample:", sorted({t for _, t in junk})[:12])

    # CORE IDEAS = the APEX common structures (top-K by in-degree). Recursion: each
    # memory's parent = its highest-in-degree citation; fold TRANSITIVELY up to the
    # apex it most grounds into (incident → core → apex). Index APEX, fold the rest.
    APEXN = 24
    ranked = sorted(claims, key=lambda c: -indeg.get(c["key"], 0))
    cores = {c["key"] for c in ranked[:APEXN] if indeg.get(c["key"], 0) >= 2}
    parent = {}
    for c in claims:
        res = sorted(c["res"], key=lambda p: -indeg.get(p, 0))
        parent[c["key"]] = res[0] if res else None

    def apex_of(k, seen=()):
        if k in cores:
            return k
        p = parent.get(k)
        return apex_of(p, seen + (k,)) if (p is not None and p not in seen) else None

    children = {k: [] for k in cores}
    orphans = []
    for c in claims:
        if c["key"] in cores:
            continue
        a = apex_of(c["key"])
        (children[a] if a in children else orphans).append(c["key"])

    def hook(c, n=150):
        s = c["desc"]
        cut = min([i for i in (s.find(". "), s.find("; ")) if i > 0] + [len(s)])
        h = s[:cut].strip()
        return (h[:n].rsplit(" ", 1)[0] + "…") if len(h) > n else h

    order = {"user": 0, "feedback": 1, "project": 2, "reference": 3, "misc": 4}
    core_claims = sorted(
        (c for c in claims if c["key"] in cores),
        key=lambda c: (order.get(c["type"], 9), -indeg[c["key"]]),
    )
    lines = [
        f"# MEMORY.md — {len(cores)} CORE IDEAS (the common structures), incidents folded as evidence.",
        f"# Projected from warrants.bib (full claims + causality); regen: build_warrants.py.\n",
    ]
    cur = None
    for c in core_claims:
        if c["type"] != cur:
            cur = c["type"]
            lines.append(f"\n## {cur}\n")
        lines.append(f"- [{c['key']}]({c['file']}) ←{indeg[c['key']]} — {hook(c)}")
        kids = children[c["key"]]
        if kids:
            lines.append(f"  ↳ {len(kids)} incidents: " + ", ".join(sorted(kids)))
    if orphans:
        lines.append(
            f"\n## ungrounded ({len(orphans)} — instance of no core yet; candidates to fold or promote)\n"
        )
        lines.append("  " + ", ".join(sorted(orphans)))
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "MEMORY.candidate.md"), "w").write(txt)
    print(
        f"\nCORE IDEAS: {len(cores)}  incidents folded: {sum(len(v) for v in children.values())}  ungrounded: {len(orphans)}"
    )
    print(
        f"MEMORY.candidate.md: {len(txt) / 1024:.1f}KB  (current 40KB; limit 24.4KB; target 17.1KB)"
    )


if __name__ == "__main__":
    main()
