#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Build the findings-only sub-paper — the IRREDUCIBLE domain content of the ratchet.

This is the only thing paperkit cannot do for us: the SCOPING JUDGEMENT that the
behavioral ratchet applies to the 14 probe-backed findings, not the 840 honest
existence-notes (process/roster records with no probe — existence is their ceiling).
Everything resumable/incremental is delegated to paperkit's own project/gate/
discriminate (whose --state/--budget IS the driver driving discriminate's pump
witness). We build the sub-paper and conform; we do not wrap.

    python3 ratchet/build_findings_subpaper.py <dest_dir>
"""
import os, re, sys, shutil
COTYPE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# The scoping judgement: the 14 findings carrying a behavioral-eligible cmd:/claim: check.
FINDINGS = ['f072_1_confirmed','f072_2_refuted','f089_1_data','f089_2_solid','f089_3_no-clean-fit',
            'f090_1_complete-data','f090_2_pinned','f090_4_refuted','f091_2_derived','f093_1_derived',
            'f093_2_also-derived','f093_4_verified','f094_5_ruled-out','f085_4_confirmed']

def build(dst):
    for sub in ("witnesses", "checks", "data"):
        s = os.path.join(COTYPE, sub)
        if os.path.isdir(s): shutil.copytree(s, os.path.join(dst, sub), dirs_exist_ok=True)
    src = open(os.path.join(COTYPE, "warrants.bib")).read()
    out, prev = [], None
    for k in FINDINGS:
        m = re.search(r'@misc\{'+re.escape(k)+r',(.*?)\n\}', src, re.S)
        claim = re.search(r'claim\s*=\s*\{(.+?)\}', m.group(1), re.S).group(1)
        chk = re.search(r'check\s*=\s*\{([^}]+)\}', m.group(1)).group(1)
        e = f'@misc{{{k},\n  section = {{findings}},'
        if prev: e += f'\n  from = {{{prev}}}, join = {{; }},'
        e += f'\n  claim = {{{claim}}},\n  check = {{{chk}}}\n}}'
        out.append(e); prev = k
    open(os.path.join(dst, "warrants.bib"), "w").write('\n'.join(out)+'\n')
    open(os.path.join(dst, "rubric.tsv"), "w").write("findings\tThe Probe-Backed Findings\n")
    open(os.path.join(dst, "paper.toml"), "w").write(
        '[paper]\ntitle = "Cotype Findings Ratchet"\nrubric = "rubric.tsv"\n'
        'warrants = ["warrants.bib"]\nout = "paper.md"\nreferences = false\n'
        '[checks.claim]\ncmd = "python3 checks/claims.py {target}"\n')

if __name__ == "__main__":
    build(sys.argv[1])
    print(f"built findings sub-paper ({len(FINDINGS)} claims) at {sys.argv[1]}")
