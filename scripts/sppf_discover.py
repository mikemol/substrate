#!/usr/bin/env python3
"""sppf_discover.py — AI-d: the SEMANTIC-SPPF discovery SUITE (composed). The three semantic-SPPF tools were live but
orphaned AS A SUITE -- three loose entry points run by hand, findings untracked. This composes them into ONE entry
that runs all three and frames their output as the BRIDGE BACKLOG (unconstructed cross-module correspondences --
candidate ≃ bridges, found structurally). They are DISTINCT lenses, not redundant:

  * sppf_label           -- the SAME OBJECT built in >1 module (same canonical name across files) -> a ≃ bridge.
  * type_sppf            -- the structural-skeleton SPPF (types hashed by shape) -> the structure substrate.
  * type_sppf_crosslayer -- isomorphism classes ranked by the DEP-DEPTH SPAN they cross -> the cross-silo bridges.

Audit verdict (AI-d): all four semantic-SPPF tools RUN (not bitrotted). sppf_node_index is the LIVE collision-index
GATE (.githooks/pre-commit; disambiguates colliding NAMES) -- separate purpose, already composed. The three above
are KEPT (compose, not retire): they find REAL unconstructed bridges -- e.g. sppf_label's ⟦Wedge⟧ (Nat.GCD.Wedge +
Algebra.Wedge) was just CONSTRUCTED by AI-Q's generic-Quot unification (recon : C→C→C→C). That a flagged bridge got
built validates the suite; its remaining findings are the standing backlog. NOT a pass/fail gate -- the candidates
are advisory (a backlog to construct), not invariants to enforce.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
LENSES = [("sppf_label",           "same OBJECT built in >1 module (≃ bridge)"),
          ("type_sppf",            "structural-skeleton SPPF (shape substrate)"),
          ("type_sppf_crosslayer", "iso classes ranked by cross-silo dep-depth span (the bridges)")]


def main():
    print("sppf_discover (AI-d): the semantic-SPPF BRIDGE-DISCOVERY suite -- run the three lenses, read the backlog.\n")
    ok = True
    for mod, what in LENSES:
        print(f"================ {mod} -- {what} ================")
        r = subprocess.run([sys.executable, os.path.join(HERE, mod + ".py")], capture_output=True, text=True, timeout=300)
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            ok = False; sys.stderr.write(r.stderr)
        print()
    print(f"  {'PASS' if ok else 'FAIL'} — three live discovery lenses, composed into one entry. Output = the bridge")
    print(f"  backlog (advisory candidates, NOT a gate). node_index is the separate live collision gate. Constructed")
    print(f"  so far: ⟦Wedge⟧ (AI-Q generic-Quot unification). Re-run after structural work to refresh the backlog.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
