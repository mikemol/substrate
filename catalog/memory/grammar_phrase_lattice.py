#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""grammar_phrase_lattice.py — HIERARCHICAL (mind-map) core-idea index.

The same eliza Sequitur-grammar phrase-clustering, applied RECURSIVELY: the whole
corpus → top concepts; each concept's member memories are RE-RUN through the same
process → sub-concepts; recurse to a depth/size floor. Self-similar clustering at
every level = a concept tree.

Per level: intern full bodies → Sequitur grammar (the hierarchical phrase index) →
phrase→member clusters → 3 collapses (prefix-merge · nesting · kernel-merge w/
member-overlap guard). Members a node's sub-concepts DON'T capture remain as the
node's direct leaves (never-discard-residue applied to the index itself).
"""

import os, re, glob, sys, shutil
from collections import defaultdict

HERE = os.path.dirname(os.path.realpath(__file__))
ELIZA = os.path.realpath(os.path.join(HERE, "../../../../github/substrate/scratch/eliza"))
sys.path.insert(0, ELIZA)
from eliza.sequitur import Sequitur, NT

SKIP = {
    "MEMORY.md",
    "ARCHIVE.md",
    "MEMORY.candidate.md",
    "MEMORY.grammar_index.md",
    "MEMORY.synth_wired.md",
}
STOP = set(
    "the a an of to in is it as be by or and not for on with that this these those we i so its are was can has had via per no also when then than only into out up down over under most more less each both new one are you your they them their why how apply drove still now yet only via".split()
)
PREFIX = {"feedback", "project", "reference", "discipline"}


def full(p):
    s = open(p).read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", s, re.S)
    if not m:
        return s
    fm, body = m.group(1), m.group(2)
    d = re.search(r"^description:\s*(.+)$", fm, re.M)
    desc = d.group(1).strip().strip('"') if d else ""
    return re.sub(r"\S*/\S*", " ", desc + "\n" + body)  # strip path/URL runs


def words(t):
    return [w for w in re.findall(r"[a-z][a-z-]{2,}", t.lower()) if w not in STOP]


def expand(seq, rules, max_out=24):
    out = []
    stack = [(s, ()) for s in reversed(seq)]
    while stack and len(out) < max_out:
        s, seen = stack.pop()
        if isinstance(s, NT):
            if s.rule_id in seen:
                out.append(f"R{s.rule_id}")
            else:
                for sub in reversed(rules.get(s.rule_id, [])):
                    stack.append((sub, seen + (s.rule_id,)))
        else:
            out.append(s)
    return out


def _subseq(a, b):
    return len(a) < len(b) and any(b[i : i + len(a)] == a for i in range(len(b) - len(a) + 1))


def cluster_phrases(items, phrase_min=3, min_members=2, tau=0.5):
    """items: [(name, tokens)]. → [(phrase_str, frozenset(members))] after the
    grammar build + 3 collapses, sorted by membership desc."""
    names = [n for n, _ in items]
    mem_toks = [t for _, t in items]
    gram = Sequitur()
    for toks in mem_toks:
        for w in toks:
            gram.observe(w)
        gram.observe("∎")
    rules = gram.all_rules()
    raw = []
    memtext = [" " + " ".join(t) + " " for t in mem_toks]
    for rid in rules:
        if rid == 0:
            continue
        p = tuple(w for w in expand(rules[rid], rules) if w != "∎")
        if len(p) < phrase_min:
            continue
        needle = " " + " ".join(p) + " "
        mems = frozenset(names[i] for i in range(len(memtext)) if needle in memtext[i])
        if len(mems) >= min_members:
            raw.append((p, mems))

    # collapse 1: strip link-prefix, merge identical, union members
    def strip_prefix(p):
        i = 0
        while i < len(p) and p[i] in PREFIX:
            i += 1
        return p[i:] if len(p) - i >= 2 else p

    merged = {}
    for p, mems in raw:
        merged.setdefault(strip_prefix(p), set()).update(mems)
    # collapse 2: drop a phrase that is a contiguous sub-phrase of a longer one
    # with the SAME member set (keep maximal granularity)
    by_members = defaultdict(list)
    for c, ms in merged.items():
        by_members[frozenset(ms)].append(c)
    units = []
    for ms, phrases in by_members.items():
        maximal = []
        for c in sorted(phrases, key=len, reverse=True):
            if not any(_subseq(c, k) for k in maximal):
                maximal.append(c)
        for c in maximal:
            units.append((c, ms))
    # collapse 3: kernel-merge (≥2 shared tokens AND member Jaccard ≥ tau)
    tok = [set(c) for c, _ in units]
    par = list(range(len(units)))

    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            a, b = units[i][1], units[j][1]
            jac = len(a & b) / len(a | b)
            # near-identical members → one cluster (even if vocab differs: the
            # arc-template case); else a lexical kernel (≥2 shared tokens) + tau.
            if jac >= 0.8 or (len(tok[i] & tok[j]) >= 2 and jac >= tau):
                par[find(i)] = find(j)
    comp = defaultdict(list)
    for i in range(len(units)):
        comp[find(i)].append(i)
    out = []
    for idxs in comp.values():
        members = frozenset().union(*(units[i][1] for i in idxs))
        rep = max(idxs, key=lambda i: (len(units[i][1]), len(units[i][0])))
        out.append((" ".join(units[rep][0]), members))
    out.sort(key=lambda x: (-len(x[1]), x[0]))
    return out


def build_tree_from(top_clusters, items, max_depth, min_recurse, top_k):
    """Build the nested tree from PRECOMPUTED top-level clusters (so the
    expensive top-level grammar build runs once); recurse on sub-corpora."""
    toks_of = dict(items)
    whole = len(toks_of)
    nodes = []
    for phrase, members in top_clusters[:top_k]:
        if len(members) == whole and max_depth < 2:
            continue
        sub = []
        if max_depth > 0 and len(members) >= min_recurse:
            sub_items = [(n, toks_of[n]) for n in members if n in toks_of]
            sc = cluster_phrases(sub_items, phrase_min=3)
            sub = [
                s
                for s in build_tree_from(sc, sub_items, max_depth - 1, min_recurse, 6)
                if len(s[1]) < len(members)
            ]
        nodes.append((phrase, members, sub))
    return nodes


def pct(vals, p):
    if not vals:
        return 0
    s = sorted(vals)
    return s[min(len(s) - 1, int(p / 100 * len(s)))]


def pp_rank(value, all_vals):
    """Percentile of `value` in the distribution (100 = largest) — the relevance coord."""
    n = len(all_vals)
    return 100 * sum(1 for v in all_vals if v <= value) // n if n else 0


def stratify(items, tier, max_tiers, lines):
    """RECURSIVE STRATIFICATION (never-discard-residue across the residue axis):
    cluster this stratum, display its dominant concepts (those whose membership is
    ≥ the Pth PERCENTILE of this stratum's size distribution — data-relative, not a
    fixed top_k), then re-run on the memories left uncovered. Recurse until only
    true singletons remain. Each tier's discarded set is the next tier's corpus."""
    names = [n for n, _ in items]
    clusters = cluster_phrases(items, phrase_min=3)
    if not clusters:  # nothing recurs ≥2 → all singletons
        lines.append(
            f"\n## tier {tier} · singletons — share no recurring phrase, kept as residue [{len(names)}]"
        )
        lines.append("  " + ", ".join(f"[[{n}]]" for n in sorted(names)))
        return
    sizes = [len(m) for _, m in clusters]
    cut = pct(sizes, 90)  # PERCENTILE partition (data-relative): show
    head = [c for c in clusters if len(c[1]) >= cut]  # concepts with membership ≥ the P90 size
    hsz = sorted(len(m) for _, m in head)
    med = hsz[len(hsz) // 2]  # recurse a concept iff ≥ median head size (percentile)
    tree = build_tree_from(head, items, max_depth=2, min_recurse=med, top_k=len(head))
    tlines = render(tree, 0, [])
    lines.append(
        f"\n## tier {tier} — {len(head)} concepts with membership ≥ P90 (≥{cut}) over {len(names)} memories"
    )
    lines += tlines
    covered = set(re.findall(r"\[\[([a-z0-9_]+)\]\]", "\n".join(tlines)))
    residual = [(n, t) for n, t in items if n not in covered]
    if residual:
        if tier < max_tiers:
            stratify(residual, tier + 1, max_tiers, lines)
        else:
            lines.append(f"\n## tier {tier}+ · residue (tier cap reached) [{len(residual)}]")
            lines.append("  " + ", ".join(f"[[{n}]]" for n, _ in residual))


def compute_tiers(items, max_tiers):
    """Recursive stratification, but RETURN the tier trees (for file emission)
    instead of rendering lines. Each tier's discarded set → next tier's corpus."""
    tiers, singletons, cur, tier = [], [], items, 1
    while cur and tier <= max_tiers:
        clusters = cluster_phrases(cur, phrase_min=3)
        if not clusters:
            singletons = [n for n, _ in cur]
            break
        sizes = [len(m) for _, m in clusters]
        cut = pct(sizes, 90)
        head = [c for c in clusters if len(c[1]) >= cut]
        hsz = sorted(len(m) for _, m in head)
        med = hsz[len(hsz) // 2]
        tree = build_tree_from(head, cur, max_depth=2, min_recurse=med, top_k=len(head))
        tiers.append((tier, tree, sizes))
        covered = set().union(*[set(m) for _, m, _ in tree]) if tree else set()
        cur = [(n, t) for n, t in cur if n not in covered]
        tier += 1
    if cur and not singletons:
        singletons = [n for n, _ in cur]
    return tiers, singletons


def slugify(s, used):
    base = (re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:50]) or "concept"
    out, i = base, 1
    while out in used:
        i += 1
        out = f"{base}-{i}"
    used.add(out)
    return out


def memlink(m):  # from index/<file>.md → memory/<m>.md
    return f"[{m}](../{m}.md)"


def write_concept_file(node, index_dir, used):
    """One concept-cluster INDEX file: its sub-concepts (with member links) and
    its direct members. Returns (phrase, slug, n) for the parent to link to."""
    phrase, members, sub = node
    slug = slugify(phrase, used)
    L = [
        f"# {phrase}",
        f"_concept index · {len(members)} memories · a node of the MEMORY mind-map. "
        f"Links: finer concepts (same dir) or memories (`../name.md`)._\n",
    ]
    captured = set()
    for sphrase, smembers, _ in sorted(sub, key=lambda x: -len(x[1])):
        captured |= set(smembers)
        L.append(
            f"- **{sphrase}** [{len(smembers)}] — "
            + ", ".join(memlink(m) for m in sorted(smembers))
        )
    residual = sorted(set(members) - captured)
    if residual:
        L.append(
            f"- _direct members_ [{len(residual)}] — " + ", ".join(memlink(m) for m in residual)
        )
    open(os.path.join(index_dir, slug + ".md"), "w").write("\n".join(L) + "\n")
    return phrase, slug, len(members)


def render(nodes, depth, lines):
    ind = "  " * depth
    for phrase, members, sub in nodes:
        lines.append(f"{ind}- **{phrase}** [{len(members)}]")
        captured = set().union(*[s[1] for s in sub]) if sub else set()
        residual = sorted(members - captured)
        for s in sub:
            render([s], depth + 1, lines)
        if residual:
            lines.append(f"{ind}  ⇐ " + ", ".join(f"[[{m}]]" for m in residual))
    return lines


PREAMBLE = """# MEMORY — core-idea index (mesh root)

**What this is.** The ROOT of a navigable concept MESH over the persistent memory corpus
(`memory/*.md`). It links to CONCEPT-CLUSTER files (in `index/`), NOT directly to memories.
Each concept is a recurring phrase discovered by interning every memory's full body through
eliza's Sequitur grammar (`scratch/eliza`). Open a concept file to see its finer sub-concepts
and its member memories; open a memory for the fact. Regenerate: `grammar_phrase_lattice.py`.
Formal claims + causality: `warrants.bib`. Unfinished work: [[project_open_threads]].
Cold / finished arcs (not in the mesh): [ARCHIVE.md](ARCHIVE.md).

**How to navigate.** `[concept](index/slug.md) [N] ·pPP` — N memories carry it, PP = its
membership percentile (relevance; admitted highest-pp-first). Open the file to descend: it
lists sub-concepts (with `../memory.md` links) and direct members. A memory appears under
several concepts — that is the MESH (a multiply-connected memory cross-referenced from each
discipline it instantiates), not redundancy. This root POINTS; the facts are in the memory
files. Less-dominant concepts + singletons: [index/_deeper.md](index/_deeper.md).

**To add a memory:** write the file in `memory/`, then jot it in the STAGING block at the
very bottom of this file and re-run the script — the regen folds it into the mesh and clears
the staged note once its file exists. Staging is preserved across regens; the mesh above is not.
"""

STAGING_MARKER = (
    "<!-- ═══════ STAGING — add new memory entries below this line, then run: "
    "python3 memory/grammar_phrase_lattice.py ═══════ -->"
)


def main():
    files = sorted(
        f
        for f in glob.glob(HERE + "/**/*.md", recursive=True)
        if os.path.basename(f) not in SKIP
        and (os.sep + "index" + os.sep) not in f
        and (os.sep + "synth" + os.sep) not in f
    )  # synth/ = derived, not source
    items = [(os.path.basename(f)[:-3], words(full(f))) for f in files]
    items = [(n, t) for n, t in items if t]
    allnames = frozenset(n for n, _ in items)
    print(f"corpus: {len(items)} memories; emitting index-of-indexes file tree …")

    INDEX_DIR = os.path.join(HERE, "index")
    shutil.rmtree(INDEX_DIR, ignore_errors=True)
    os.makedirs(INDEX_DIR)
    tiers, singletons = compute_tiers(items, max_tiers=6)
    used_slugs = set()

    # tier 1 = the dominant concepts the ROOT links to (with pp-relevance).
    _, t1_tree, t1_sizes = tiers[0]
    root = [PREAMBLE, "## concepts", ""]  # blank after heading (MD022/MD032)
    for node in t1_tree:
        phrase, slug, n = write_concept_file(node, INDEX_DIR, used_slugs)
        root.append(f"- [{phrase}](index/{slug}.md) [{n}] ·p{pp_rank(n, t1_sizes)}")
    root += [
        "",
        "## deeper / less-dominant concepts + singletons → [index/_deeper.md](index/_deeper.md)",
    ]
    n_concept_files = len(t1_tree)

    # _deeper.md = the index OF the lower tiers' concept files + the singletons.
    deep = [
        "# deeper concepts (below the dominant tier)",
        "",
        "> less-dominant concept clusters (re-clustered from what the prior tier didn't "
        "surface) + the unclustered singletons. `slug.md` = a concept, `../name.md` = a memory.",
    ]
    for tnum, tree, _ in tiers[1:]:
        deep += ["", f"## tier {tnum}", ""]
        for node in tree:
            phrase, slug, n = write_concept_file(node, INDEX_DIR, used_slugs)
            deep.append(f"- [{phrase}]({slug}.md) [{n}]")
            n_concept_files += 1
    if singletons:
        deep += [
            "",
            f"## singletons — share no recurring phrase, kept as residue [{len(singletons)}]",
            "",
            ", ".join(memlink(m) for m in sorted(singletons)),
        ]
    open(os.path.join(INDEX_DIR, "_deeper.md"), "w").write("\n".join(deep) + "\n")

    root_path = os.path.join(HERE, "MEMORY.md")  # the LIVE loaded index (installed)

    # STAGING — preserve the human-editable inbox below the marker across regens,
    # SELF-CLEARING any staged line whose referenced memory file now exists (it has
    # been folded into the mesh above). The generated mesh is rewritten; staging is not.
    prev = open(root_path).read() if os.path.exists(root_path) else ""
    prior_staging = prev.split(STAGING_MARKER, 1)[1] if STAGING_MARKER in prev else ""
    kept = []
    for ln in prior_staging.splitlines():
        if (
            ln.strip().lstrip("_>( ").startswith("empty")
        ):  # drop the auto-placeholder (old/new form)
            continue
        refs = re.findall(r"\[\[?([a-z0-9_]+)\]?\]|\(\.\./([a-z0-9_]+)\.md\)", ln)
        slugs = [a or b for a, b in refs]
        if slugs and all(os.path.exists(os.path.join(HERE, s + ".md")) for s in slugs):
            continue  # integrated → drop from inbox
        kept.append(ln)
    staging_body = "\n".join(kept).strip()
    if not staging_body:
        staging_body = (
            "> empty — write `memory/<slug>.md` (frontmatter + body), add a line "
            "`- [[<slug>]] — one-line` here, then re-run the script."
        )

    root_txt = "\n".join(root) + "\n\n" + STAGING_MARKER + "\n\n" + staging_body + "\n"
    # Agda mixfix (_·_ _↔_ …) reads as MD049 underscore-emphasis — it IS code; wrap it (never plain prose).
    root_txt = re.sub(r"(?<!`)(_[^\s_`]*[^\sA-Za-z0-9_`][^\s_`]*_)(?!`)", r"`\1`", root_txt)
    open(root_path, "w").write(root_txt)

    # coverage: every memory reachable from SOME index file (via ../name.md links).
    refs = set()
    for f in glob.glob(INDEX_DIR + "/*.md"):
        refs |= set(re.findall(r"\]\(\.\./([a-z0-9_]+)\.md\)", open(f).read()))
    covered = refs & allnames
    print(f"=== ROOT MEMORY.md: {len(root_txt) / 1024:.1f} KB · {len(t1_tree)} top concept links")
    print(
        f"=== index/: {n_concept_files} concept files + _deeper.md · {len(singletons)} singletons"
    )
    print(f"=== COVERAGE: {len(covered)}/{len(allnames)} memories reachable through the file tree")


if __name__ == "__main__":
    main()
