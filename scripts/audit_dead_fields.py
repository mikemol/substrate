#!/usr/bin/env python3
"""audit_dead_fields.py — POSIWID dead at the FIELD level.

A record field that is set but never projected is write-only: data the record
carries that nothing consults. Detection (high-confidence slice):

  For a field name f of record R, count across the (comment-stripped) tree:
    total  = token occurrences of f (R.f / .f / open-projection all yield 'f')
    writes = occurrences of `f =` (record-literal / pattern assignment)
    reads  ≈ total - writes - 1(declaration)
  f is DEAD if reads ≤ 0 — it appears only as its declaration and in
  assignments, never consulted.

Only UNIQUELY-named fields are trusted (a name shared by ≥2 records can't be
attributed by token alone). Caveats: record-PATTERN reads `record{f=p}` look
like writes (so a field only ever destructured-by-pattern may be over-flagged
— rare here, projection is preferred); copattern defs `f x = …` are counted as
reads (conservative — won't false-flag).
"""
import os, re, collections
from _agdatext import split_arrows, strip
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agda", "Substrate"))
text={};
for dp,_,fns in os.walk(ROOT):
    for fn in fns:
        if fn.endswith(".agda"):
            p=os.path.join(dp,fn); text[p]=strip(open(p,encoding="utf-8").read())

# parse record field blocks
rec_fields=collections.defaultdict(list)   # (record,file) -> [fields]
field_owners=collections.defaultdict(list) # fieldname -> [(record,file)]
ftype={}                                   # fieldname -> declared type string
recre=re.compile(r"^record\s+(\S+)")
for p,t in text.items():
    lines=t.splitlines(); i=0
    while i<len(lines):
        m=recre.match(lines[i])
        if m:
            R=m.group(1); j=i+1; infield=False
            while j<len(lines) and (lines[j].strip()=="" or lines[j][:1] in " \t"):
                s=lines[j].strip()
                if s.startswith("field"): infield=True; s=s[5:].strip()
                if infield and " : " in s:
                    nm_part,ty=s.split(" : ",1)
                    for nm in nm_part.split():
                        rec_fields[(R,p)].append(nm); field_owners[nm].append((R,p)); ftype[nm]=ty
                elif infield and s and ":" in s and not s.startswith("--"):
                    nm=s.split(":",1)[0].strip()
                    if nm and " " not in nm:
                        rec_fields[(R,p)].append(nm); field_owners[nm].append((R,p)); ftype[nm]=s.split(":",1)[1]
                j+=1
            i=j; continue
        i+=1

LAW=re.compile(r"≡|≈|assoc|comm|identity|ident|-inv|inv-|refl|sym\b|trans\b|cong|law|coher|naturalit|-stated|triangle|preserv|respect")
def is_law(nm):
    return bool(LAW.search(ftype.get(nm,"")) or LAW.search(nm))

# token + write counts across the tree
tok=collections.Counter(); wr=collections.Counter()
allnames=set(field_owners)
for p,t in text.items():
    for w in re.split(r"[\s()\[\]{};,.\"]+",t):
        if w in allnames: tok[w]+=1
for f in allnames:
    pat=re.compile(re.escape(f)+r"\s*=(?!=)")
    wr[f]=sum(len(pat.findall(t)) for t in text.values())

# producers: a record name appearing as the RESULT type of some signature =
# the record is constructed somewhere (a law-field is then discharged at build).
recnames={R for (R,_) in rec_fields}
produced=set()
sig=re.compile(r"^\s*[^\s:]+\s*:\s*(.+)$")
for t in text.values():
    for line in t.splitlines():
        m=sig.match(line)
        if not m: continue
        res=split_arrows(m.group(1))[-1]
        produced|={w for w in re.split(r"[\s()\[\]{};,.]+",res) if w in recnames}

data_dead=collections.defaultdict(list); law_dead=collections.defaultdict(list)
law_unexercised=collections.defaultdict(list)
ambiguous=0; total_fields=0
for nm,owners in field_owners.items():
    total_fields+=1
    if len(owners)>1: ambiguous+=1; continue          # name collision — can't attribute
    reads=tok[nm]-wr[nm]-1
    if reads<=0:
        (R,p)=owners[0]
        if is_law(nm):
            law_dead[(R,p)].append(nm)
            if R not in produced: law_unexercised[(R,p)].append(nm)  # never built ⇒ never exercised
        else:
            data_dead[(R,p)].append(nm)

rel=lambda p: os.path.relpath(p,ROOT)
nd=sum(len(v) for v in data_dead.values()); nl=sum(len(v) for v in law_dead.values())
print(f"== incompleteness map (never-consulted fields; {ambiguous} name-collisions skipped) ==\n")
print(f"## DATA fields set but never read — {nd} across {len(data_dead)} records")
print(f"   (data carried but no consumer reads it — the using code is unwritten):")
for (R,p),fs in sorted(data_dead.items(), key=lambda kv:-len(kv[1])):
    print(f"   {R:28s} {rel(p)}\n        {', '.join(sorted(fs))}")
nu=sum(len(v) for v in law_unexercised.values())
print(f"\n## LAW/obligation fields never projected — {nl} across {len(law_dead)} records")
print(f"   UNEXERCISED ({nu} laws / {len(law_unexercised)} records): never projected AND")
print(f"   record never constructed ⇒ no proof relies on it ⇒ forces NO distinction")
print(f"   (the realizability hole — implementation owed):")
for (R,p),fs in sorted(law_unexercised.items(), key=lambda kv:-len(kv[1])):
    print(f"      {R:28s} {len(fs):2d}  {rel(p)}")
print(f"   ({nl-nu} other never-projected laws ARE discharged at construction — "
      f"they force their distinction at build, exercised, fine.)")
