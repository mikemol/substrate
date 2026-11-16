#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""synth_scale.py — refresh the synth/ apex layer, IN-PROCESS and INCREMENTAL.

  · build the corpus + gauge context ONCE (synth_apex.build_context).
  · the cluster PHRASE-LIST is CACHED (synth/.cluster_cache.json) — the ~78s Sequitur
    grammar build is rerun only when the memory FILE-SET changes (add/remove) or --all;
    content edits reuse the cache (membership is recomputed cheaply per phrase).
  · regen only STALE apexes (a memory in recorded-witnesses ∪ current-members newer than
    the apex) IN-PROCESS via build_apex — no per-cluster subprocess / corpus reload.
  · gate only what regenerated.

  python3 synth_scale.py [min_members] [--all]
(--all forces a full phrase-recompute + re-scale. A content edit that introduces a wholly
 NEW concept only surfaces on a file-set change or --all — documented trade-off of the cache.)
"""

import os, re, sys, glob, json, time

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import grammar_phrase_lattice as G
import synth_apex

FORCE = "--all" in sys.argv
MIN = next((int(a) for a in sys.argv[1:] if a.isdigit()), 4)
CACHE = os.path.join(HERE, "synth", ".cluster_cache.json")
PATHS = {os.path.basename(f)[:-3]: f for f in glob.glob(HERE + "/**/*.md", recursive=True)}

t0 = time.time()
ctx = synth_apex.build_context()  # corpus + gauge, ONCE
names, toks, N = ctx["names"], ctx["toks"], ctx["N"]
cur_files = sorted(names)


def slug(ph):
    return re.sub(r"[^a-z0-9]+", "-", ph.lower()).strip("-")


# cluster PHRASES — cached; recompute the grammar only on file-set change / --all
phrases = None
if not FORCE and os.path.exists(CACHE):
    c = json.load(open(CACHE))
    if c.get("files") == cur_files:
        phrases = c["phrases"]
if phrases is None:
    items = [(names[i], toks[i]) for i in range(N) if toks[i]]
    phrases = [ph for ph, _ in G.cluster_phrases(items, phrase_min=3)]
    os.makedirs(os.path.join(HERE, "synth"), exist_ok=True)
    json.dump({"files": cur_files, "phrases": phrases}, open(CACHE, "w"))
    print(f"cluster phrases RECOMPUTED ({len(phrases)}) — file-set changed or --all")
else:
    print(
        f"cluster phrases from cache ({len(phrases)}) — file-set unchanged, grammar build skipped"
    )


# ⚑ `outdated` AND NOT `stale`: this compares MTIMES — the apex against every member
# source and every `[[wikilink]]` witness it cites — which is one of five distinct
# comparisons the word `stale` was covering across this repo (mtime-vs-source here,
# content-hash-vs-recorded in `run_selftests`, set-difference in
# `check_feature_coverage`, rederived-vs-committed in `toolmodes`, a delete work-list
# in `sppf_db`).  Naming the comparison lets a reader tell which is meant without
# opening the site.
def outdated(ph, members):
    apex = os.path.join(HERE, "synth", slug(ph) + ".md")
    if not os.path.exists(apex):
        return True
    amt = os.path.getmtime(apex)
    rel = set(names[i] for i in members)
    rel |= set(re.findall(r"\[\[([a-z0-9_]+)\]\]", open(apex).read().split("## witnesses")[-1]))
    return any(PATHS.get(nm) and os.path.getmtime(PATHS[nm]) > amt for nm in rel)


regen_paths, skipped = [], 0
for ph in phrases:
    members = synth_apex.members_of(ph, ctx)  # current membership (cheap substring scan)
    if len(members) < MIN:
        continue
    if FORCE or outdated(ph, members):
        p = synth_apex.build_apex(ph, ctx)  # IN-PROCESS — no reload
        if p:
            regen_paths.append(p)
    else:
        skipped += 1
print(
    f"regenerated {len(regen_paths)} apexes, {skipped} skipped (fresh) in {time.time() - t0:.0f}s"
)

if regen_paths:
    import subprocess

    g = subprocess.run(
        [sys.executable, os.path.join(HERE, "synth_gate.py")] + regen_paths,
        capture_output=True,
        text=True,
    )
    fails = [l for l in g.stdout.splitlines() if l.startswith("FAIL")]
    passes = [l for l in g.stdout.splitlines() if l.startswith("PASS")]
    print(f"=== GATE (regenerated): {len(passes)} PASS, {len(fails)} FAIL ===")
    for l in fails[:20]:
        print("  " + l)
    print("REGENERATED APEXES GATE-CLEAN" if not fails else f"{len(fails)} need attention")
else:
    print("nothing stale — all apexes fresh")
