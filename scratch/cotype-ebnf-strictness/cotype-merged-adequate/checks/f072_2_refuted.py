# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
import sys, os, re, importlib.util
HERE=os.path.dirname(os.path.realpath(__file__)); ROOT=os.path.dirname(HERE)
KEY="f072_2_refuted"
src=open(os.path.join(ROOT,"warrants.bib")).read()
claim=re.sub(r'\s+',' ',re.search(r'@misc\{'+re.escape(KEY)+r',(.*?)\n\}',src,re.S).group(1))
mlist=re.search(r'non-cyc(?:lotomic)? degrees?\s*\[([\d,\s]+)\]', claim)
if not mlist: print(f"{KEY}: prose no longer asserts a non-cyc degree list"); sys.exit(1)
asserted=sorted([int(x) for x in mlist.group(1).split(',')], reverse=True)
sys.path.insert(0, os.path.join(ROOT,"witnesses"))
spec=importlib.util.spec_from_file_location("probe_simplex_faces", os.path.join(ROOT,"witnesses","probe_simplex_faces.py"))
pr=importlib.util.module_from_spec(spec); spec.loader.exec_module(pr)
got=sorted(pr.compute("(2,3,5)")["nc_degs"], reverse=True)
if got != asserted: print(f"PROSE!=COMPUTE {KEY}: prose {asserted} vs probe {got}"); sys.exit(1)
print(f"{KEY}: prose-asserted non-cyc degrees {asserted} reproduced by probe"); sys.exit(0)
