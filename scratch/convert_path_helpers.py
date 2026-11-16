#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Convert inline path<->module conversions onto `agda_lex.module_path` / `module_file`.

WHY A TOOL AND NOT 45 HAND-EDITS.  Hand-patching each site is exactly what produced 69
divergent conversions in three suffix-strip spellings (`[:-5]` 22x, `[:-len(".agda")]`
23x, `with_suffix` 5x).  A mechanical conversion is uniform, reviewable as one diff, and
re-runnable when the next copy appears.

⚑ PHASE A IS MECHANICAL ONLY.  Every rewrite here must be semantics-preserving, and the
proof is a CENSUS DIFF: run each read-only gate before and after and require byte-
identical output.  Sites where the canonical is MORE correct (unicode names, parameterized
headers, comment masking) are Phase B — they change behaviour and need a build behind
them, so this tool must not touch them.  It only rewrites the two path conversions, whose
canonical form is a strict drop-in.

⚑ ROOT IS PER-FILE, NOT GLOBAL.  `scope_fix.py` runs with cwd=agda/ (its docstring says
"Run from agda/."), so its root is the EMPTY STRING; `agda_defs.py` uses a relative
`AG="agda"`; others an absolute ROOT.  Passing the wrong one yields a plausible WRONG
ANSWER, not an error — the exact failure mode this whole exercise exists to retire.  So
the root is declared per file in ROOTS below and never guessed.

DRY-RUN by default; `--apply` snapshots first.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edit_snapshot

# path -> module.  Group 1 is the path expression, group 2 the root expression (or None
# when the site strips no root, i.e. the path is already module-relative).
P2M = [
    # `p[len(AG) + 1:-5].replace("/", ".")`  -> module_path(p, AG)
    (re.compile(r"(?P<p>\w+)\[len\((?P<root>\w+)\)\s*\+\s*1:-5\]"
                r"\.replace\(\"/\",\s*\"\.\"\)"),
     lambda m: f'module_path({m.group("p")}, {m.group("root")})'),
    # `x[:-len(".agda")].replace("/", ".")`  -> module_path(x, "")
    (re.compile(r"(?P<p>[\w.\[\]()]+)\[:-len\(\"\.agda\"\)\]"
                r"\.replace\(\"/\",\s*\"\.\"\)"),
     lambda m: f'module_path({m.group("p")}, "")'),
    # `os.path.relpath(os.path.abspath(p), AGDA)[:-5].replace("/", ".")`
    #                                        -> module_path(p, AGDA)
    # ⚑ The abspath/relpath dance is exactly what `module_path` normalizes internally
    # (it abspaths both sides when their absoluteness differs), so dropping it is
    # semantics-preserving — and pinned by the "root spelling does not change the
    # answer" test.  Listed BEFORE the bare `[:-5]` rule, which would otherwise match
    # the inner expression and leave the relpath wrapper stranded around a module name.
    (re.compile(r"os\.path\.relpath\(os\.path\.abspath\((?P<p>\w+)\),\s*"
                r"(?P<root>\w+)\)\[:-5\]\.replace\(\"/\",\s*\"\.\"\)"),
     lambda m: f'module_path({m.group("p")}, {m.group("root")})'),
    # `rel[:-5].replace("/", ".")`           -> module_path(rel, "")
    (re.compile(r"(?P<p>\w+)\[:-5\]\.replace\(\"/\",\s*\"\.\"\)"),
     lambda m: f'module_path({m.group("p")}, "")'),
]

# ⚑ NOT INCLUDED, each for a measured reason (the census named them):
#   * `.agdai` variants          — wrong suffix; module_file/module_path hardcode .agda
#   * directory-only conversions — module_file always APPENDS .agda
#   * bare `[:-5]` with no .replace — a stem strip, not a module conversion; agda_lex
#     exposes no `stem` helper, so there is nothing to adopt (residue, not conversion)
#   * ROOT set to agda/Substrate — one level too deep; converting would silently DROP
#     the `Substrate.` prefix across ~12 scripts

# Per-file root for the module->path direction, and the import line each file needs.
ROOTS = {
    "scratch/scope_fix.py": '""',          # contract: run from agda/
    "scratch/agda_defs.py": "AG",
    "scratch/fix_stale_using.py": "AG",
    "scratch/split_pipeline.py": '""',
    "scripts/cap_diagnose.py": '""',
    "scripts/reuse_sweep.py": "AGDA",
}

IMPORT_SCRATCH = (
    "import os as _o, sys as _s\n"
    "_s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))\n"
    "from agda_lex import module_path   # THE path<->module authority; never re-derive\n"
)
IMPORT_SCRIPTS = (
    "import os as _o, sys as _s\n"
    "_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.dirname("
    "_o.path.abspath(__file__))), \"scratch\"))\n"
    "from agda_lex import module_path   # THE path<->module authority; never re-derive\n"
)


def convert(src):
    """(new_src, n) — pure, so the decision is inspectable without writing."""
    n = 0
    for pat, repl in P2M:
        src, k = pat.subn(repl, src)
        n += k
    return src, n


def _selftest():
    """Counted — a hardcoded total once hid an added case (prune_imports.py:332)."""
    cases = []

    def check(name, got, want):
        cases.append((name, got == want, got, want))

    s, n = convert('    m = p[len(AG) + 1:-5].replace("/", ".")\n')
    check("root-stripping form", s.strip(), "m = module_path(p, AG)")
    check("counted", n, 1)

    s, _ = convert('    mod = path[:-len(".agda")].replace("/", ".")\n')
    check("self-documenting-suffix form -> empty root",
          s.strip(), 'mod = module_path(path, "")')

    s, _ = convert('    return rel[:-5].replace("/", ".")\n')
    check("magic-5 form -> empty root", s.strip(), 'return module_path(rel, "")')

    s, _ = convert(
        '    return os.path.relpath(os.path.abspath(path), AGDA)'
        '[:-5].replace("/", ".")\n')
    check("relpath/abspath wrapper collapses into the root argument",
          s.strip(), "return module_path(path, AGDA)")

    # ⚑ A bare stem strip is NOT a module conversion — no `.replace`. Converting it
    # would change the value from a PATH to a dotted NAME, silently.
    stem = '    d = p[:-5]\n'
    check("bare stem strip untouched", convert(stem)[0], stem)

    # ⚑ `.agdai` must never be swept: module_path strips only `.agda`, so the tail
    # `i` would survive into the module name.
    ai = '    m = p[:-6].replace("/", ".")\n'
    check(".agdai-shaped strip untouched", convert(ai)[0], ai)

    # ⚑ A trailing expression after the conversion must survive (scope_fix:136 appends
    # a "." for a prefix probe).
    s, _ = convert('    mod = path[:-len(".agda")].replace("/", ".") + "."\n')
    check("trailing expression preserved", s.strip(),
          'mod = module_path(path, "") + "."')

    ok = sum(1 for _, good, _, _ in cases if good)
    for name, good, got, want in cases:
        if not good:
            print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
    print(f"convert_path_helpers selftest: {ok}/{len(cases)}")
    return 0 if ok == len(cases) else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    apply = "--apply" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")] or sorted(ROOTS)
    if apply:
        edit_snapshot.guard(f"convert_path_helpers ({len(files)} file(s))", files)
    total = 0
    for rel in files:
        p = os.path.join(os.path.dirname(HERE), rel)
        if not os.path.isfile(p):
            print(f"  skip (absent): {rel}")
            continue
        src = open(p, encoding="utf-8").read()
        new, n = convert(src)
        if not n:
            continue
        if "from agda_lex import module_path" not in new:
            hdr = IMPORT_SCRIPTS if rel.startswith("scripts/") else IMPORT_SCRATCH
            L = new.split("\n")
            k = max((i for i, l in enumerate(L[:60])
                     if re.match(r"^(import|from)\s", l)), default=0) + 1
            new = "\n".join(L[:k]) + "\n" + hdr + "\n".join(L[k:])
        total += n
        print(f"{n:3d} {'converted' if apply else 'would convert'}  {rel}")
        if apply:
            open(p, "w", encoding="utf-8").write(new)
    print(f"{total} site(s) {'converted' if apply else 'convertible'}"
          f"{'' if apply else ' (dry run; pass --apply)'}")
