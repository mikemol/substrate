#!/usr/bin/env python3
"""
B3 — proof that S4's normal Klein-four shares exactly one V2 (the seam)
with each of its three interface Klein-fours, and that the two interface
V4s meet trivially.

Self-contained, no dependencies. Run: python3 b3_shared_v2_proof.py
Substrate is explicit: S4 = permutations of 4 letters D,C,S,W (positions 0..3),
comp = permutation composition, inv = inverse. Nothing is taken on faith;
every group fact is recomputed from these.
"""
from itertools import permutations, combinations
from collections import Counter

LET = "DCSW"

def perm_name(p):
    seen=[False]*4; cycles=[]
    for i in range(4):
        if seen[i]: continue
        c=[]; j=i
        while not seen[j]:
            seen[j]=True; c.append(j); j=p[j]
        if len(c)>1: cycles.append(c)
    return "e" if not cycles else "".join("("+"".join(LET[k] for k in c)+")" for c in cycles)

S4 = [tuple(p) for p in permutations(range(4))]
e  = (0,1,2,3)
def comp(a,b): return tuple(a[b[i]] for i in range(4))   # (a∘b)(i)=a(b(i))
def inv(a):
    r=[0]*4
    for i in range(4): r[a[i]]=i
    return tuple(r)

def cycle_type(p):
    seen=[False]*4; ct=[]
    for i in range(4):
        if seen[i]: continue
        n=0; j=i
        while not seen[j]:
            seen[j]=True; n+=1; j=p[j]
        ct.append(n)
    return tuple(sorted(ct, reverse=True))

def is_subgroup(elts):
    s=set(elts)
    if e not in s: return False
    for a in s:
        if inv(a) not in s: return False
        for b in s:
            if comp(a,b) not in s: return False
    return True

def is_klein_four(elts):
    return (len(elts)==4 and is_subgroup(elts)
            and all(x==e or comp(x,x)==e for x in elts))

def signature(V):
    return dict(Counter(cycle_type(x) for x in V if x!=e))

def is_normal(V):
    # V normal iff gVg^-1 = V for all g in S4
    Vs=set(V)
    return all({comp(comp(g,x),inv(g)) for x in V}==Vs for g in S4)

def main():
    invols=[p for p in S4 if p!=e and comp(p,p)==e]
    assert len(invols)==9, "S4 must have 9 involutions"

    V4s=set()
    for trio in combinations(invols,3):
        elts=(e,)+trio
        if is_klein_four(elts):
            V4s.add(frozenset(elts))
    V4s=sorted(V4s, key=lambda V: sorted(perm_name(x) for x in V if x!=e))
    assert len(V4s)==4, "S4 must have exactly 4 Klein-four subgroups"

    normal=[V for V in V4s if is_normal(V)]
    assert len(normal)==1 and signature(normal[0])=={(2,2):3}
    N=normal[0]
    interfaces=[V for V in V4s if V!=N]

    print("S4 Klein-four subgroups (4 total):")
    for V in V4s:
        tag="NORMAL (gauge)" if V==N else "interface"
        body="{e, "+", ".join(sorted(perm_name(x) for x in V if x!=e))+"}"
        print(f"  [{tag:14}] {body}  sig={signature(V)}")

    print("\nGauge ∩ interface  (expect exactly one shared V2 = the seam):")
    ok_gauge=True
    for V in interfaces:
        shared=[perm_name(x) for x in (N&V) if x!=e]
        print(f"  normal ∩ {{{', '.join(sorted(perm_name(x) for x in V if x!=e))}}} = {shared}")
        ok_gauge &= (len(shared)==1)

    print("\nInterface ∩ interface  (expect trivial):")
    ok_iface=True
    for A,B in combinations(interfaces,2):
        shared=[perm_name(x) for x in (A&B) if x!=e]
        print(f"  {{{', '.join(sorted(perm_name(x) for x in A if x!=e))}}} ∩ "
              f"{{{', '.join(sorted(perm_name(x) for x in B if x!=e))}}} = {shared if shared else '∅'}")
        ok_iface &= (len(shared)==0)

    seams=sorted(perm_name(x) for x in N if x!=e)
    print(f"\nThe three seams (= the three double-transpositions) = {seams}")
    print(f"\nB3 (gauge shares exactly one V2 with each interface): {ok_gauge}")
    print(f"B3 (interface V4s meet trivially):                     {ok_iface}")
    print(f"\nALL B3 CHECKS PASS: {ok_gauge and ok_iface}")

if __name__=="__main__":
    main()