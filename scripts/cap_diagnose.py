#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""cap_diagnose.py — is a module's cost ELABORATION or LOAD? Measure, don't guess.

WHY THIS EXISTS.  The two costs demand OPPOSITE mitigations, and they are
indistinguishable from a failure exit code:

  · ELABORATION — the module's own content is expensive.  Splitting/sharding it
    WORKS: an elaboration peak is per-module, so dividing the content at an
    associative boundary divides the peak.
  · LOAD — reading the dependency closure's interfaces is expensive.  Splitting
    the module does NOTHING (every shard reloads the same closure); only
    shrinking or SEALING the closure moves it.

Applying the split lever to a load floor produces no change and looks like a
wall; applying the seal lever to an elaboration peak seals the wrong thing.  So
the determination has to be mechanical, and so does the recommendation.

METHOD (three measurements, all real compiles under membudget):
  BASE   an empty module            → agda's irreducible baseline
  LOAD   a module importing exactly this target's imports, defining NOTHING
                                    → the interface-closure cost
  TOTAL  the target itself, forced (its .agdai is removed first)
Then ELAB = TOTAL − LOAD and CLOSURE = LOAD − BASE.

⚑ THE FORCED RECHECK IS LOAD-BEARING.  agda SKIPS a module whose .agdai is
up to date and exits 0 having done nothing — a false green that reads exactly
like a fix.  Any measurement that does not delete the .agdai first is measuring
the cache.  (This tool exists because that false green was believed three times.)

Peaks are maxRSS, which over-counts the OOM-relevant footprint but is the same
quantity the cap ratchet and membudget's autobudget use, so the numbers are
comparable to the rest of the toolchain.

    cap_diagnose.py <Module.agda> ...          # run from agda/
    cap_diagnose.py --heap 64 <Module.agda>    # cap to judge against (default 64)
"""

import os
import re
import subprocess
import sys
import tempfile
import os as _o, sys as _s

_s.path.insert(
    0, _o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))), "scratch")
)
from agda_lex import module_path  # THE path<->module authority; never re-derive

IMPORT = re.compile(r"^\s*(?:open\s+)?import\s+(\S+)")
LADDER = [64, 96, 128, 192, 256, 384]


def imports_of(path):
    """The target's imported modules (statement-aware: a `using (…)` may sit on
    an indented continuation, and a line-wise scan would take it for a module)."""
    mods, lines = [], open(path, encoding="utf-8").read().split("\n")
    for l in lines:
        if l.lstrip().startswith("--"):
            continue
        m = IMPORT.match(l)
        if m:
            mods.append(m.group(1))
    return list(dict.fromkeys(mods))


def run(src_dir, target, heap, root):
    """Compile the FILE `target` at -M<heap>m; → (exit, peak_mb).

    agda is given a PATH, not a module name: a bare module name resolves only
    against the include path and fails with a scope error, which is easily
    mistaken for a real one."""
    cmd = [
        "/usr/bin/time",
        "-v",
        "agda",
        "--safe",
        "--without-K",
        "+RTS",
        f"-M{heap}m",
        "-RTS",
        "-i.",
        f"-i{src_dir}",
        target,
    ]
    p = subprocess.run(
        [os.path.join(root, "scripts", "membudget"), "run", "384", "capdiag", "--"] + cmd,
        capture_output=True,
        text=True,
        cwd=os.path.join(root, "agda"),
    )
    out = p.stdout + p.stderr
    m = re.search(r"Maximum resident set size \(kbytes\): (\d+)", out)
    return p.returncode, (int(m.group(1)) // 1024 if m else -1)


def probe(tmp, name, body, heap, root):
    p = os.path.join(tmp, name + ".agda")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(f"{{-# OPTIONS --safe --without-K #-}}\n\nmodule {name} where\n\n{body}\n")
    return run(tmp, p, heap, root)


def verdict(base, load, total, cap):
    """Classify, then name the lever that actually applies to THAT cost."""
    closure, elab = load - base, total - load
    span = max(total - base, 1)
    if elab <= 0.25 * span:
        kind = "LOAD-BOUND"
        rec = (
            "shrink or SEAL the closure — splitting this module cannot help, "
            "every shard reloads the same interfaces. In order of leverage: "
            "(1) prune_imports.py — drop imports it does not reference; "
            "(2) `opaque` the DEPENDENCIES' proof definitions so their "
            "interfaces ship a handle, not an unfoldable body; "
            "(3) split_param_module.py the heavy dep so this module applies "
            "one shard's telescope instead of the whole body; "
            "(4) retire any barrel/capstone in the closure."
        )
    elif elab >= 0.60 * span:
        kind = "ELABORATION-BOUND"
        rec = (
            "shard the CONTENT — the cost is this module's own elaboration. "
            "(1) MULTI-DEFINITION module → split_lemmas.py: one definition per "
            "file, each its own elaboration unit. "
            "(2) SINGLE-DEFINITION module (nothing left to divide horizontally) "
            "→ STAGE THE PROOF: a dense composite (`trans A B`, a cong-chain) "
            "has its midpoint named as an intermediate lemma, and EACH STAGE IS "
            "SEALED `opaque`. A consumer then composes handles instead of "
            "re-normalising the chain, so the peak is the largest single stage "
            "rather than the whole composite. "
            "(3) STILL OVER after staging → the dense redex is UPSTREAM: recurse "
            "and stage the proof in the DEPENDENCY that defines it. "
            "⚑ Splitting lemmas and staging proofs are ONE move at two grades — "
            "just as split_lemmas recurses up the dep chain, so does staging. "
            "⚑ SEAL AT THE STAGE BOUNDARY INSIDE THE PROOF, never the neutral "
            "the proof is ABOUT: sealing the neutral starves the very consumer "
            "whose content is that computation (measured — it fails with a scope "
            "error, not a smaller peak)."
        )
    else:
        kind = "MIXED"
        rec = (
            "both levers apply; take the closure first (prune_imports.py, then "
            "`opaque` the deps' proofs) since it is cheaper and non-invasive, "
            "then re-measure before sharding the content."
        )
    if total <= cap:
        kind += " (under cap)"
    return kind, closure, elab, rec


def main():
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip()
    argv = sys.argv[1:]
    cap = int(argv[argv.index("--heap") + 1]) if "--heap" in argv else 64
    targets = [a for a in argv if not a.startswith("--") and a.endswith(".agda")]
    if not targets:
        raise SystemExit(__doc__)

    with tempfile.TemporaryDirectory() as tmp:
        _, base = probe(tmp, "CapDiagEmpty", "", 384, root)
        print(f"BASE (empty module): {base} MB\n")
        for t in targets:
            mod = module_path(t, "")
            core = os.path.join(root, "agda", "_build", "2.8.0", "agda", t + "i")
            if os.path.exists(core):
                os.remove(core)  # FORCE a real recheck; never measure the cache
            _, load = probe(
                tmp,
                "CapDiagLoad",
                "\n".join(f"import {m}" for m in imports_of(os.path.join(root, "agda", t))),
                384,
                root,
            )
            rc, total = run(os.path.join(root, "agda"), t, 384, root)
            if rc != 0:
                print(f"{mod}\n  UNBUILDABLE even at -M384m (exit {rc})\n")
                continue
            # Smallest heap on the ladder that actually builds it — each attempt
            # forces a fresh recheck, or we would be re-reading the .agdai the
            # PREVIOUS rung just wrote and calling that a pass.
            need = None
            for h in LADDER:
                if os.path.exists(core):
                    os.remove(core)
                if run(os.path.join(root, "agda"), t, h, root)[0] == 0:
                    need = h
                    break
            kind, closure, elab, rec = verdict(base, load, total, cap)
            print(f"{mod}")
            print(f"  total {total} MB = base {base} + closure {closure} + elaboration {elab}")
            print(f"  verdict: {kind}; needs -M{need}m (cap is -M{cap}m)")
            print(f"  → {rec}\n")


if __name__ == "__main__":
    main()
