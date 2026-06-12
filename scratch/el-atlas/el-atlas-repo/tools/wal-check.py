#!/usr/bin/env python3
"""WAL checker: the log must sanction the state, the state must honor
the log. Checks: (1) wal.md well-formed — BEGIN/END(/ABORT) pairing in
order, at most one open BEGIN and only as the final entry; (2) a dirty
working tree requires an open BEGIN (unsanctioned deltas fail); (3) the
last END's recorded head must be HEAD or an ancestor of it; (4) every
END's declared artifacts must exist; (5) any BEGIN carrying pre=<sha>
must have that sha an ancestor of its matching END's head=<sha> (the
move's delta pre..head is well-formed; moves predating the W14
convention carry no pre= and are exempt). Exit 0 PASS / 1 FAIL.
Usage: wal-check.py [--quiet]"""
import io, os, re, subprocess, sys
R=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
q='--quiet' in sys.argv
def say(s):
    if not q: print(s)
def fail(s): print('WAL-CHECK FAIL: '+s); sys.exit(1)
txt=io.open(os.path.join(R,'wal.md'),encoding='utf-8').read()
events=[]
for ln in txt.splitlines():
    m=re.match(r'(BEGIN|END|ABORT) (W\d+)',ln.strip())
    if m: events.append((m.group(1),m.group(2),ln.strip()))
open_id=None
for kind,wid,ln in events:
    if kind=='BEGIN':
        if open_id: fail(f'{wid} opened while {open_id} still open')
        open_id=wid
    else:
        if open_id!=wid: fail(f'{kind} {wid} without matching open BEGIN')
        open_id=None
dirty=subprocess.run(['git','-C',R,'status','--porcelain'],capture_output=True,text=True).stdout.strip()
if dirty and not open_id: fail('working tree dirty with no open BEGIN — unsanctioned deltas:\n'+dirty[:300])
ends=[ln for k,w,ln in events if k=='END']
# check (5): pre..head well-formedness per move
import collections
begin_pre={}; end_head={}
for k,w,ln in events:
    if k=='BEGIN':
        m=re.search(r'pre=([0-9a-f]{7,})',ln)
        if m: begin_pre[w]=m.group(1)
    if k=='END':
        m=re.search(r'head=([0-9a-f]{7,})',ln)
        if m: end_head[w]=m.group(1)
for w,pre in begin_pre.items():
    if w in end_head:
        r=subprocess.run(['git','merge-base','--is-ancestor',pre,end_head[w]],capture_output=True)
        if r.returncode!=0: fail(f'{w}: pre={pre} is not an ancestor of its END head={end_head[w]}')
if ends:
    m=re.search(r'head=([0-9a-f]{7,})',ends[-1])
    if m:
        r=subprocess.run(['git','-C',R,'merge-base','--is-ancestor',m.group(1),'HEAD'])
        if r.returncode!=0: fail(f'last END head {m.group(1)} is not an ancestor of HEAD')
    for e in ends:
        a=re.search(r'artifacts=(\S+)',e)
        if a:
            for p in a.group(1).split(','):
                if p and not os.path.exists(os.path.join(R,p)): fail(f'declared artifact missing: {p}')
say(f'WAL-CHECK PASS: {sum(1 for k,_,_ in events if k=="BEGIN")} moves logged; open: {open_id or "none"}; tree {"dirty (sanctioned)" if dirty else "clean"}')
sys.exit(0)
