#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Split a PARAMETERIZED Agda module (`module Over <telescope> where` + indented
body) HORIZONTALLY into one-definition-per-file leaves.

WHY THIS EXISTS.  `split_lemmas.py` treats a `module … where` block as a single
indivisible unit ("the telescope binds the whole block"), so it cannot split the
fat `module Over (CR)(d)(f-lo)` modules of the Graded chain — the very ones a
consumer must APPLY in full just to reach one lemma.  A module application
COPIES, so `open Q.Over CR d f-lo` charges the consumer for Quotient's entire
body (the *Q machinery + three ring records) to get `-P`.

THE MOVE.  Keep the telescope, split the FILE: each leaf is its own file holding
exactly ONE definition wrapped in the SAME `module Over <telescope> where`.  The
consumer then applies only the leaves it uses, and "where does `-P` live?" is
answered by the filename rather than by a search.  Pair with
`narrow_leaf_imports.py` (PREFIX=<parent>) to drop the leaves a consumer does
not reference.

CONSERVATION GUARD.  Refuses to write unless every non-blank body line lands in
exactly one leaf (the same guard `split_lemmas` uses; it caught seven silent
deletions there).

USAGE:
  split_param_module.py agda/Substrate/…/Quotient.agda           # dry run
  split_param_module.py agda/Substrate/…/Quotient.agda --apply
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_lemmas import sanitize  # single-source the name transliteration

from agda_imports import _span_end   # THE statement-span authority (agda_lex-backed); never re-derive

IMP = re.compile(r"^(open\s+import|import)\s")
MODL = re.compile(r"^module\s+(\S+)")
OVER = re.compile(r"^module\s+(\S+)")            # the inner `module Over …`
DECL = re.compile(r"^  ([^\s:;{}()@|]+)\s*(?::|=)")


def parse(path):
    lines = open(path, encoding="utf-8").read().split("\n")
    opt = next(l for l in lines if l.startswith("{-# OPTIONS"))
    mi = next(i for i, l in enumerate(lines) if MODL.match(l))
    parent = MODL.match(lines[mi]).group(1)

    # preamble imports (statement-aware: a `using (…)` continuation is indented)
    pre, i = [], mi + 1
    while i < len(lines):
        if IMP.match(lines[i]):
            e = _span_end(lines, i)
            pre.extend(lines[i:e]); i = e
        else:
            i += 1

    # the inner parameterized module header (may span lines until `where`)
    oi = next(i for i in range(mi + 1, len(lines)) if OVER.match(lines[i]) and i != mi)
    hdr = [lines[oi]]
    j = oi
    while "where" not in lines[j]:
        j += 1; hdr.append(lines[j])
    body = lines[j + 1:]

    # ⚑ A COL-0 line after the telescope ENDS the module's body: it is TRAILING
    # TOP-LEVEL content (a concrete instantiation `module GF16 = Over 3 m-lo₄`,
    # its `open`s, and the reflections built on it).  Left in the unit stream it
    # is silently SWALLOWED by the last definition and re-emitted inside that
    # leaf, where `Over` names only that leaf ⇒ the instance breaks (measured on
    # DLogHom: 16 trailing lines absorbed into `dlog-inv-law`).  Cut it off and
    # hand it back so the PARENT keeps it (the splitter is additive).
    trailing = []
    for k, l in enumerate(body):
        if l.strip() and not l.startswith(" ") and not l.lstrip().startswith("--"):
            trailing = body[k:]
            body = body[:k]
            break

    # body prelude: the `open …` / `private variable` lines every leaf needs
    prelude, k = [], 0
    while k < len(body):
        s = body[k].strip()
        # ⚑ `module X = <Path>.Over <args>` is a PRELUDE line: it binds a module
        # ALIAS the following opens (and the leaf bodies) reference.  Treating it
        # as the first BODY line stopped prelude collection dead, so every leaf
        # lost the `open …FromCommRing.Over` / `open …Defs.Over FCRq.…` lines that
        # come after it ⇒ [NotInScope] Poly (measured on Quotient's bundle leaves,
        # after ⟡cap64-fcr-split introduced the `module FCRq =` qualifier).
        # ⚑ A bare `private` opens a BLOCK: consume it and everything indented
        # deeper.  A module alias is normally wrapped in one (`private module
        # FCRq = …` — the [ShadowedModule] fix), so stopping at `private` lost
        # the whole prelude and every leaf failed [NotInScope] Poly.
        if s == "private":
            ind0 = len(body[k]) - len(body[k].lstrip())
            prelude.append(body[k]); k += 1
            while k < len(body) and (not body[k].strip()
                                     or len(body[k]) - len(body[k].lstrip()) > ind0):
                prelude.append(body[k]); k += 1
            continue
        if (s.startswith("open ") or s.startswith("private variable")
                or re.match(r"^module\s+\S+\s*=", s)
                or s.startswith("--") or not s):
            prelude.append(body[k]); k += 1
        else:
            break
    # trim trailing blanks/comments off the prelude so they head the first unit
    while prelude and not prelude[-1].strip():
        prelude.pop()

    # ⟡public-policy: a LEAF re-exports only what it DEFINES. The parent's
    # `open Dep.Over … public` lines must lose their `public` on the way into a
    # leaf: otherwise every leaf re-exports the whole dependency, and a leaf
    # that opens BOTH its own `Dep.Over` and a sibling's `Over` sees each of the
    # dependency's names by TWO paths -> [AmbiguousName] (measured on Mod:
    # `ytime` via Core.Over and via Xpow.Over). Non-public keeps one path.
    prelude = [re.sub(r"\s+public\s*$", "", l) if l.strip().startswith("open ") else l
               for l in prelude]

    # PRIVATE HELPER BLOCKS are module-local and UNEXPORTABLE: a sibling leaf
    # cannot import them, so they must be COPIED into every leaf that cites one
    # (the `private variable` hoist of split_lemmas, one class up). Left in the
    # unit stream they are silently swallowed by the PRECEDING definition —
    # measured on Div, where `private r0/rS` landed in KEY-nth's leaf and
    # recon-nth, which USES them, failed [NotInScope].
    rest, privs, i2 = [], [], k
    while i2 < len(body):
        if body[i2].strip() == "private":
            blk, i2 = [body[i2]], i2 + 1
            while i2 < len(body) and (not body[i2].strip()
                                      or len(body[i2]) - len(body[i2].lstrip()) > 2):
                blk.append(body[i2]); i2 += 1
            while blk and not blk[-1].strip():
                i2 -= 1; blk.pop()
            privs.append(([m2.group(1) for l2 in blk
                           if (m2 := re.match(r"^\s{4,}([^\s:;{}()@|]+)\s*:(?!:)", l2))], blk))
        else:
            rest.append(body[i2]); i2 += 1

    # units: leading comment block + declaration + its clauses
    units, cur, curname, pend = [], [], None, []
    for ln in rest:
        m = DECL.match(ln)
        if m and cur and ln.strip() and not ln.startswith("    "):
            if m.group(1) != curname:
                units.append((curname, cur)); cur, curname = list(pend), None; pend = []
        if m and curname is None:
            curname = m.group(1)
        if curname is None:
            pend.append(ln)          # comment/blank before the next unit
        else:
            cur.append(ln)
    if cur:
        units.append((curname, cur))
    return opt, parent, pre, hdr, prelude, units, lines, privs, trailing


def main():
    path = sys.argv[1]
    apply = "--apply" in sys.argv
    opt, parent, pre, hdr, prelude, units, orig, privs, trailing = parse(path)

    # conservation: every non-blank body line lands in exactly one unit
    got = sum(len([l for l in u if l.strip()]) for _, u in units)
    want = len([l for l in orig[orig.index(hdr[-1]) + 1:] if l.strip()]) - len(
        [l for l in prelude if l.strip()]) - sum(
        len([l for l in b if l.strip()]) for _, b in privs) - len(
        [l for l in trailing if l.strip()])
    if got != want:
        sys.exit(f"CONSERVATION FAIL: {got} lines in units vs {want} in body — refusing to write")

    names = {}
    used = set()
    for n, _ in units:
        names[n] = sanitize(n, used)

    outdir = path[:-5]                      # Quotient.agda -> Quotient/
    print(f"{parent}: {len(units)} units -> {outdir}/")
    # The telescope's EXPLICIT ARGUMENT NAMES — what a sibling `open` must pass.
    # (Splitting on the header text yields the BINDER DECLARATIONS `{A : Set}
    # (CR : CommutativeRing A) …`, which is a parse error in argument position;
    # implicits are omitted because Agda infers them.)
    tele = " ".join(hdr).split("where")[0]
    tele = tele.split("Over", 1)[1] if "Over" in tele else tele
    args = " ".join(n for grp in re.findall(r"\(([^()]*?):", tele) for n in grp.split())
    for n, ulines in units:
        leaf = names[n]
        # Sibling leaves this unit references. An OPERATOR is written `_*Q_` at
        # its definition but `*Q` at an infix use site, so a bare token match
        # misses every infix edge (the H2 class): probe both spellings.
        # COMMENTS ARE NOT REFERENCES. A unit's trailing comment block routinely
        # names the lemma that comes NEXT ("shift lemma X = Y ∘ …"); scanning it
        # invents an edge Y→X on top of the real X→Y and the two leaves import
        # each other -> [CyclicModuleDependency] (measured on Mod:
        # ytime-shift <-> ytime-basis-shift). Strip line comments first.
        txt = " ".join(re.sub(r"(^|\s)--.*$", "", l) for l in ulines)
        toks = set(re.findall(r"[^\s(){}\[\];,]+", txt))
        sibs = [m for m, _ in units
                if m != m.strip("_") and m.strip("_") in toks or (m != n and m in toks)]
        sibs = [m for m in dict.fromkeys(sibs) if m != n]
        imports = list(pre)
        for s in sibs:
            # BARE import + fully-qualified open: `import … as X` is a banned
            # directive (check_ban_ratchet), and a generated split must not
            # manufacture new debt to pay off old debt.
            imports.append(f"import {parent}.{names[s]}")
        opens = [f"  open {parent}.{names[s]}.Over {args}".rstrip() for s in sibs]
        content = [
            "-" * 72,
            f"-- {parent}.{leaf}  —  defines `{n}`",
            "--",
            "-- ⟡definition-per-file (split upstream, never filter imports): one definition,",
            "-- named by its file. A consumer applies THIS leaf's telescope instead of the",
            "-- whole parent module — a module application COPIES, so applying the parent to",
            f"-- reach `{n}` charges the consumer for every other definition in it.",
            "-" * 72,
            "",
            opt,
            "",
            f"module {parent}.{leaf} where",
            "",
        ] + imports + [""] + hdr + prelude + opens + [
        ] + [l for ns, blk in privs if any(n in toks for n in ns) for l in blk] + ulines
        if apply:
            os.makedirs(outdir, exist_ok=True)
            with open(os.path.join(outdir, leaf + ".agda"), "w", encoding="utf-8") as f:
                f.write("\n".join(content).rstrip() + "\n")
        print(f"  {n:22s} -> {leaf}.agda   ({len(ulines)} lines, sibs: {','.join(sibs) or '—'})")
    if trailing:
        print(f"  ⚑ {len([l for l in trailing if l.strip()])} TRAILING top-level lines"
              f" kept in the PARENT (concrete instantiation) — rewire it to the leaves")
    if not apply:
        print("(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
