#!/usr/bin/env python3
"""reuse_tui.py — a Textual TUI over the interned SPPF (the whole agglomerated structural space).

Every canonical node with fanin ≥ 2 is duplicated structure = a consolidation opportunity (N instances
of one pattern → parameterize; fanin = instances = the win). Left: a DataTable of shared subtrees ranked
by impact (fanin × size). Right: the selected subtree's instances as a MODULE TREE (navigate to the
canonical home) + what it ⊃ contains. Filter by head; sort by impact/size/fanin/rung.

  scripts/reuse_tui.py --build     # intern the forest (~90s) → cache (do once)
  scripts/reuse_tui.py             # load cache, launch the browser
"""
import sys, os, json, argparse, glob

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGDA = os.path.join(REPO, "agda")
CACHE = os.path.join(REPO, "scratch", "generated", "sppf_index.json")

# --------------------------------------------------------------------------- build (interner)
def build(cache_path, min_size, min_fanin, cap):
    sys.path.insert(0, os.path.join(REPO, "jea", "metalanguage"))
    import jea_pysim as J, typeholer_path as tp
    cores = sorted(glob.glob(os.path.join(AGDA, "_build", "**", "agda", "Substrate", "**", "*.agdai"),
                             recursive=True))
    print(f"interning {len(cores)} cores …", flush=True)
    C = J.Corpus()
    for c in cores:
        try: C.add_agdai(c)
        except Exception: pass
    print(f"{len(C.units)} units; extracting shared subtrees (size≥{min_size}, fanin≥{min_fanin}) …", flush=True)
    cands = tp.extract_cands(C, min_fanin=min_fanin, min_size=min_size)
    cands.sort(key=lambda c: -(c.units * c.size))
    keep = cands[:cap]
    print(f"{len(cands)} candidates; containment tower on the top {len(keep)} …", flush=True)
    direct, rung, _ = tp.containment_dag(keep)
    by_nid = {c.nid: c for c in keep}
    rows = []
    for c in keep:
        insts = sorted({C.units[i].name for i in c.unit_ids})
        contains = sorted({tp._head_str(by_nid[b].head) for b in direct.get(c.nid, []) if b in by_nid})
        rows.append({"fanin": c.units, "size": c.size, "head": tp._head_str(c.head),
                     "rung": rung.get(c.nid, 0), "contains": contains, "instances": insts})
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    json.dump({"rows": rows, "units": len(C.units), "cores": len(cores), "n_candidates": len(cands)},
              open(cache_path, "w"))
    print(f"✓ cached {len(rows)} shared subtrees → {cache_path}")

# --------------------------------------------------------------------------- Textual app
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import DataTable, Tree, Input, Header, Footer
from textual.binding import Binding

SORTS = ["impact", "size", "fanin", "rung"]
def _keyfn(k):
    if k == "impact": return lambda r: -(r["fanin"] * r["size"])
    return lambda r: -r[k]

class SPPF(App):
    CSS = """
    #table { width: 58%; }
    #detail { width: 42%; border-left: solid $accent; }
    Input { dock: top; }
    """
    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("s", "sort", "sort"),
        Binding("slash", "focus_filter", "filter"),
        Binding("escape", "unfocus_filter", "unfilter"),
    ]

    def __init__(self, rows, meta):
        super().__init__()
        self.allrows = rows
        self.meta = meta
        self.sort_key = "impact"
        self.filt = ""
        self.view = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Input(placeholder="filter by head substring …  (/ to focus, Esc to leave)", id="filter")
        with Horizontal():
            yield DataTable(id="table", cursor_type="row", zebra_stripes=True)
            yield Tree("select a subtree", id="detail")
        yield Footer()

    def on_mount(self):
        t = self.query_one("#table", DataTable)
        t.add_column("impact", width=7)
        t.add_column("×", width=6)
        t.add_column("size", width=5)
        t.add_column("rung", width=4)
        t.add_column("head")
        self.refresh_table()
        t.focus()

    def refresh_table(self):
        t = self.query_one("#table", DataTable)
        t.clear()
        rows = [r for r in self.allrows if not self.filt or self.filt.lower() in r["head"].lower()]
        rows.sort(key=_keyfn(self.sort_key))
        self.view = rows
        for i, r in enumerate(rows):
            t.add_row(str(r["fanin"] * r["size"]), f"{r['fanin']}×", str(r["size"]),
                      str(r["rung"]), r["head"], key=str(i))
        self.sub_title = (f"{len(rows)}/{len(self.allrows)} subtrees · {self.meta['units']} units · "
                          f"sort:{self.sort_key} · filter:'{self.filt}'")
        if rows: self.show_detail(rows[0])

    def show_detail(self, r):
        tree = self.query_one("#detail", Tree)
        tree.reset(f"{r['head']}   [{r['fanin']} instances × size {r['size']} · rung {r['rung']}]")
        if r["contains"]:
            c = tree.root.add(f"⊃ contains ({len(r['contains'])})")
            for h in r["contains"]:
                c.add_leaf(h)
        ins = tree.root.add(f"instances ({r['fanin']}) — canonical = shallowest", expand=True)
        for name in sorted(r["instances"]):
            node = ins
            parts = name.split(".")
            for j, p in enumerate(parts):
                if j == len(parts) - 1:
                    node.add_leaf(p)
                else:
                    child = next((c for c in node.children if str(c.label) == p), None)
                    node = child if child is not None else node.add(p)
        tree.root.expand()

    def on_data_table_row_highlighted(self, event):
        if event.row_key is not None and event.row_key.value is not None:
            self.show_detail(self.view[int(event.row_key.value)])

    def on_input_changed(self, event):
        self.filt = event.value
        self.refresh_table()

    def action_sort(self):
        self.sort_key = SORTS[(SORTS.index(self.sort_key) + 1) % len(SORTS)]
        self.refresh_table()

    def action_focus_filter(self):
        self.query_one("#filter", Input).focus()

    def action_unfocus_filter(self):
        self.query_one("#table", DataTable).focus()

def run_tui(cache_path):
    data = json.load(open(cache_path))
    SPPF(data["rows"], data).run()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--cache", default=CACHE)
    ap.add_argument("--min-size", type=int, default=3)
    ap.add_argument("--min-fanin", type=int, default=2)
    ap.add_argument("--cap", type=int, default=8000)
    args = ap.parse_args()
    if args.build:
        build(args.cache, args.min_size, args.min_fanin, args.cap); return
    if not os.path.exists(args.cache):
        print(f"no cache at {args.cache} — run:  scripts/reuse_tui.py --build"); return
    run_tui(args.cache)

if __name__ == "__main__":
    main()
