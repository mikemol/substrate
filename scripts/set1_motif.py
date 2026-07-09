#!/usr/bin/env python3
"""set1_motif.py v2 — join multi-line record/module headers before classifying.
Motif = WHY the site is Set₁: what Set-valued thing is fielded or returned."""
import re, glob, collections
def strip_comments(src): return [re.sub(r"--.*$","",l) for l in src.splitlines()]

def join_headers(lines):
    """Return list of (start_lineno, joined_text, is_header). A header spans until
    the line containing 'where' (or the line itself if it has both)."""
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if re.match(r"\s*(record|module|data)\s", l) and "where" not in l:
            j, buf = i, l
            while j+1 < len(lines) and "where" not in buf and j-i < 6:
                j += 1; buf += " " + lines[j].strip()
            out.append((i+1, buf, True)); i = j+1
        else:
            out.append((i+1, l, False)); i += 1
    return out

files = sorted(glob.glob("agda/Substrate/**/*.agda", recursive=True))
set1_records = set()
for f in files:
    for _, t, h in join_headers(strip_comments(open(f,encoding="utf-8").read())):
        m = re.search(r"record\s+([A-Za-z][\w'ᴳ₁₂-]*)", t)
        if m and "Set₁" in t: set1_records.add(m.group(1))

def first_field_block(lines, k):
    blk=[]
    for j in range(k, min(k+16, len(lines))):
        s=lines[j].strip()
        if s.startswith("field"): continue
        if s and not s.startswith(("--","open","private")): blk.append(s)
        if len(blk)>=8: break
    return " ; ".join(blk)

def motif(t, lines, k):
    if re.search(r"record|module|data", t):
        blk = first_field_block(lines, k)
        if re.search(r"\w+\s*:\s*Set\s*(;|$)", blk):            return "M1-fields-bare-carrier"
        if re.search(r"_?≈?\w*_?\s*:\s*\w+\s*→\s*\w+\s*→\s*Set\b", blk): return "M4-fields-Set-valued-relation"
        for r in sorted(set1_records, key=len, reverse=True):
            if re.search(rf":\s*{re.escape(r)}\b", blk):          return "M2-fields-a-Set₁-record"
        if re.search(r":\s*Set\b", blk):                          return "M1-fields-bare-carrier"
        return "M5-record-other"
    return "M3-typeformer-into-Set"

census=collections.Counter(); detail=collections.defaultdict(list)
for f in files:
    lines = strip_comments(open(f,encoding="utf-8").read())
    for ln0, t, h in join_headers(lines):
        if "Set₁" not in t: continue
        m = motif(t, lines, ln0)
        census[m]+=1; detail[m].append((f.replace("agda/Substrate/",""), ln0, t.strip()[:60]))
print(f"  Set₁ sites: {sum(census.values())}   (Set₁-valued records: {len(set1_records)})")
for m,n in census.most_common(): print(f"    {n:4d}  {m}")
print()
for m,_ in census.most_common():
    print(f"  ── {m} ──")
    for f,i,t in detail[m][:2]: print(f"      {f}:{i}: {t}")
