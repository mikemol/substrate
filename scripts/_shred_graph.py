#!/usr/bin/env python3
# _shred_graph.py — the single-source Agda data/record dependency graph the shred tools were each rebuilding.
# Surfaced by the reuse wedge (scratch/scripts_dedup.py) as the rung-1 consolidation: after the rung-0 pure
# leaves (strip/split_arrows/_b64) were lifted, the residual IDENTICAL families were `reach` (3 files), `rank`
# (3), `refs` (2), `toks` (5) — all COUPLED to a module-level graph state (kind/known/produced/consumed/
# importers/body) that bridge_graph_shred / rank4_shred / realizability_surface / type_dead_ends /
# type_reaction each rebuilt. This class holds that build once; the tools instantiate it and keep only their
# own analysis residue (type_dead_ends/type_reaction use just .known/.toks + their own produced/consumed).
#
# The build is the VERBATIM bridge_graph_shred/rank4_shred build (the richest, a superset): `known` is the
# same data|record-decl set every tool scanned, so .toks is behaviour-identical for all five; `importers`/
# `produced`/`consumed` are built the same way the three reach/rank users built them, so .reach/.rank/.refs
# reproduce their results exactly (verified by byte-identical tool output).
#
# Invoked as `scripts/<tool>.py`, so a bare `from _shred_graph import ShredGraph` resolves (scripts/ = path[0]).
import os, re, collections
from _agdatext import strip, split_arrows


class ShredGraph:
    def __init__(self, root):
        self.text = {}; self.kind = {}; self.home = {}; self.modof = {}; self.fileof = {}
        self.body = collections.defaultdict(list)
        modre = re.compile(r"^module\s+(\S+)\s+where", re.M)
        declre = re.compile(r"^(data|record)\s+(\S+)(.*)$")
        for dp, _, fns in os.walk(root):
            for fn in fns:
                if not fn.endswith(".agda"):
                    continue
                p = os.path.join(dp, fn); t = strip(open(p, encoding="utf-8").read()); self.text[p] = t
                mm = modre.search(t)
                if mm:
                    self.modof[p] = mm.group(1); self.fileof[mm.group(1)] = p
                lines = t.splitlines(); i = 0
                while i < len(lines):
                    m = declre.match(lines[i])
                    if m:
                        name, rest = m.group(2), m.group(3); self.body[name].append(rest); j = i + 1
                        self.kind.setdefault(name, m.group(1)); self.home.setdefault(name, p)
                        while j < len(lines) and (lines[j].strip() == "" or lines[j][:1] in " \t"):
                            if " : " in lines[j]:
                                self.body[name].append(lines[j].split(" : ", 1)[1])
                            j += 1
                        i = j; continue
                    i += 1
        self.known = set(self.kind)
        self.produced = set(); self.consumed = set()
        sig = re.compile(r"^\s*[^\s:]+\s*:\s*(.+)$")
        for t in self.text.values():
            for line in t.splitlines():
                m = sig.match(line)
                if not m:
                    continue
                if "→" in m.group(1):
                    parts = split_arrows(m.group(1))
                    for a in parts[:-1]:
                        self.consumed |= set(self.toks(a))
                    self.produced |= set(self.toks(parts[-1]))
                else:
                    self.produced |= set(self.toks(m.group(1)))
        self.imports = collections.defaultdict(set)
        impre = re.compile(r"^\s*(?:open\s+import|import)\s+([A-Za-z0-9_.'-]+)", re.M)
        for p, t in self.text.items():
            if p not in self.modof:
                continue
            for m in impre.finditer(t):
                if m.group(1) in self.fileof:
                    self.imports[self.modof[p]].add(m.group(1))
        self.importers = collections.defaultdict(set)
        for m, ds in self.imports.items():
            for d in ds:
                self.importers[d].add(m)

    def toks(self, s):
        return [t for t in re.split(r"[\s()\[\]{};,.]+", s) if t in self.known]

    def reach(self, mod):
        seen = {mod}; q = collections.deque([mod])
        while q:
            u = q.popleft()
            for v in self.importers[u]:
                if v not in seen:
                    seen.add(v); q.append(v)
        return len(seen) - 1

    def rank(self, T):
        mod = self.modof.get(self.home[T], "")
        if T in self.consumed:
            return 4 if self.reach(mod) >= 40 else 3
        if T in self.produced:
            return 2
        return 1

    def refs(self, T):
        r = set()
        for b in self.body[T]:
            r |= set(self.toks(b))
        r.discard(T)
        return r
