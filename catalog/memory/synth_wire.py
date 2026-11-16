#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_wire.py — Ⓜ.synth-wire: emit a mesh ROOT whose concept nodes are the
graded SYNTH APEX memories (synth/<slug>.md), not bare phrase index-files. Opening
a concept now lands on a real (synthetic) apex memory — graded by sharing-breadth,
witnessed, gate-clean — whose members are [[links]] into the corpus. The index
dissolves into the corpus as a witness-tower (apexes are themselves memories).

Candidate output: MEMORY.synth_wired.md (review before it replaces MEMORY.md).
"""

import os, re, sys, glob

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G


def slug(phrase):
    return re.sub(r"[^a-z0-9]+", "-", phrase.lower()).strip("-")


# Ⓜ.synth-boilerplate — a concept phrase is a clean noun-phrase; junk is a prose
# FRAGMENT (glue words) or a repeated-token degenerate. Cheap, no member analysis.
GLUE = set(
    (
        "but which there would already have has does want this that here just only lives happens "
        "right full genuine literally natural pattern between through above content header deferred "
        "closes blocks failure candidates next summary triggered landed substantial empirical citations "
        "parallel architectural user off past again actually way thing within reads makes gives says "
        "done gates modules session three other same look once use stop side"
    ).split()
)


def is_concept(phrase):
    t = phrase.split()
    if len(set(t)) < len(t):  # repeated token: sylow sylow / substrate X substrate
        return False
    if any(w in GLUE for w in t):  # prose-glue → sentence fragment, not a concept
        return False
    return True


# reuse the in-process context + cached cluster phrases (skip the ~78s grammar build that
# synth_scale already cached); member counts are recomputed cheaply via members_of.
import synth_apex, json

ctx = synth_apex.build_context()
CACHE = os.path.join(HERE, "synth", ".cluster_cache.json")
cur_files = sorted(ctx["names"])
if os.path.exists(CACHE) and json.load(open(CACHE)).get("files") == cur_files:
    phrases = json.load(open(CACHE))["phrases"]
else:  # fallback: recompute the grammar
    items = [(ctx["names"][i], ctx["toks"][i]) for i in range(ctx["N"]) if ctx["toks"][i]]
    phrases = [ph for ph, _ in G.cluster_phrases(items, phrase_min=3)]
ranked = sorted(((len(synth_apex.members_of(ph, ctx)), ph) for ph in phrases), reverse=True)

PREAMBLE = """# MEMORY — core-idea index (synth-apex mesh root)

**What this is.** The ROOT of the memory mesh. It links to CONCEPT APEXES (`synth/<slug>.md`),
NOT to bare phrases — each apex is a *synthetic memory* (`type: synthetic`): the cluster's
shared Sequitur-grammar structure read as a GRADED CURVE over sharing-breadth (universal-shallow
→ pairwise-deep), every line witnessed by ≥2 members and gated by `synth_gate.py`. Open an apex
to descend: its bands show the universal skeleton, the broad motifs, and the deep pairwise
co-quotes (with member-edges); its `## witnesses` are `[[links]]` into the corpus. The apexes
are *derived* — regenerate with `synth_apex.py` / `synth_scale.py`; the facts live in the member
memories. Unfinished work: [[project_open_threads]]. Cold arcs: [ARCHIVE.md](ARCHIVE.md).

**How to navigate.** `[concept](synth/slug.md) [N]` — N members carry it (breadth ≈ relevance).
A memory lives under several apexes (the mesh); that is correct. This root POINTS; descend for the fact.
"""

STAGING_MARKER = (
    "<!-- ═══════ STAGING — add new memory entries below this line, then run: "
    "python3 memory/synth_scale.py 4 && python3 memory/synth_wire.py ═══════ -->"
)

root = [PREAMBLE, "## concepts → graded synth apexes", ""]  # blank after heading (MD022/MD032)
seen, linked, dropped = set(), 0, []
for n, ph in ranked:
    s = slug(ph)
    if s in seen or not os.path.exists(os.path.join(HERE, "synth", s + ".md")):
        continue
    seen.add(s)
    if is_concept(ph):
        root.append(f"- [{ph}](synth/{s}.md) [{n}]")
        linked += 1
    else:
        dropped.append(f"{ph} [{n}]")
root += [
    "",  # caption as a blockquote (avoids MD036/MD049)
    f"> {linked} concepts wired; {len(dropped)} template/fragment clusters filtered "
    f"(Ⓜ.synth-boilerplate) — apexes still on disk, just not surfaced here.",
    "",
]
print("DROPPED (template/fragment):", "; ".join(dropped))

# STAGING — preserve the inbox below the marker across regens; self-clear entries whose
# memory file now exists (same discipline as the prior MEMORY.md generator). Writes the
# LIVE loaded index directly.
root_path = os.path.join(HERE, "MEMORY.md")
PATHS = {os.path.basename(f)[:-3] for f in glob.glob(HERE + "/**/*.md", recursive=True)}
prev = open(root_path).read() if os.path.exists(root_path) else ""
prior = prev.split(STAGING_MARKER, 1)[1] if STAGING_MARKER in prev else ""
kept = []
for ln in prior.splitlines():
    if ln.strip().lstrip("_>( ").startswith("empty"):  # old/new empty-inbox placeholder
        continue
    refs = re.findall(r"\[\[?([a-z0-9_]+)\]?\]|\(\.\./([a-z0-9_]+)\.md\)", ln)
    slugs = [a or b for a, b in refs]
    if slugs and all(sg in PATHS for sg in slugs):  # integrated → drop from inbox
        continue
    kept.append(ln)
staging = (
    "\n".join(kept).strip()
    or "> empty — write memory/<slug>.md, then run synth_scale.py 4 && synth_wire.py"
)
# blank lines around the staging marker + list (MD032); root already ends with a blank element
txt = "\n".join(root) + "\n" + STAGING_MARKER + "\n\n" + staging + "\n"
# Agda mixfix (_·_ _↔_ _⊗ˢ_ …) reads as underscore-emphasis to markdownlint (MD049) — it IS code, so
# wrap it. Conservative: only underscore-delimited tokens containing a non-alnum operator char (never
# plain _word_ prose emphasis), and never re-wrap one already in backticks.
txt = re.sub(r"(?<!`)(_[^\s_`]*[^\sA-Za-z0-9_`][^\s_`]*_)(?!`)", r"`\1`", txt)
open(root_path, "w").write(txt)
print(f"wrote {root_path}: {linked} concept→apex links, {len(txt) / 1024:.1f} KB")
