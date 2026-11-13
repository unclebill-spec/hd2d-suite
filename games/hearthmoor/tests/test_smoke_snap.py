"""pure-python self-test that run()'s worktree SNAP dict is not shadowed by the seal JS snapshot.

No browser. python3 tests/test_smoke_snap.py
"""
import ast
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import smoke  # noqa: E402
from smoke import SEAL_SNAP  # noqa: E402


# (a) the seal snapshot lives at module level as a JS IIFE string, not under the name SNAP.
assert isinstance(SEAL_SNAP, str)
assert SEAL_SNAP.strip().startswith("(() =>")
assert "window.__hm.S" in SEAL_SNAP and "bag:" in SEAL_SNAP and "gold:" in SEAL_SNAP and "shard:" in SEAL_SNAP
assert "rift_shard" in SEAL_SNAP

# (b) evaluating that string the way T.ev receives it must not replace a snapshot_tracked-style dict.
SNAP = {Path("/tmp/x"): b"data"}
ns = {"SNAP": SNAP, "SEAL_SNAP": SEAL_SNAP}
code = compile("pre = SEAL_SNAP\n", "<seal-snap>", "exec")
exec(code, ns)  # noqa: S102  harness self-test, no untrusted input
assert isinstance(ns["SNAP"], dict)
assert list(ns["SNAP"].items()) == [(Path("/tmp/x"), b"data")]
assert ns["pre"] is SEAL_SNAP
assert ns["SNAP"] is SNAP

# (c) inside run(), SNAP is only the worktree dict. The JS snapshot string is not assigned to it.
src = Path(smoke.__file__).read_text()
tree = ast.parse(src)
run_fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run")
snap_vals = []


class _SnapAssigns(ast.NodeVisitor):
    def visit_Assign(self, node):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "SNAP":
                snap_vals.append(node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        if isinstance(node.target, ast.Name) and node.target.id == "SNAP" and node.value is not None:
            snap_vals.append(node.value)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name) and node.target.id == "SNAP":
            snap_vals.append(node.value)
        self.generic_visit(node)

    def visit_NamedExpr(self, node):
        if isinstance(node.target, ast.Name) and node.target.id == "SNAP":
            snap_vals.append(node.value)
        self.generic_visit(node)


_SnapAssigns().visit(run_fn)
assert len(snap_vals) == 1, [ast.dump(v) for v in snap_vals]
val = snap_vals[0]
assert isinstance(val, ast.Call)
assert isinstance(val.func, ast.Name) and val.func.id == "snapshot_tracked"
assert not any(isinstance(n, ast.Constant) and isinstance(n.value, str) for n in ast.walk(val))
assert not any(isinstance(n, ast.Name) and n.id == "SEAL_SNAP" for n in ast.walk(val))
run_src = ast.get_source_segment(src, run_fn)
assert run_src is not None
assert "T.ev(SEAL_SNAP)" in run_src
assert 'SNAP = "' not in run_src and "SNAP = '" not in run_src
assert "SNAP = SEAL_SNAP" not in run_src

print("SNAP unshadowed self-test: 3 cases ok")
