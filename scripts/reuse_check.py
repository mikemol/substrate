#!/usr/bin/env python3
"""reuse_check.py — ⟡reuse-before-write-query: lower a PROPOSED def into the EXISTING corpus interner and
report its nearest existing kin + canonical home, or "novel". This is the reuse-search DISCIPLINE
(CLAUDE.md: "before building a new def/lemma/module/bridge, search for the structure it would reinvent")
reconstituted as a mechanical QUERY over a not-yet-committed skeleton — the propose→nearest primitive the
FIND tools lacked (jea_pysim --clusters/--extract consume already-interned artifacts; nothing lowered a
PROPOSAL). The negative axis (a discipline the actor must remember) becomes a positive affordance (a command).

REUSES jea_pysim.Corpus entirely — no new interner: add_file (.py) / add_agdai (compiled .agdai) interns the
proposal into a reference corpus. The relation to each existing def is kept GRADED as the WEDGE, not collapsed
to a scalar: for the proposal's support Sₚ and an existing def's Sₑ it reports ∩ (shared = the reuse), Sₚ∖Sₑ
(what the proposal ADDS), Sₑ∖Sₚ (what the existing carries beyond it), and the subset verdict those decide —
Sₚ⊆Sₑ (instantiate the existing) · Sₑ⊆Sₚ (generalize the existing) · = (verbatim) · overlap (factor the core).
A scalar "0.32 / WEAK" would crush all four cells + the direction into one number ([[dont-collapse-to-smallest-
representable]]); NOVEL means ∩=∅ with every existing def, a structural fact, not a threshold.

USAGE
  scripts/reuse_check.py --propose scratch/stub.py
        → nearest existing def in the tooling corpus (scripts/*.py + jea/**/*.py by default)
  scripts/reuse_check.py --propose _build/…/MyProposal.agdai
        → nearest existing def in the substrate .agdai corpus (agda/_build/**/*.agdai by default)
  scripts/reuse_check.py --propose stub.py --against 'scripts/*.py' 'jea/metalanguage/*.py' --top 8

HONEST BOUNDARY: add_agdai needs a COMPILED core, so an Agda proposal must be typechecked first (write the
skeleton → `agda` it → point here at its .agdai). For the cheaper "does this RECORD already exist / how many
instances inhabit it?" question (no compile), use scratch/set1_consolidate.py's type-head report. Read-only.
"""
import os, sys, glob, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "jea", "metalanguage"))
import jea_pysim as P

DEFAULT_PY = ["scripts/*.py", "jea/metalanguage/*.py", "jea/*.py"]
DEFAULT_AGDAI = ["agda/_build/**/*.agdai"]


def expand(globs):
    out = []
    for g in globs:
        gg = g if os.path.isabs(g) else os.path.join(ROOT, g)
        out.extend(sorted(glob.glob(gg, recursive=True)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--propose", required=True, help="the PROPOSED def file (.py stub, or a compiled .agdai)")
    ap.add_argument("--against", nargs="*", default=None,
                    help="reference-corpus globs (default: tooling .py for a .py proposal; the .agdai tree for .agdai)")
    ap.add_argument("--top", type=int, default=6)
    args = ap.parse_args()

    prop = args.propose if os.path.isabs(args.propose) else os.path.join(ROOT, args.propose)
    if not os.path.exists(prop):
        sys.exit(f"reuse_check: proposal not found: {prop}")
    is_agda = prop.endswith(".agdai")
    ref_globs = args.against or (DEFAULT_AGDAI if is_agda else DEFAULT_PY)
    refs = [f for f in expand(ref_globs) if os.path.abspath(f) != os.path.abspath(prop)]
    if not refs:
        sys.exit(f"reuse_check: reference corpus empty for {ref_globs}")

    print(f"# ⟡reuse-before-write-query — interning {len(refs)} reference files …", file=sys.stderr)
    C = P.Corpus()
    for f in refs:
        try:
            (C.add_agdai if f.endswith(".agdai") else C.add_file)(f)
        except Exception:
            continue
    n_ref = len(C.units)
    try:
        (C.add_agdai if is_agda else C.add_file)(prop)
    except Exception as e:
        sys.exit(f"reuse_check: could not intern proposal {prop}: {e}")
    proposal_units = C.units[n_ref:]
    if not proposal_units:
        sys.exit("reuse_check: proposal interned to 0 units (empty / unparsed / undecodable core)")

    print(f"# proposal '{os.path.relpath(prop, ROOT)}' → {len(proposal_units)} def(s); "
          f"reference corpus = {n_ref} defs\n", file=sys.stderr)

    for pu in proposal_units:
        P_ = pu.support
        rel = []                                          # per candidate: the WEDGE, kept graded
        for ru in C.units[:n_ref]:
            E = ru.support
            inter = P_ & E
            if not inter:
                continue
            p_only, e_only = P_ - E, E - P_               # the two residues (symmetric difference = their union)
            if not p_only and not e_only:
                verdict = "IDENTICAL     reuse it verbatim"
            elif not p_only:
                verdict = "PROPOSAL ⊆     instantiate the existing — it already covers you"
            elif not e_only:
                verdict = "EXISTING ⊆     the existing is a special case — generalize/extend it"
            else:
                verdict = "OVERLAP        factor the shared core; each keeps its residue"
            rel.append((len(inter), len(p_only), len(e_only), verdict, ru))
        # rank: fewest UNSHARED-by-proposal first (⊆ ⇒ 0 = fully reusable), then largest shared core
        rel.sort(key=lambda t: (t[1], -t[0]))
        if not rel:
            print(f"■ {pu.name}   → NOVEL  (|support|={len(P_)}; ∩ with every existing def is ∅)\n")
            continue
        print(f"■ {pu.name}   (|support|={len(P_)})")
        print(f"     {'∩':>5} {'+prop':>6} {'+exist':>7}  relation / move                                  where")
        for ninter, np, ne, verdict, ru in rel[:args.top]:
            loc = f"{os.path.relpath(ru.path, ROOT)}:{ru.lineno}" if ru.lineno and ru.lineno > 0 \
                else os.path.relpath(ru.path, ROOT)
            print(f"     {ninter:>5} {np:>6} {ne:>7}  {verdict:48} {ru.name}  {loc}")
        print()


if __name__ == "__main__":
    main()
