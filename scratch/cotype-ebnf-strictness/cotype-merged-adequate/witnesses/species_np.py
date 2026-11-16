# SPDX-License-Identifier:Apache-2.0
# Copyright 2026 Mike Mol
"""Numeric (numpy-only) companion to species_store's frame construction.

The nullity path (Φ_p mult = nullity(Φ_p(T))/φ(p)) only needs T as floats — it calls
T.evalf() immediately. Building C·P·Cpinv directly in numpy skips the sympy import
(~0.27s fixed cost per process) and the exact rational inverse. Identical T to float
tolerance; verified against species_store across all probe cases.
"""
from itertools import combinations
import numpy as np

def cyc_setup(nv):
    edges = list(combinations(range(nv), 2)); eidx = {e: i for i, e in enumerate(edges)}
    tree = set((0, j) for j in range(1, nv)); rows = []
    for e in edges:
        if e in tree: continue
        a, b = e; v = [0.0]*len(edges); v[eidx[e]] += 1
        if a != 0: v[eidx[(0, a)]] -= 1
        if b != 0: v[eidx[(0, b)]] += 1
        rows.append(v)
    C = np.array(rows, dtype=float)                 # cycle-space basis (star-tree frame)
    Cpinv = C.T @ np.linalg.inv(C @ C.T)            # Moore-Penrose pseudo-inverse
    return edges, eidx, C, Cpinv

def rep(p, edges, eidx, C, Cpinv):
    m = len(edges); P = np.zeros((m, m))
    for j, (a, b) in enumerate(edges):
        pa, pb = p[a], p[b]; e2 = (pa, pb) if pa < pb else (pb, pa); P[eidx[e2], j] = 1.0
    return C @ P @ Cpinv                            # T, already numeric

def phi_coeffs_prime(p):
    """Φ_p(x) coeffs for PRIME p (all 1, length p); φ(p)=p-1. No sympy."""
    return [1.0]*p, p-1

def phi_mult(perm, nv, p):
    """Φ_p multiplicity via numeric nullity — the price-is-right number, sympy-free."""
    edges, eidx, C, Cpinv = cyc_setup(nv)
    T = rep(perm, edges, eidx, C, Cpinv).astype(complex)
    coeffs, phi = phi_coeffs_prime(p)
    d = len(coeffs)-1
    powers = [np.eye(T.shape[0], dtype=complex)]
    for _ in range(d): powers.append(powers[-1] @ T)
    M = sum(coeffs[i]*powers[d-i] for i in range(d+1))
    nullity = M.shape[0] - np.linalg.matrix_rank(M, tol=1e-6)
    return nullity//phi if phi else nullity
