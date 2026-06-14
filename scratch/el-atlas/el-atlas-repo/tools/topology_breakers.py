"""
topology_breakers.py — AUTO-ENUMERATE the conductance model's symmetry-breakers at RUNTIME, on
whatever machine you run it on. Nothing about this box is hardcoded: caches, core tiers, NUMA
nodes, power-budget tree, and GPUs are all DISCOVERED from the running system, and the breaker
registry is built from what is found. Run it on a different machine and it rediscovers that
machine's breakers (homogeneous cores -> no heterogeneity breaker; multi-NUMA -> per-node
controller breakers; 0/1/N GPUs -> the matching power+PCIe breakers; psys present -> a chassis
aggregate node; etc.).

A breaker is a named structural threshold where the conductance regime changes. survey(topo, test)
flags which fire for a proposed measurement and whether it confounds the intended conductance --
e.g. a compute-scaling test whose working set exceeds the DISCOVERED largest private cache spills
into a shared cache and stops being an independent-branch test.

Discovery, not assumption -- the key portability move:
  * caches: read shared_cpu_list per cache index -> private vs shared is DISCOVERED (e.g. Alder
    Lake E-cores share L2 per cluster; a Zen has different sharing; this reads the truth).
  * heterogeneity: group CPUs by cpuinfo_max_freq -> 1 tier = homogeneous, >1 = hybrid.
  * NUMA: enumerate nodes -> each is a memory-controller domain (contention is per node).
  * power: enumerate /sys/class/powercap (intel-rapl/amd, psys=chassis) -> the budget TREE.
  * GPUs: nvidia-smi -L + per-GPU power limits + iGPU presence.
"""
import os, glob, re, subprocess
os.environ.setdefault("CUDA_PATH", "/usr")
from host_probe import probe_host, _read, _parse_size


def _cpus_in(spec):                       # "0-5,8" -> 7
    n = 0
    for part in (spec or "").split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-"); n += int(b) - int(a) + 1
        elif part:
            n += 1
    return n


# ---------- DISCOVERY (everything read from the running system) ----------
def discover_caches():
    """Per cache index on a representative of EACH freq tier: level/type/size/sharing scope."""
    seen = {}
    for cpu in _tier_reps():
        for d in sorted(glob.glob(f"/sys/devices/system/cpu/cpu{cpu}/cache/index*")):
            lvl, typ = _read(d + "/level"), _read(d + "/type")
            shared = _cpus_in(_read(d + "/shared_cpu_list"))
            key = (int(lvl), typ)
            ent = dict(level=int(lvl), type=typ, bytes=_parse_size(_read(d + "/size")),
                       shared_by=shared, scope=("private" if shared <= 1 else f"shared/{shared}"))
            # keep the smallest-sharing instance per (level,type) seen across tiers
            if key not in seen or shared < seen[key]['shared_by']:
                seen[key] = ent
    return sorted(seen.values(), key=lambda c: (c['level'], c['type']))


def discover_cpu_tiers():
    """Group logical CPUs by max frequency -> tiers (hybrid if >1). Falls back to 1 tier."""
    tiers = {}
    for d in glob.glob("/sys/devices/system/cpu/cpu[0-9]*"):
        m = re.search(r"cpu(\d+)$", d)
        f = _read(d + "/cpufreq/cpuinfo_max_freq")
        if m and f:
            tiers.setdefault(int(f), []).append(int(m.group(1)))
    if not tiers:
        tiers = {0: list(range(os.cpu_count() or 1))}
    return tiers


def _tier_reps():
    return [sorted(cs)[0] for cs in discover_cpu_tiers().values()]


def discover_numa():
    nodes = []
    for d in sorted(glob.glob("/sys/devices/system/node/node[0-9]*")):
        nodes.append(dict(node=os.path.basename(d), cpus=_cpus_in(_read(d + "/cpulist"))))
    return nodes or [dict(node="node0", cpus=os.cpu_count() or 1)]


def discover_power():
    """The powercap budget tree: each domain's name + power limits (W). psys (if present) is the
    platform/chassis aggregate; package-N are CPU sockets; amd-* on AMD."""
    domains = []
    seen = set()
    for d in sorted(glob.glob("/sys/class/powercap/*")):
        name = _read(d + "/name")
        if not name or name in seen:          # dedup: multiple sysfs paths reach the same domain
            continue
        seen.add(name)
        limits = {}
        for c in (0, 1):
            pl, cn = _read(f"{d}/constraint_{c}_power_limit_uw"), _read(f"{d}/constraint_{c}_name")
            if pl and int(pl) > 0:
                limits[cn or f"PL{c}"] = int(pl) / 1e6
        domains.append(dict(name=name, limits=limits, depth=os.path.basename(d).count(":")))
    return domains


def discover_gpus():
    gpus = []
    try:
        out = subprocess.run(["nvidia-smi",
                              "--query-gpu=name,power.max_limit,enforced.power.limit,pcie.link.gen.max,pcie.link.width.max",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5)
        for line in out.stdout.strip().splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",")]
            num = lambda x: float(x) if x not in ("", "[N/A]") else None
            gpus.append(dict(name=parts[0], pmax=num(parts[1]), penf=num(parts[2]),
                             pcie_gen=parts[3], pcie_width=parts[4], kind="discrete"))
    except Exception:
        pass
    # integrated GPU presence (Intel/AMD) via DRM render nodes that aren't the nvidia ones
    for card in glob.glob("/sys/class/drm/card[0-9]"):
        vendor = _read(card + "/device/vendor")
        if vendor in ("0x8086", "0x1002"):        # Intel / AMD integrated
            gpus.append(dict(name=f"iGPU(vendor {vendor})", kind="integrated",
                             shares="CPU package power budget"))
            break
    return gpus


def discover():
    h = probe_host()
    tiers = discover_cpu_tiers()
    caches = discover_caches()
    private = [c for c in caches if c['scope'] == 'private' and c['type'] in ('Data', 'Unified')]
    return dict(host=h, tiers=tiers, n_tiers=len(tiers), caches=caches,
                largest_private=max((c['bytes'] for c in private), default=h['l1d']),
                numa=discover_numa(), power=discover_power(), gpus=discover_gpus())


# ---------- BREAKER REGISTRY (built FROM the discovery) ----------
def BREAKERS(topo):
    brk = []
    lp = topo['largest_private']
    # informational: which cache level a working set lands in (per discovered level, non-confounding)
    for c in topo['caches']:
        if c['type'] == 'Instruction':
            continue
        brk.append(dict(
            name=f"spill>L{c['level']}({c['scope']})", domain="capacity",
            thresh=f"{c['bytes']//1024}K",
            fires=lambda t, _b=c['bytes']: t.get('working_set', 0) > _b,
            regime=f"working set exceeds L{c['level']} ({c['scope']})",
            confounds=False))
    # THE confound: leaving the largest PRIVATE cache means residing in a SHARED level -> compute
    # branches stop being independent. Threshold is the DISCOVERED largest private data cache.
    brk.append(dict(
        name="exceeds-private-cache", domain="capacity", thresh=f"{lp//1024}K (largest private)",
        fires=lambda t: t.get('working_set', 0) > lp,
        regime="working set leaves private caches -> resides in a SHARED cache/DRAM (contention)",
        confounds=lambda t: t['intent'] == 'compute-private',
        fix=f"keep working set <= {lp//1024}K so each branch stays in its own private cache"))
    # heterogeneity breaker ONLY if >1 freq tier discovered
    if topo['n_tiers'] > 1:
        big = max(topo['tiers'].items(), key=lambda kv: (kv[0], len(kv[1])))
        nbig = len(big[1])
        brk.append(dict(name="core-heterogeneity", domain="compute",
                        thresh=f"{topo['n_tiers']} freq tiers; fastest tier has {nbig} cores",
                        fires=lambda t, _n=nbig: t.get('n_branches', 1) > _n,
                        regime="slower/weaker core tier joins -> per-branch rate drops",
                        confounds=True, fix=f"pin to the {nbig} fastest-tier cores"))
    # NUMA: per-node memory controller; cross-node distance breaker if >1 node
    if len(topo['numa']) > 1:
        brk.append(dict(name="NUMA-cross-node", domain="bandwidth",
                        thresh=f"{len(topo['numa'])} NUMA nodes",
                        fires=lambda t: t.get('cross_numa', False),
                        regime="remote-node memory traversal -> higher latency / lower BW",
                        confounds=True, fix="pin memory and threads to one NUMA node"))
    # memory-controller contention (always present; per node)
    brk.append(dict(name="mem-controller-contention", domain="bandwidth",
                    thresh=f"{len(topo['numa'])} controller(s)",
                    fires=lambda t: t['intent'] == 'memory-stream' and t.get('n_branches', 1) > 1,
                    regime="cores share the controller -> aggregate BW saturates (G_AND cap)",
                    confounds=False))   # intended regime for a memory-stream test
    # POWER TREE: budget nodes are the CPU package(s) and the chassis aggregate (psys). Sub-domains
    # (core/uncore/dram/mmio) are not separate budgets -> skipped. psys is emitted even with NO
    # exposed limit: its existence IS the CPU<->dGPU coupling point; the value needs measurement.
    for dom in topo['power']:
        nm = dom['name']
        is_chassis = (nm == 'psys')
        if not (nm.startswith('package') or is_chassis):
            continue
        if not dom['limits'] and not is_chassis:
            continue
        thr = "; ".join(f"{k} {v:.0f}W" for k, v in dom['limits'].items()) \
            or "limit not exposed (needs combined-load measurement)"
        brk.append(dict(
            name=f"power:{nm}", domain="POWER", thresh=thr,
            fires=(lambda t: t['intent'] == 'het-sum') if is_chassis
                  else (lambda t: t.get('n_branches', 1) > 1 or t['intent'] == 'het-sum'),
            regime=("CHASSIS aggregate (psys): caps CPU package + dGPU TOGETHER -> the het G_OR sum "
                    "is an UPPER bound" if is_chassis
                    else f"{nm} budget shared by its consumers (P/E cores + iGPU)"),
            confounds=is_chassis,
            fix=("measure combined CPU+GPU load power; cap het-sum by it" if is_chassis
                 else "run >2s past burst (PL1) for sustained (PL0)")))
    # GPUs: power cap + PCIe gate per discrete GPU; iGPU shares CPU package
    has_dgpu = any(g['kind'] == 'discrete' for g in topo['gpus'])
    for g in topo['gpus']:
        if g['kind'] == 'discrete' and g.get('penf') and g.get('pmax') and g['penf'] < g['pmax']:
            brk.append(dict(name=f"gpu-power-cap:{g['name'][:18]}", domain="POWER",
                            thresh=f"enforced {g['penf']:.0f}W of {g['pmax']:.0f}W",
                            fires=lambda t: t['intent'] in ('het-sum', 'gpu-compute'),
                            regime="GPU peak FLOP/s overstated: enforced cap < max -> below boost clock",
                            confounds=True, fix=f"derate GPU peak by ~{g['penf']/g['pmax']:.2f}"))
        if g['kind'] == 'discrete':
            brk.append(dict(name="PCIe-gate", domain="bandwidth",
                            thresh=f"gen{g.get('pcie_gen')} x{g.get('pcie_width')}",
                            fires=lambda t: t['intent'] == 'het-sum' and t.get('residence') == 'host',
                            regime="GPU branch fed over PCIe -> starved for host-streamed low-I work",
                            confounds=False))
    # chassis coupling ONLY if both a CPU package budget AND a dGPU exist, and no psys node already covers it
    has_psys = any(d['name'] == 'psys' for d in topo['power'])
    if has_dgpu and not has_psys:
        brk.append(dict(name="chassis-coupling(CPU-pkg<->dGPU)", domain="POWER",
                        thresh="no psys node exposed -> aggregate not directly queryable",
                        fires=lambda t: t['intent'] == 'het-sum',
                        regime="CPU package & dGPU share chassis cooling -> het G_OR sum is an UPPER bound",
                        confounds=True, fix="measure combined-load power; cap het-sum by the chassis envelope"))
    return brk


def survey(topo, test):
    fired = []
    for br in BREAKERS(topo):
        if br['fires'](test):
            cf = br['confounds']
            cf = cf(test) if callable(cf) else cf
            fired.append((br['name'], cf, br['regime'], br.get('fix', "")))
    return fired


def _show(title, fired):
    print(f"   {title}")
    for name, cf, regime, fix in fired or [("(none)", False, "no breakers fire -- clean", "")]:
        print(f"     [{'CONFOUND' if cf else 'expected':8s}] {name}: {regime}")
        if cf and fix:
            print(f"                fix: {fix}")


if __name__ == "__main__":
    topo = discover()
    h = topo['host']
    print(f"DISCOVERED TOPOLOGY (runtime, this machine): {h['model']}")
    print(f"  core tiers: {[(round(f/1e6,1), len(c)) for f, c in sorted(topo['tiers'].items(), reverse=True)]} "
          f"(GHz, #cores){'  [hybrid]' if topo['n_tiers']>1 else '  [homogeneous]'}")
    print(f"  caches: " + ", ".join(f"L{c['level']}{c['type'][0]}={c['bytes']//1024}K/{c['scope']}"
                                     for c in topo['caches']))
    print(f"  largest private data cache: {topo['largest_private']//1024}K  (the independent-branch limit)")
    print(f"  NUMA nodes: {len(topo['numa'])}")
    print(f"  power tree: " + " | ".join(
        f"{d['name']}(" + (",".join(f"{k}={v:.0f}W" for k, v in d['limits'].items()) or "limit n/a") + ")"
        for d in topo['power'] if d['limits'] or d['name'] == 'psys'))
    print(f"  GPUs: " + ("; ".join(f"{g['name']} [{g['kind']}"
            + (f", {g['penf']:.0f}/{g['pmax']:.0f}W" if g.get('penf') else "") + "]" for g in topo['gpus']) or "none"))
    brk = BREAKERS(topo)
    print(f"\nAUTO-ENUMERATED {len(brk)} BREAKERS:")
    for br in brk:
        print(f"  - {br['name']:34s} [{br['domain']:9s}] {br['thresh']}")

    print(f"\nAUTO-SURVEY of proposed measurements (confounds flagged from discovered structure):")
    _show("compute-private, working set > largest-private-cache:",
          survey(topo, dict(intent='compute-private', working_set=topo['largest_private'] * 4, n_branches=4)))
    _show("compute-private, working set <= largest-private-cache:",
          survey(topo, dict(intent='compute-private', working_set=topo['largest_private'] // 2, n_branches=2)))
    _show("het-sum, host-resident:", survey(topo, dict(intent='het-sum', residence='host')))

    # portability checks: discovery found real structure + survey logic is threshold-driven
    w_disc = topo['largest_private'] > 0 and len(topo['caches']) >= 2 and len(brk) >= 4
    w_spill = any(c == True for _, c, _, _ in survey(topo, dict(intent='compute-private',
                  working_set=topo['largest_private'] * 4, n_branches=2)))
    w_clean = not any(c for _, c, _, _ in survey(topo, dict(intent='compute-private',
                  working_set=topo['largest_private'] // 2, n_branches=1)))
    ok = w_disc and w_spill and w_clean
    print(f"\nTOPOLOGY BREAKERS: discovered-structure {w_disc}; auto-catches-spill {w_spill}; "
          f"clean-when-private {w_clean}")
    print(f"\n  {'PASS' if ok else 'FAIL'} — every breaker is AUTO-ENUMERATED from the running system; the")
    print(f"  spill threshold is the DISCOVERED largest private cache, the heterogeneity breaker appears")
    print(f"  only if >1 freq tier exists, NUMA/GPU/power breakers track what's actually present. Run this")
    print(f"  on another machine and it rediscovers that machine's breakers -- no hardcoded topology.")
