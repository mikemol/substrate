#!/usr/bin/env python3
# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
# =============================================================================
# species_store.py  --  the mechanism-keyed residue store + predictions lattice
#
# ONE brick `species(rung, p)` over a sqlite residue table, replacing the six
# ad-hoc probes. Two things the mechanism-in-the-key buys (user's design):
#   (1) SELECT by mechanism match: residues are keyed (rung, perm, mechanism),
#       so the species tables are QUERIES (GROUP BY mechanism, rung), and the
#       "is order-4 just order-2 composed?" question is a JOIN, not a new run.
#   (2) Predict where the next species lives: the prime-indexed tower conjecture
#       is a prediction over EMPTY cells of a (rung, mechanism) lattice; the next
#       experiment to run is the highest-discrimination NULL cell.
#
# Residue stored is BASIS-INVARIANT (det, singular?, kernel_dim, spectrum,
# root-of-unity) -- the matrix itself is basis-dependent scratch, never persisted.
# Exact arithmetic throughout (sympy srepr strings, never floats). Compute-once,
# across runs AND across sessions: the table is the durable witness.
# =============================================================================
import sqlite3, sys, os
import sympy as sp
from itertools import combinations, permutations
from math import comb, factorial, gcd

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "species.db")

# ---------- the rep (basis-dependent; only invariants are persisted) ----------
def cyc_setup(nv):
    edges = list(combinations(range(nv), 2)); eidx = {e: i for i, e in enumerate(edges)}
    tree = set((0, j) for j in range(1, nv)); rows = []
    for e in edges:
        if e in tree: continue
        a, b = e; v = [0]*len(edges); v[eidx[e]] += 1
        if a != 0: v[eidx[(0, a)]] -= 1
        if b != 0: v[eidx[(0, b)]] += 1
        rows.append(v)
    C = sp.Matrix(rows); Cpinv = C.T*(C*C.T).inv()
    return edges, eidx, C, Cpinv

def rep(p, edges, eidx, C, Cpinv):
    m = len(edges); P = sp.zeros(m, m)
    for j, (a, b) in enumerate(edges):
        pa, pb = p[a], p[b]; e2 = (pa, pb) if pa < pb else (pb, pa); P[eidx[e2], j] = 1
    return C*P*Cpinv

def cyc_type(g, nv):
    seen = [False]*nv; parts = []
    for s in range(nv):
        if seen[s]: continue
        l = 0; x = s
        while not seen[x]: seen[x] = True; x = g[x]; l += 1
        if l > 1: parts.append(l)
    return tuple(sorted(parts, reverse=True)) or (1,)

# ---------- mechanism = the order-p cycle structure being probed ----------
def order_p_classes(p):
    """The cycle-types that are the 'mechanism' for prime p: (p), (p,p), ..."""
    return [(p,), (p, p)]

def mechanism_name(p):
    return f"order-{p}"

# ---------- the store ----------
def connect():
    db = sqlite3.connect(DB)
    db.execute("""CREATE TABLE IF NOT EXISTS residue(
        rung INT, perm TEXT, mechanism TEXT, cyc_type TEXT,
        det TEXT, singular INT, kernel_dim INT, spectrum TEXT, root_of_unity TEXT,
        PRIMARY KEY(rung, perm, mechanism))""")
    db.execute("""CREATE TABLE IF NOT EXISTS predictions(
        rung INT, mechanism TEXT, p INT, nv INT,
        predicted_singular INT,   -- 1 = conjecture says species IGNITES here
        actual_singular INT,      -- count of singular cells found; NULL = unfilled
        PRIMARY KEY(rung, mechanism))""")
    db.commit()
    return db

def root_of_unity_tag(eigs):
    """Classify the spectrum's torsion flavor: does it contain primitive p-th roots?"""
    tags = []
    s = str(eigs)
    if "-1:" in s or "-1," in s or s.strip().startswith("{-1"): tags.append("-1(order2)")
    if "sqrt(3)*I" in s: tags.append("omega(order3)")
    if "sqrt(5)" in s: tags.append("order5-flavor")
    if "0:" in s or " 0," in s or "0]" in s: tags.append("ZERO(annihilation)")
    return ";".join(tags) if tags else "rational"

# ---------- the ONE brick: species(rung, p) ----------
def species(rung, p, db=None, class_target=None, verbose=True):
    """Compute-or-fetch the order-p zero-divisor species at this rung.
       Writes every (rung, perm, mechanism) residue to the store; returns summary."""
    own = db is None
    if own: db = connect()
    nv = rung + 1; dim = comb(nv-1, 2)
    mech = mechanism_name(p)
    targets = [class_target] if class_target else order_p_classes(p)

    # how many residue rows already present for this (rung, mechanism)?
    have = db.execute("SELECT COUNT(*) FROM residue WHERE rung=? AND mechanism=?",
                      (rung, mech)).fetchone()[0]
    edges = eidx = C = Cpinv = None
    I = None
    n_singular = 0; n_total = 0; ru_tags = set()
    for p_perm in permutations(range(nv)):
        ct = cyc_type(p_perm, nv)
        if ct not in targets: continue
        n_total += 1
        permkey = ",".join(map(str, p_perm))
        row = db.execute("SELECT singular, root_of_unity FROM residue WHERE rung=? AND perm=? AND mechanism=?",
                         (rung, permkey, mech)).fetchone()
        if row is not None:                      # REUSE: already computed
            if row[0]: n_singular += 1
            if row[1]: ru_tags.add(row[1])
            continue
        # compute (lazily build the basis once)
        if edges is None:
            edges, eidx, C, Cpinv = cyc_setup(nv); I = sp.eye(dim)
        T = rep(p_perm, edges, eidx, C, Cpinv)
        det = sp.cancel(T.det())                 # cheaper than full simplify for det=0 test
        singular = 1 if det == 0 else 0
        # eigenvals (expensive symbolic root-finding) ONLY for singular cells -- the
        # zero-divisor species is what we're after; clean cells need only det.
        if singular:
            kdim = len(T.nullspace())
            eigs = {sp.nsimplify(k): v for k, v in T.eigenvals().items()}
            ru = root_of_unity_tag(eigs)
            eigs_s = sp.srepr(eigs)
        else:
            kdim = 0; ru = "rational(nonsingular)"; eigs_s = ""
        db.execute("INSERT OR REPLACE INTO residue VALUES(?,?,?,?,?,?,?,?,?)",
                   (rung, permkey, mech, str(ct), sp.srepr(det), singular, kdim,
                    eigs_s, ru))
        db.commit()                               # INCREMENTAL: progress survives a kill
        if singular: n_singular += 1
        ru_tags.add(ru)
        if verbose and n_total % 2000 == 0:
            print(f"    ... {n_total} elems scanned, {n_singular} singular so far", flush=True)
    db.commit()
    if verbose:
        reused = "(all reused)" if have >= n_total and n_total > 0 else f"(had {have})"
        print(f"  species(rung={rung}, p={p}) nv={nv}: {n_total} order-{p} elems, "
              f"{n_singular} SINGULAR {reused} | tags: {sorted(t for t in ru_tags if t)}", flush=True)
    # update predictions.actual
    db.execute("""INSERT OR REPLACE INTO predictions(rung,mechanism,p,nv,predicted_singular,actual_singular)
                  VALUES(?,?,?,?,
                    COALESCE((SELECT predicted_singular FROM predictions WHERE rung=? AND mechanism=?), ?),
                    ?)""",
               (rung, mech, p, nv, rung, mech, predict_ignition(rung, p), n_singular))
    db.commit()
    if own: db.close()
    return n_singular, n_total

# ---------- the prime-indexed tower prediction ----------
def predict_ignition(rung, p):
    """Conjecture: order-p species ignites where p | nv and nv > p. Returns 1/0."""
    nv = rung + 1
    return 1 if (nv % p == 0 and nv > p) else 0

def seed_predictions(db, rungs, primes):
    for rung in rungs:
        nv = rung+1
        for p in primes:
            mech = mechanism_name(p)
            pred = predict_ignition(rung, p)
            db.execute("""INSERT OR IGNORE INTO predictions(rung,mechanism,p,nv,predicted_singular,actual_singular)
                          VALUES(?,?,?,?,?,NULL)""", (rung, mech, p, nv, pred))
    db.commit()

def next_experiment(db):
    """Highest-discrimination UNFILLED cell: a predicted-hot cell not yet tested,
       cheapest first (smallest nv!)."""
    rows = db.execute("""SELECT rung, mechanism, p, nv, predicted_singular
                         FROM predictions WHERE actual_singular IS NULL
                         ORDER BY predicted_singular DESC, nv ASC""").fetchall()
    return rows

def show_lattice(db):
    print("\n  (rung, mechanism) LATTICE  [pred=conjecture, actual=found]")
    print("  rung  nv  mechanism   predicted  actual   verdict")
    for r in db.execute("""SELECT rung,nv,mechanism,predicted_singular,actual_singular
                           FROM predictions ORDER BY p, rung""").fetchall():
        rung,nv,mech,pred,act = r
        if act is None:   verdict = "UNFILLED"
        elif (act>0)==(pred==1): verdict = "CONFIRMS" if act>0 else "confirms-clean"
        else: verdict = "*** REFUTES ***"
        actstr = "?" if act is None else str(act)
        print(f"  {rung:>4} {nv:>3}  {mech:<10} {pred:>9}  {actstr:>6}   {verdict}")

# ---------- CLI ----------
if __name__ == "__main__":
    db = connect()
    if len(sys.argv) >= 2 and sys.argv[1] == "seed":
        # seed prediction lattice over a default grid
        seed_predictions(db, rungs=range(2, 12), primes=[2,3,5,7])
        print("seeded predictions lattice (rungs 2-11, primes 2,3,5,7)")
        show_lattice(db)
    elif len(sys.argv) >= 2 and sys.argv[1] == "lattice":
        show_lattice(db)
    elif len(sys.argv) >= 2 and sys.argv[1] == "next":
        for r in next_experiment(db):
            print(f"  UNFILLED predicted={'HOT' if r[4] else 'clean'}: species(rung={r[0]}, p={r[2]})  nv={r[3]}  frames={factorial(r[3])}")
    elif len(sys.argv) >= 3 and sys.argv[1] == "run":
        rung = int(sys.argv[2]); p = int(sys.argv[3])
        species(rung, p, db=db)
        show_lattice(db)
    else:
        print(__doc__ or "usage: seed | lattice | next | run RUNG P")
    db.close()
