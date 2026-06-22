#!/usr/bin/env python3
"""cpu_load — the shared CPU matmul-throughput workload for the el-atlas measurement probes.

A spin: multiply x·y ``iters`` times and return one element (the read defeats dead-code elimination).
Folded from the byte-identical inner ``work`` of engine_validate / power_arms /
branch-independence-nedge-pilot (Π11). A SHARED workload is the more rigorous choice for measurement:
the three throughput probes now provably exercise the identical load, so their FLOP/s numbers stay
comparable — the prior inline copies could silently drift apart (the "a probe should show its load"
rationale is met by this one documented, named primitive)."""
import numpy as np


def matmul_spin(xy, iters):
    x, y = xy
    for _ in range(iters):
        z = np.dot(x, y)
    return float(z[0, 0])
